"""
This file defines the Interpreter class.
It's the main file. `from interpreter import interpreter` will import an instance of this class.
"""
import json
import os
import threading
import time
from datetime import datetime
from queue import Queue
from .computer.computer import Computer
from .default_system_message import default_system_message
from .respond import respond
from .utils.telemetry import send_telemetry
from .utils.truncate_output import truncate_output
from PyQt6.QtCore import QObject, pyqtSignal
import requests
import builtins
from .workspace import Workspace

class FileOperationTracker(QObject):
    file_operation = pyqtSignal(str, str, str)

    def open(self, file, mode='r', *args, **kwargs):
        f = builtins.open(file, mode, *args, **kwargs)
        if 'w' in mode or 'a' in mode:
            self.file_operation.emit('open', file, f'File opened in {mode} mode')
        return f

    def write(self, f, data):
        result = f.write(data)
        self.file_operation.emit('write', f.name, data)
        return result

class OpenInterpreter:
    """
    This class (one instance is called an `interpreter`) is the "grand central station" of this project.

    Its responsibilities are to:

    1. Given some user input, prompt the language model.
    2. Parse the language models responses, converting them into LMC Messages.
    3. Send code to the computer.
    4. Parse the computer's response (which will already be LMC Messages).
    5. Send the computer's response back to the language model.
    6. Handle file operations (create, modify, delete) within the local system.
    ...

    The above process should repeat—going back and forth between the language model and the computer— until:

    6. Decide when the process is finished based on the language model's response.
    """

    def __init__(
            self,
            messages=None,
            offline=False,
            auto_run=False,
            verbose=False,
            debug=False,
            max_output=2800,
            safe_mode="off",
            shrink_images=False,
            loop=False,
            loop_message="""Proceed. You CAN run code on my machine. If the entire task I asked for is done, say exactly 'The task is done.' If you need some specific information (like username or password) say EXACTLY 'Please provide more information.' If it's impossible, say 'The task is impossible.' (If I haven't provided a task, say exactly 'Let me know what you'd like to do next.') Otherwise keep going.""",
            loop_breakers=[
                "The task is done.",
                "The task is impossible.",
                "Let me know what you'd like to do next.",
                "Please provide more information.",
            ],
            disable_telemetry=os.getenv("DISABLE_TELEMETRY", "false").lower() == "true",
            in_terminal_interface=False,
            conversation_history=True,
            conversation_filename=None,
            os=False,
            speak_messages=False,
            llm=None,
            system_message=default_system_message,
            custom_instructions="",
            user_message_template="{content}",
            always_apply_user_message_template=False,
            code_output_template="Code output: {content}\n\nWhat does this output mean / what's next (if anything, or are we done)?",
            empty_code_output_template="The code above was executed on my machine. It produced no text output. what's next (if anything, or are we done)?",
            code_output_sender="user",
            computer=None,
            sync_computer=False,
            import_computer_api=False,
            skills_path=None,
            import_skills=False,
            multi_line=True,
            contribute_conversation=False,
            
            
    ):
        # State
        self.file_tracker = FileOperationTracker()
        self.setup_file_tracking()

        self.messages = [] if messages is None else messages
        self.responding = False
        self.last_messages_count = 0
        self.file_operation = self.file_tracker.file_operation
        # Settings
        self.offline = offline
        self.auto_run = auto_run
        self.verbose = verbose
        self.debug = debug
        self.max_output = max_output
        self.safe_mode = safe_mode
        self.shrink_images = shrink_images
        self.disable_telemetry = disable_telemetry
        self.in_terminal_interface = in_terminal_interface
        self.multi_line = multi_line
        self.contribute_conversation = contribute_conversation

        # Loop messages
        self.loop = loop
        self.loop_message = loop_message
        self.loop_breakers = loop_breakers

        # Conversation history
        self.conversation_history = conversation_history
        self.conversation_filename = conversation_filename

        # OS control mode related attributes
        self.os = os
        self.speak_messages = speak_messages

        # Computer
        self.computer = Computer(self) if computer is None else computer
        self.sync_computer = sync_computer
        self.computer.import_computer_api = import_computer_api

        # Skills
        if skills_path:
            self.computer.skills.path = skills_path

        self.computer.import_skills = import_skills

        # LLM
        self.llm = llm

        # These are LLM related
        self.system_message = system_message
        self.custom_instructions = custom_instructions
        self.user_message_template = user_message_template
        self.always_apply_user_message_template = always_apply_user_message_template
        self.code_output_template = code_output_template
        self.empty_code_output_template = empty_code_output_template
        self.code_output_sender = code_output_sender

    def setup_file_tracking(self):
        self.locals = {
            'open': self.file_tracker.open,
            'write': self.file_tracker.write
        }

    @property
    def anonymous_telemetry(self) -> bool:
        return not self.disable_telemetry and not self.offline

    @property
    def will_contribute(self):
        overrides = (
            self.offline or not self.conversation_history or self.disable_telemetry
        )
        return self.contribute_conversation and not overrides

    def wait(self):
        while self.responding:
            time.sleep(0.2)
        return self.messages[self.last_messages_count:]

    def chat(self, message=None, display=True, stream=False, blocking=True):
        try:
            self.responding = True
            if message:
                self._handle_message(message, display)
            else:
                self._handle_message(self._get_message(), display)

            if not blocking:
                chat_thread = threading.Thread(
                    target=self.chat, args=(message, display, stream, True)
                )  # True as in blocking = True
                chat_thread.start()
                return

            if stream:
                return self._streaming_chat(message=message, display=display)

            # If stream=False, *pull* from the stream.
            for _ in self._streaming_chat(message=message, display=display):
                pass

            # Return new messages
            self.responding = False
            return self.messages[self.last_messages_count:]

        except GeneratorExit:
            self.responding = False
            # It's fine
       
            raise

    def run_code(self, language, code):
        # Change working directory to workspace
        original_cwd = os.getcwd()
        os.chdir(self.workspace_path)

        try:
            # Run the code
            exec(code, self.locals)
            result = self.computer.run(language, code)
        finally:
            # Change back to original working directory
            os.chdir(original_cwd)

            return result

    def chat_stream(self, message=None):
        """
        A generator that yields chunks of the conversation.
        This is more suitable for GUI applications that need to update in real-time.
        """
        self.responding = True
        try:
            for chunk in self._streaming_chat(message=message, display=False):
                yield chunk

            self.responding = False
        except Exception as e:
            self.responding = False
            if self.anonymous_telemetry:
                message_type = type(message).__name__
                send_telemetry(
                    "errored",
                    properties={
                        "error": str(e),
                        "in_terminal_interface": self.in_terminal_interface,
                        "message_type": message_type,
                        "os_mode": self.os,
                    },
                )
            raise

    def chat_async(self, message=None, callback=None):
        """
        An asynchronous version of chat that uses a callback function.
        This is useful for GUI applications that need to update without blocking.
        """

        def chat_thread():
            try:
                for chunk in self.chat_stream(message):
                    if callback:
                        callback(chunk)
            except Exception as e:
                if callback:
                    callback({"type": "error", "content": str(e)})

        threading.Thread(target=chat_thread).start()

    def _handle_message(self, message):
        if not message:
            message = "No entry from user - please suggest something to enter."

        if isinstance(message, dict):
            if "role" not in message:
                message["role"] = "user"
            self.messages.append(message)
        elif isinstance(message, str):
            self.messages.append({"role": "user", "type": "message", "content": message})
        elif isinstance(message, list):
            self.messages = message

        self.last_messages_count = len(self.messages)
        return message

    def _save_conversation(self):
        if self.conversation_history and not self.conversation_filename:
            first_few_words = self._get_first_few_words()
            date = datetime.now().strftime("%B_%d_%Y_%H-%M-%S")
            self.conversation_filename = f"{first_few_words}__{date}.json"

        if self.conversation_history:
            if not os.path.exists(self.conversation_history_path):
                os.makedirs(self.conversation_history_path)
            with open(os.path.join(self.conversation_history_path, self.conversation_filename), "w") as f:
                json.dump(self.messages, f)

    def _get_first_few_words(self):
        content = self.messages[0]["content"][:25]
        words = content.split()
        if len(words) >= 2:
            first_few_words = "_".join(words[:-1])
        else:
            first_few_words = content[:15]
        return "".join(c for c in first_few_words if c not in '<>:"/\\|?*!')

    def chat(self, message=None, display=True, stream=False, blocking=True):
        try:
            self.responding = True
            message = self._handle_message(message)

            if not blocking:
                threading.Thread(target=self.chat, args=(message, display, stream, True)).start()
                return

            if stream:
                return self._streaming_chat(message=message, display=display)

            for _ in self._streaming_chat(message=message, display=display):
                pass

            self._save_conversation()
            self.responding = False
            return self.messages[self.last_messages_count:]

        except GeneratorExit:
            self.responding = False
            raise

    def get_conversation_history(self):
        """
        Returns the current conversation history.
        Useful for GUI applications to display the chat history.
        """
        return self.messages

    def get_system_info(self):
        """
        Returns system information.
        Useful for GUI applications to display system details.
        """
        return {
            "os": self.os,
            "offline": self.offline,
            "llm_model": self.llm.model,
            "safe_mode": self.safe_mode,
        }


    def _respond_and_store(self):
        """
        Pulls from the respond stream, adding delimiters. Some things, like active_line, console, confirmation... these act specially.
        Also assembles new messages and adds them to `self.messages`.
        """
        self.verbose = False

        # Utility function
        def is_active_line_chunk(chunk):
            return "format" in chunk and chunk["format"] == "active_line"

        last_flag_base = None

        try:
            for chunk in respond(self):
                # For async usage
                if hasattr(self, "stop_event") and self.stop_event.is_set():
                    break

                if chunk["content"] == "":
                    continue

                # Handle the special "confirmation" chunk, which neither triggers a flag or creates a message
                if chunk["type"] == "confirmation":
                    # Emit a end flag for the last message type, and reset last_flag_base
                    if last_flag_base:
                        yield {**last_flag_base, "end": True}
                        last_flag_base = None

                    if self.auto_run == False:
                        yield chunk

                    # We want to append this now, so even if content is never filled, we know that the execution didn't produce output.
                    # ... rethink this though.
                    self.messages.append(
                        {
                            "role": "computer",
                            "type": "console",
                            "format": "output",
                            "content": "",
                        }
                    )
                    continue

                # Check if the chunk's role, type, and format (if present) match the last_flag_base
                if (
                        last_flag_base
                        and "role" in chunk
                        and "type" in chunk
                        and last_flag_base["role"] == chunk["role"]
                        and last_flag_base["type"] == chunk["type"]
                        and (
                        "format" not in last_flag_base
                        or (
                                "format" in chunk
                                and chunk["format"] == last_flag_base["format"]
                        )
                )
                ):
                    # If they match, append the chunk's content to the current message's content
                    # (Except active_line, which shouldn't be stored)
                    if not is_active_line_chunk(chunk):
                        self.messages[-1]["content"] += chunk["content"]
                else:
                    # If they don't match, yield a end message for the last message type and a start message for the new one
                    if last_flag_base:
                        yield {**last_flag_base, "end": True}

                    last_flag_base = {"role": chunk["role"], "type": chunk["type"]}

                    # Don't add format to type: "console" flags, to accommodate active_line AND output formats
                    if "format" in chunk and chunk["type"] != "console":
                        last_flag_base["format"] = chunk["format"]

                    yield {**last_flag_base, "start": True}

                    # Add the chunk as a new message
                    if not is_active_line_chunk(chunk):
                        self.messages.append(chunk)

                # Yield the chunk itself
                yield chunk

                # Truncate output if it's console output
                if chunk["type"] == "console" and chunk["format"] == "output":
                    self.messages[-1]["content"] = truncate_output(
                        self.messages[-1]["content"],
                        self.max_output,
                        add_scrollbars=self.computer.import_computer_api,
                        # I consider scrollbars to be a computer API thing
                    )

            # Yield a final end flag
            if last_flag_base:
                yield {**last_flag_base, "end": True}
        except GeneratorExit:
            raise  # gotta pass this up!

    def reset(self):
        self.computer.terminate()  # Terminates all languages
        self.computer._has_imported_computer_api = False  # Flag reset
        self.messages = []
        self.last_messages_count = 0


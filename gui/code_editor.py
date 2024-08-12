from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import pyqtSignal
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerJavaScript, QsciLexerHTML, QsciLexerBash

class CodeEditor(QWidget):
    analysis_complete = pyqtSignal(str)
    content_changed = pyqtSignal(dict)

    def __init__(self, interpreter, chat_widget):
        super().__init__()
        self.interpreter = interpreter
        self.chat_widget = chat_widget
        self.current_file = None
        
        layout = QVBoxLayout()

        # Language selector and buttons
        controls_layout = QHBoxLayout()
        
        self.language_selector = QComboBox()
        self.language_selector.addItems(["python", "javascript", "html", "shell"])
        self.language_selector.currentTextChanged.connect(self.change_language)
        controls_layout.addWidget(self.language_selector)

        self.run_button = QPushButton("Run Code")
        self.run_button.clicked.connect(self.run_code)
        controls_layout.addWidget(self.run_button)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file)
        controls_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)
        controls_layout.addWidget(self.save_button)

        self.save_as_button = QPushButton("Save As")
        self.save_as_button.clicked.connect(self.save_file_as)
        controls_layout.addWidget(self.save_as_button)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze_content)
        controls_layout.addWidget(self.analyze_button)

        self.upload_media_button = QPushButton("Upload Media")
        self.upload_media_button.clicked.connect(self.upload_media)
        controls_layout.addWidget(self.upload_media_button)

        layout.addLayout(controls_layout)

        # Code editor
        self.editor = QsciScintilla()
        self.editor.setUtf8(True)
        self.editor.setFont(QFont('Courier', 10))
        self.editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.editor.setMarginWidth(0, "000")
        self.editor.setMarginsForegroundColor(QColor("#ff888888"))
        self.editor.textChanged.connect(self.on_content_changed)

        # Set up Python lexer by default
        self.set_lexer("python")

        layout.addWidget(self.editor)

        self.setLayout(layout)

    def set_lexer(self, language):
        if language == "python":
            lexer = QsciLexerPython()
        elif language == "javascript":
            lexer = QsciLexerJavaScript()
        elif language == "html":
            lexer = QsciLexerHTML()
        elif language == "shell":
            lexer = QsciLexerBash()
        else:
            lexer = None

        self.editor.setLexer(lexer)
   
    def change_language(self, language):
        self.set_lexer(language)
        self.on_content_changed()

    def run_code(self):
        code = self.editor.text()
        language = self.language_selector.currentText()
        result = self.interpreter.run_code(language, code)

        if isinstance(result, list):
            for item in result:
                if item['type'] == 'console':
                    self.chat_widget.append_console_output(item.get('content', ''))
                elif item['type'] == 'code':
                    self.chat_widget.append_code(item.get('content', ''), language)
                else:
                    self.chat_widget.append_message('AI', item.get('content', ''))
        else:
            self.chat_widget.append_message('AI', "Code execution complete.")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as f:
                f.write(self.editor.text())
            self.chat_widget.append_message('System', f"File saved: {self.current_file}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.editor.text())
            self.current_file = file_path
            self.chat_widget.append_message('System', f"File saved as: {file_path}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if file_path:
            with open(file_path, 'r') as f:
                file_content = f.read()
            self.editor.setText(file_content)
            self.current_file = file_path
            self.chat_widget.append_message('System', f"File opened: {file_path}")
            
            # Determine the language based on file extension
            extension = file_path.split('.')[-1].lower()
            if extension == 'py':
                self.language_selector.setCurrentText("python")
            elif extension == 'js':
                self.language_selector.setCurrentText("javascript")
            elif extension == 'html':
                self.language_selector.setCurrentText("html")
            else:
                self.language_selector.setCurrentText("shell")
            
            self.on_content_changed()

    def get_current_content(self):
        return {
            'content': self.editor.text(),
            'language': self.language_selector.currentText(),
            'file_path': self.current_file
        }

    def on_content_changed(self):
        self.content_changed.emit(self.get_current_content())

    def analyze_content(self):
        content_info = self.get_current_content()
        self.analysis_complete.emit(content_info['content'])

    def upload_media(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Media File", "", "Media Files (*.png *.jpg *.jpeg *.gif *.bmp *.mp3 *.wav *.mp4 *.avi *.mov)")
        if file_path:
            self.chat_widget.handle_media_upload(file_path)

from ..base_language import BaseLanguage

class HTML(BaseLanguage):
    file_extension = "html"
    name = "HTML"

    def __init__(self):
        super().__init__()

    def run(self, code):
        # Both assistant and user see the HTML code
        yield {
            "type": "code",
            "format": "html",
            "content": code,
            "recipient": "both"
        }

        # Inform that HTML is being displayed
        yield {
            "type": "console",
            "format": "output",
            "content": "HTML code is ready to be displayed.",
            "recipient": "both"
        }

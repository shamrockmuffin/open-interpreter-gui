import base64
from io import BytesIO
from PIL import Image
from weasyprint import HTML

def html_to_png_base64(html_content):
    # Convert HTML to PNG
    png_image = HTML(string=html_content).write_png()

    # Convert PNG to base64
    buffered = BytesIO()
    Image.open(BytesIO(png_image)).save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str

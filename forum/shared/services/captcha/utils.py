import random
import string

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def captcha_text(length=5):
    char = string.ascii_letters + string.digits
    return "".join(random.choices(char, k=length))

def captcha_image(text):
    image = Image.new('RGB', (120, 40), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    draw.text((10, 5), text, font=font, fill=(0, 0, 0))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
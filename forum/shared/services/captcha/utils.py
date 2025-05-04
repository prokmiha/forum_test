import random
import string

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def captcha_text(length=5):
    char = string.ascii_letters + string.digits
    return "".join(random.choices(char, k=length))

def captcha_image(text):
    width, height = 160, 60  # увеличим размер для удобства
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Вычислить размер текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Центрировать
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Тень
    draw.text((x+1, y+1), text, font=font, fill=(180, 180, 180))

    # Основной текст
    draw.text((x, y), text, font=font, fill=(10, 10, 10))

    # Вернуть как bytes
    output = BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    return output.getvalue()

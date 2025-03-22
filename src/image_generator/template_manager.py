from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_base_template():
    # Default Instagram portrait dimensions
    img = Image.new('RGB', (1080, 1350), color=(23, 32, 42))
    return img

def add_text_to_image(img, text, position, font_size=40, color=(255, 255, 255)):
    draw = ImageDraw.Draw(img)
    font_path = os.path.join(BASE_DIR, '../../assets/fonts/Roboto-Regular.ttf')
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    return img
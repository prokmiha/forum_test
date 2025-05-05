import re
import bleach
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

ALLOWED_TAGS = ['a', 'code', 'strong', 'i']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'target', 'rel']
}

def clean_html(text: str) -> str:
    cleaned = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    if not cleaned.strip():
        raise ValueError("Текст комментария не может быть пустым")
    return cleaned

def validate_user_name(name: str):
    if not name or len(name.strip()) < 3:
        raise ValueError("Имя должно содержать минимум 3 символа.")

    if not re.match(r'^[A-Za-zА-Яа-я0-9\s]+$', name.strip()):
        raise ValueError("Имя может содержать только латиницу, кириллицу и цифры.")

def validate_email_address(email: str):
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("Введите корректный email.")

def sanitize_comment_data(data: dict) -> dict:
    validate_user_name(data.get("user_name", ""))

    if email := data.get("email"):
        validate_email_address(email)

    if text := data.get("text"):
        data["text"] = clean_html(text)

    return data 
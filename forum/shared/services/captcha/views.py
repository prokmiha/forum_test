from django.http import HttpResponse
from .utils import captcha_text, captcha_image

def captcha_view(request):
    text = captcha_text()
    image = captcha_image(text)

    request.session["captcha_text"] = text

    return HttpResponse(image, content_type="image/png")
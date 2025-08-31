from django.http import HttpRequest

from general import default_render


def get_error_msg(status_code: int):
    match status_code:
        case 400 | 405:
            return "The request sent by your client seems to be malformed."
        case 401:
            return "You are not authenticated as required by this resource."
        case 403:
            return "You are forbidden from accessing this resource."
        case 404:
            return "The requested resource was not found."
        case 418:
            return "I'm a teapot."
        case _ if 500 <= status_code < 600:
            return "There was an internal server error."
        case _:
            return "I have programmed no extra error message here."


def error_page(request: HttpRequest, status_code: int):
    return default_render(request, f"special/error_page.html", {
        "title": f"Error: {status_code}",
        "status": status_code,
        "error_msg": get_error_msg(status_code),
    })

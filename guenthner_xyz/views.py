from general import default_render


def error_page(error_code: str):
    return lambda request: default_render(request, f"special/{error_code}.html", {
        "title": f"{error_code} Page",
        "status": error_code,
    })

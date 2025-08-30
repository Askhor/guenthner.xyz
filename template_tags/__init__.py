import os

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def load_js(context: dict, path: str, load_async=False) -> str:
    request = context["request"]
    return format_html(
        f'<script src="https://{request.get_host()}/js/{path}.js" {"async" if load_async else ""}></script>')


@register.simple_tag(takes_context=True)
def load_css(context: dict, path: str) -> str:
    request = context["request"]
    return format_html(f'<link rel="stylesheet" href="https://{request.get_host()}/css/{path}.css">')


@register.filter
@stringfilter
def add_description(desc: str):
    return format_html(f'<meta name="description" content="{desc}">')


@register.filter
@stringfilter
def strip_file_extension(path: str):
    return os.path.splitext(path)[0]

import base64
import os

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def load_js(context: dict, path: str, extra_args="") -> str:
    return format_html(
        f'<script src="{context["schost"]}/js/{path}.js" {extra_args}></script>')


@register.simple_tag(takes_context=True)
def load_css(context: dict, path: str) -> str:
    return format_html(f'<link rel="stylesheet" href="{context["schost"]}/css/{path}.css">')


@register.filter
@stringfilter
def add_description(desc: str):
    return format_html(f'<meta name="description" content="{desc}">')


@register.filter
@stringfilter
def strip_file_extension(path: str):
    return os.path.splitext(path)[0]


@register.filter
@stringfilter
def base64e(value: str):
    return base64.urlsafe_b64encode(str(value).encode()).decode()


@register.filter
@stringfilter
def base64d(value: str):
    return base64.urlsafe_b64decode(str(value).encode()).decode()

import base64
import os

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_block_tag(takes_context=True)
def define(context: dict, content, name):
    context[f"template_{name}"] = content
    return content


@register.simple_tag(takes_context=True)
def use(context: dict, name):
    return context[f"template_{name}"]


@register.simple_tag(takes_context=True)
def load_js(context: dict, path: str, extra_args="") -> str:
    return mark_safe(
        f'<script src="{context["schost"]}/js/{path}.js" {extra_args}></script>')


@register.simple_tag(takes_context=True)
def load_css(context: dict, path: str) -> str:
    return mark_safe(f'<link rel="stylesheet" href="{context["schost"]}/css/{path}.css">')


@register.simple_tag
def load_alpine():
    return mark_safe("""<script src="//unpkg.com/alpinejs" defer></script>
                        <style>[x-cloak] { display: none !important; }</style>""")


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

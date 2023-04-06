from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def responsive_image(image_url, alt_text='', class_name=''):
    """
    Returns a responsive image with a specified URL, alt text, and CSS class name.
    """
    return format_html(
        '<img src="{}" alt="{}" class="{}" loading="lazy" decoding="async" />',
        image_url, alt_text, class_name
    )

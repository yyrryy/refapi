from django import template
import re

register = template.Library()

@register.filter
def extract_brand(value):
    match = re.search(r'brand:(\d+)', value)
    return match.group(1) if match else 'Brand not found'

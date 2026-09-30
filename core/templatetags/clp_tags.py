# core/templatetags/clp_tags.py
from django import template

register = template.Library()

@register.filter(name='clp')
def clp_format(value):
    """Convierte un número a formato de moneda chilena (ej: 85.000)"""
    try:
        val = int(float(value))
        return f"{val:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica precio por cantidad y lo formatea en CLP"""
    try:
        val = float(value) * float(arg)
        val_int = int(val)
        return f"{val_int:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return ''
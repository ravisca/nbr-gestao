from django import template

register = template.Library()

@register.filter
def numero_natural(value):
    """
    Formata um número para exibir decimais apenas se for maior que zero.
    Por exemplo: 10.00 -> 10 | 10.50 -> 10,50
    """
    try:
        float_val = float(value)
        if float_val.is_integer():
            return str(int(float_val))
        else:
            # Retorna com vírgula para manter padrão PT-BR caso haja decimais
            return f"{float_val:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return value

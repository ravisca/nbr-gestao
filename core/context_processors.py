from django.templatetags.static import static


def site_config(request):
    """Injeta a configuração do site em todos os templates."""
    from .models import ConfiguracaoSite

    try:
        config = ConfiguracaoSite.load()
        logo_site_url = config.logo_site.url if config.logo_site else static('img/logo.png')
        logo_relatorio_url = config.logo_relatorio.url if config.logo_relatorio else static('img/logo.png')
        favicon_url = config.favicon.url if config.favicon else static('img/favicon.png')
        nome_sistema = config.nome_sistema
    except Exception:
        logo_site_url = static('img/logo.png')
        logo_relatorio_url = static('img/logo.png')
        favicon_url = static('img/favicon.png')
        nome_sistema = 'SIGEP'

    return {
        'site_logo': logo_site_url,
        'site_logo_relatorio': logo_relatorio_url,
        'site_favicon': favicon_url,
        'site_nome': nome_sistema,
    }

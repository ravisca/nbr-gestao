from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

import os
from django.conf import settings
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    sUrl = settings.STATIC_URL        # Typically /static/
    mUrl = settings.MEDIA_URL         # Typically /media/
    mRoot = settings.MEDIA_ROOT       # Typically /home/user/var/www/media/
    sRoot = settings.STATIC_ROOT      # Typically /home/user/var/www/static/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl) or (not sUrl.startswith('/') and uri.startswith(f"/{sUrl}")):
        # Strip the STATIC_URL prefix to get the relative path
        # Handle case where sUrl is 'static/' but uri is '/static/img/...'
        if uri.startswith(sUrl):
            relative_path = uri.replace(sUrl, "", 1)
        else:
            relative_path = uri.replace(f"/{sUrl}", "", 1)
        
        # First try to find it using staticfiles finders (dev)
        path = finders.find(relative_path)
        
        # If not found (or in production where finders might not work same way), try STATIC_ROOT
        if not path:
            path = os.path.join(sRoot, relative_path)
    else:
        # If it doesn't start with static/media url, it might be a relative path already via finders
        path = finders.find(uri)
        if not path:
             return uri

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    
    result = BytesIO()
    
    # Force UTF-8 encoding
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return HttpResponse(f"Erro ao gerar PDF: {pdf.err}", status=400)

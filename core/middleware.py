
import logging
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            logger.info(f"[RoleMiddleware] User: {request.user.username}, Path: {request.path}")
            logger.info(f"[RoleMiddleware] Groups: {list(request.user.groups.values_list('name', flat=True))}")
            logger.info(f"[RoleMiddleware] is_staff: {request.user.is_staff}, is_superuser: {request.user.is_superuser}")
            
            # Always allow superusers and 'Gestão' group to bypass role restrictions
            if request.user.is_superuser or request.user.groups.filter(name='Gestão').exists():
                logger.info(f"[RoleMiddleware] User {request.user.username} is Gestão/superuser - bypassing")
                return self.get_response(request)

            path = request.path
            
            # Check for Operacional group
            if request.user.groups.filter(name='Operacional').exists():
                logger.info(f"[RoleMiddleware] User {request.user.username} is Operacional")
                allowed_prefixes = [
                    '/estoque/',
                    '/beneficiarios/',
                    '/atividades/projetos/', # Permite visualizar projetos (editar é bloqueado na view)
                    '/static/',
                    '/media/',
                    '/accounts/login/',
                    '/accounts/logout/',
                    '/admin/logout/',
                ]
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                if path == '/' or path == '/home/':
                    is_allowed = True
                    
                if not is_allowed:
                    logger.info(f"[RoleMiddleware] Redirecting {request.user.username} to estoque_list")
                    return redirect('estoque_list')

            # Check for Núcleo group (antigo Professor)
            elif request.user.groups.filter(name='Núcleo').exists():
                logger.info(f"[RoleMiddleware] User {request.user.username} is Núcleo")
                allowed_prefixes = [
                    '/atividades/registrar/',
                    '/atividades/sucesso/',
                    '/atividades/ajax/',
                    '/static/',
                    '/media/',
                    '/accounts/login/',
                    '/accounts/logout/',
                    '/admin/logout/',
                ]
                
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                logger.info(f"[RoleMiddleware] Path '{path}' allowed: {is_allowed}")
                
                if not is_allowed:
                    # Redirect to Activity Registration (página principal do Núcleo)
                    try:
                        target_url = reverse('registrar_atividade_mobile')
                    except:
                        target_url = '/atividades/registrar/'
                        
                    if path != target_url:
                        logger.info(f"[RoleMiddleware] Redirecting {request.user.username} to {target_url}")
                        return redirect(target_url)
        
        response = self.get_response(request)
        return response

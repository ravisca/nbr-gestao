
from django.shortcuts import redirect
from django.urls import reverse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            
            # Check for Operacional group
            if request.user.groups.filter(name='Operacional').exists():
                allowed_prefixes = [
                    '/estoque/',
                    '/beneficiarios/',
                    '/atividades/projetos/', # Permite visualizar projetos (editar é bloqueado na view)
                    '/static/', 
                    '/media/',
                    '/accounts/logout/',
                    '/admin/logout/',
                ]
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                if path == '/' or path == '/home/':
                    is_allowed = True
                    
                if not is_allowed:
                    return redirect('estoque_list')

            # Check for Núcleo group (antigo Professor)
            elif request.user.groups.filter(name='Núcleo').exists():
                allowed_prefixes = [
                    '/atividades/',
                    '/static/', 
                    '/media/',
                    '/accounts/logout/',
                    '/admin/logout/', 
                ]
                
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                
                if not is_allowed:
                    # Redirect to Atividades Dashboard (Project List)
                    try:
                        target_url = reverse('projeto_list')
                    except:
                        target_url = '/atividades/projetos/'
                        
                    if path != target_url:
                        return redirect(target_url)
        
        response = self.get_response(request)
        return response

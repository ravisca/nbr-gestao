
from django.shortcuts import redirect
from django.urls import reverse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check for Professor group
            if request.user.groups.filter(name='Professor').exists():
                path = request.path
                # Allowed paths
                allowed_prefixes = [
                    '/atividades/',
                    '/static/', 
                    '/media/',
                    '/accounts/logout/',
                    '/admin/logout/', # Ensure they can logout
                ]
                
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                
                if not is_allowed:
                    # Redirect to Atividades Dashboard (Project List)
                    # Use reverse to be safe, but hardcoded for middleware simplicity often works if lazy
                    # better to resolve 'projeto_list'
                    try:
                        target_url = reverse('projeto_list')
                    except:
                        target_url = '/atividades/projetos/'
                        
                    if path == target_url:
                        pass # Already there
                    else:
                        return redirect(target_url)
        
        response = self.get_response(request)
        return response

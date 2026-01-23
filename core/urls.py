"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
from .views import HomeView
=======
from .views import HomeView, UsuarioListView, UsuarioCreateView
>>>>>>> a014260e5a3fa23c4620002e99e70b890e84ffb1
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # URLs de Autenticação (Login, Logout, Password Reset)
    path('', HomeView.as_view(), name='home'),
    path('atividades/', include('atividades.urls')),
    path('beneficiarios/', include('beneficiarios.urls')),
    path('estoque/', include('estoque.urls')),
    path('financeiro/', include('financeiro.urls')),
<<<<<<< HEAD
=======
    
    # Gestão de Usuários
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/criar/', UsuarioCreateView.as_view(), name='usuario_create'),
>>>>>>> a014260e5a3fa23c4620002e99e70b890e84ffb1
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
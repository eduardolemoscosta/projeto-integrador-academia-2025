from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UsuarioCreate, PerfilUpdate, PerfilList, PerfilDetailView
from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html'
    ), name='login'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'), #alterar senha
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'), #email enviado
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('registrar/', UsuarioCreate.as_view(), name='registrar'),
    path('signup/', UsuarioCreate.as_view(), name='signup'),
    path('atualizar-dados/', PerfilUpdate.as_view(), name='atualizar-dados'),
    path('listar/usersauth/', PerfilList.as_view(), name='listar-usersauth'),
    path('detalhes-usuario/<int:pk>/', PerfilDetailView.as_view(), name='detalhes-usuario'),

    path('calcular-imc/', views.calcular_imc, name='calcular_imc'),
    path('progresso-imc/', views.progresso_imc, name='progresso_imc'),
    path('apagar-imc/<int:imc_id>/', views.apagar_imc, name='apagar_imc'),
    path('adicionar-problema/', views.adicionar_problema_medico, name='adicionar_problema'),

]


from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.contrib.auth.models import User, Group
from .forms import UsuarioForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Perfil
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import IMCRegistro
from .forms import IMCForm

from django.contrib.auth.decorators import login_required


class UsuarioCreate(CreateView):
    template_name = "cadastros/form_add_user.html"
    form_class = UsuarioForm
    success_url = reverse_lazy('inicio')

    def form_valid(self, form):
        
        grupo, _ = Group.objects.get_or_create(name="Docente") #ou Discentes

        url = super().form_valid(form)

        self.object.groups.add(grupo)
        
        Perfil.objects.get_or_create(usuario=self.object)

        return url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Registro de novo usuário"
        context['botao'] = "Cadastrar"
        return context


class PerfilList(ListView):
    login_url = reverse_lazy('login')  
    model = Perfil
    template_name = 'cadastros/listas/userauth.html'
    paginate_by = 3

    def get_queryset(self):
        # Se o usuário é staff, ele pode ver todos os perfis
        if self.request.user.is_staff:
            queryset = Perfil.objects.all()
        else:
            # Usuário comum só pode ver o próprio perfil
            queryset = Perfil.objects.filter(usuario=self.request.user)
        
        # Aplicar o filtro de nome_completo, se existir
        txt_nome = self.request.GET.get('nome_completo')
        if txt_nome:
            queryset = queryset.filter(nome_completo__icontains=txt_nome)  # Ajuste aqui
        
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Lista de Usuários"
        return context



class PerfilUpdate(UpdateView):
    template_name = "cadastros/form_perfil.html"
    model = Perfil
    fields = ['nome_completo', 'email', 'matricula']
    success_url = reverse_lazy("inicio")

    def get_object(self, queryset=None):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Meus dados"
        context['botao'] = "Atualizar"
        return context
    

def custom_logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def calcular_imc(request):
    if request.method == 'POST':
        form = IMCForm(request.POST)
        if form.is_valid():
            imc_registro = form.save(commit=False)
            imc_registro.user = request.user
            imc_registro.save()
            return redirect('progresso_imc')
    else:
        form = IMCForm()
    
    # Get the last 10 IMC calculations for the user
    historico = IMCRegistro.objects.filter(user=request.user).order_by('-data_registro')[:10]
    
    return render(request, 'calcular_imc.html', {'form': form, 'historico': historico})

@login_required
def progresso_imc(request):
    registros = IMCRegistro.objects.filter(user=request.user).order_by('-data_registro')
    return render(request, 'progresso_imc.html', {'registros': registros})

def apagar_imc(request, imc_id):
    
    imc_registro = get_object_or_404(IMCRegistro, id=imc_id, user=request.user) 
    
    imc_registro.delete()
    
    return redirect('progresso_imc')


class PerfilDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('login')
    model = Perfil
    template_name = 'cadastros/detalhes_usuario.html'
    context_object_name = 'perfil'

    def get_object(self, queryset=None):
        perfil = get_object_or_404(Perfil, pk=self.kwargs['pk'])
        
        # Only staff can view other users' profiles, regular users can only view their own
        if not self.request.user.is_staff and perfil.usuario != self.request.user:
            raise PermissionDenied("Você não tem permissão para visualizar este perfil.")
        
        return perfil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil = self.get_object()
        
        # Get IMC history for this user
        imc_history = IMCRegistro.objects.filter(user=perfil.usuario).order_by('-data_registro')
        
        # Calculate statistics
        total_registros = imc_history.count()
        if total_registros > 0:
            imc_sum = sum(registro.imc for registro in imc_history)
            imc_medio = imc_sum / total_registros
            ultimo_imc = imc_history[0].imc if imc_history else None
        else:
            imc_medio = None
            ultimo_imc = None
        
        context['imc_history'] = imc_history
        context['titulo'] = f"Perfil de {perfil.nome_completo or perfil.usuario.username}"
        context['total_registros'] = total_registros
        context['imc_medio'] = imc_medio
        context['ultimo_imc'] = ultimo_imc
        
        return context
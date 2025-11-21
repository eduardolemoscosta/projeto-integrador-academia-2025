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
from .models import ProblemaMedico
from .forms import ProblemaMedicoForm 
from .models import Perfil, IMCRegistro, ProblemaMedico 

from .forms import IMCForm
from .models import ProblemaMedico, Perfil 

from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.exceptions import PermissionDenied


class UsuarioCreate(CreateView):
    template_name = "usuarios/signup.html"
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        
        grupo, _ = Group.objects.get_or_create(name="Docente") #ou Discentes

        # Get nome_completo and email from form before saving
        nome_completo = form.cleaned_data.get('nome_completo')
        email = form.cleaned_data.get('email')
        
        url = super().form_valid(form)

        # Save email to User model
        if email:
            self.object.email = email
            self.object.save()

        self.object.groups.add(grupo)
        
        # Create or get Perfil and set nome_completo and email
        perfil, _ = Perfil.objects.get_or_create(usuario=self.object)
        if nome_completo:
            perfil.nome_completo = nome_completo
        if email:
            perfil.email = email
        perfil.save()

        return url

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Criar uma conta"
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



class PerfilUpdate(LoginRequiredMixin, UpdateView):
    template_name = "cadastros/form_perfil.html"
    model = Perfil
    fields = ['email']  # Only email can be edited by staff
    success_url = reverse_lazy("inicio")

    def get_object(self, queryset=None):
        perfil, _ = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def form_valid(self, form):
        """Only allow staff to save changes"""
        if not self.request.user.is_staff:
            raise PermissionDenied("Apenas administradores podem editar informações do perfil.")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Meus dados"
        context['botao'] = "Atualizar"
        context['perfil'] = self.get_object()
        return context


class StaffPerfilUpdate(LoginRequiredMixin, UpdateView):
    """View for staff to edit user matrícula and nome_completo"""
    login_url = reverse_lazy('login')
    template_name = "cadastros/form_perfil_staff.html"
    model = Perfil
    fields = ['nome_completo', 'matricula']
    success_url = reverse_lazy("listar-usersauth")

    def dispatch(self, request, *args, **kwargs):
        """Only allow staff to access this view"""
        if not request.user.is_staff:
            raise PermissionDenied("Apenas administradores podem editar matrícula e nome.")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        perfil = get_object_or_404(Perfil, pk=self.kwargs['pk'])
        return perfil

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        perfil = self.get_object()
        context['titulo'] = f"Editar Perfil de {perfil.usuario.username}"
        context['botao'] = "Salvar Alterações"
        context['usuario'] = perfil.usuario
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
    
    return render(request, 'calcular_imc.html', {'form': form})

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
        
   # Esta função começa com 4 espaços
    def get_context_data(self, **kwargs):
    # 8 espaços
        context = super().get_context_data(**kwargs)
        perfil = self.get_object()

    # Get IMC History for this user
    # 8 espaços
        imc_history = IMCRegistro.objects.filter(user=perfil.usuario).order_by('-data_registro')

    # Get IMC calculation
    # 8 espaços
        if imc_history:
            total_registros = imc_history.count()
            imc_sum = sum(registro.imc for registro in imc_history)
            imc_medio = imc_sum / total_registros
            ultimo_imc = imc_history[0].imc if imc_history else None
        else:
            total_registros = 0
            imc_medio = None
            ultimo_imc = None

    # 8 espaços
        context['imc_history'] = imc_history
        context['titulo'] = f"Perfil de {perfil.nome_completo or perfil.usuario.username}"
        context['total_registros'] = total_registros
        context['imc_medio'] = imc_medio
        context['ultimo_imc'] = ultimo_imc

    #
    # AQUI ESTÁ A LINHA NOVA QUE ADICIONAMOS:
    #
    # 8 espaços
        context['meus_problemas'] = ProblemaMedico.objects.filter(usuario=perfil.usuario)

    # 8 espaços
        return context

@login_required # Garante que só usuários logados acedam
def adicionar_problema_medico(request):
    if request.method == 'POST':
        # Se o usuário enviou o formulário
        form = ProblemaMedicoForm(request.POST)
        if form.is_valid():
            # Salva no banco, mas não permanentemente ainda
            problema = form.save(commit=False)
            
            # ATRIBUI O USUÁRIO LOGADO! Esta é a ligação.
            problema.usuario = request.user 
            
            # Agora sim, salva no banco
            problema.save()
            
            # Redireciona para outra página (ex: o perfil)
            # Mude 'nome_da_url_do_perfil' para o nome real da sua URL de perfil
            return redirect('detalhes-usuario', pk=request.user.id)
    else:
        
        form = ProblemaMedicoForm()

    context = {
        'form': form
    }

    
    return render(request, 'usuarios/adicionar_problema.html', context)


def mostrar_matricula(request, user_id):
    """View to display the generated matricula after user registration"""
    user = get_object_or_404(User, id=user_id)
    perfil = get_object_or_404(Perfil, usuario=user)
    
    context = {
        'user': user,
        'perfil': perfil,
        'matricula': perfil.matricula,
        'nome_completo': perfil.nome_completo or user.username
    }
    
    return render(request, 'usuarios/mostrar_matricula.html', context)


def gerar_matricula(request):
    """View for staff to generate a matrícula only (no user creation)"""
    if not request.user.is_staff:
        raise PermissionDenied("Apenas administradores podem gerar matrículas.")
    
    if request.method == 'POST':
        # Generate matricula: year + "111" + sequential number (4 digits with leading zeros)
        current_year = datetime.now().year
        year_prefix = f"{current_year}111"
        
        # Find the highest sequential number for this year
        existing_matriculas = Perfil.objects.filter(
            matricula__startswith=year_prefix
        ).exclude(matricula__isnull=True).values_list('matricula', flat=True)
        
        if existing_matriculas:
            # Extract the sequential numbers and find the maximum
            sequential_numbers = []
            for mat in existing_matriculas:
                try:
                    # Extract the last 4 digits (sequential number)
                    seq_num = int(mat[-4:])
                    sequential_numbers.append(seq_num)
                except (ValueError, IndexError):
                    continue
            
            if sequential_numbers:
                next_sequential = max(sequential_numbers) + 1
            else:
                next_sequential = 1
        else:
            # First matrícula for this year
            next_sequential = 1
        
        # Format: year + "111" + sequential number (4 digits)
        matricula = f"{year_prefix}{next_sequential:04d}"
        
        context = {
            'matricula': matricula,
            'ano': current_year,
            'gerada': True
        }
        
        return render(request, 'usuarios/criar_matricula.html', context)
    
    # GET request - show form to generate matrícula
    return render(request, 'usuarios/criar_matricula.html', {'gerada': False})

def excluir_perfil(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    perfil.delete()
    return redirect('listar-usersauth')

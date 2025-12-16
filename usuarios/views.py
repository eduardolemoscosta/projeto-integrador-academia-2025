from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.contrib.auth.models import User, Group
from .forms import UsuarioForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import Perfil, IMCRegistro, ProblemaMedico, MatriculaDisponivel
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .forms import ProblemaMedicoForm, IMCForm, StaffPerfilForm
from django.contrib.auth.decorators import login_required
from datetime import datetime


class UsuarioCreate(CreateView):
    template_name = "usuarios/signup.html"
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Processa o formulário de criação de usuário.
        Cria o perfil e associa o usuário ao grupo apropriado.
        """
        grupo, _ = Group.objects.get_or_create(name="Docente") #ou Discentes

        # Get nome_completo, email, and matricula from form before saving
        nome_completo = form.cleaned_data.get('nome_completo')
        email = form.cleaned_data.get('email')
        matricula = form.cleaned_data.get('matricula')
        
        url = super().form_valid(form)

        # Save email to User model
        if email:
            self.object.email = email
            self.object.save()

        self.object.groups.add(grupo)
        
        # Create or get Perfil and set nome_completo, email, and matricula
        perfil, _ = Perfil.objects.get_or_create(usuario=self.object)
        if nome_completo:
            perfil.nome_completo = nome_completo
        if email:
            perfil.email = email
        if matricula:
            # Mark the matricula as used
            MatriculaDisponivel.objects.filter(
                matricula=matricula,
                utilizada=False
            ).update(utilizada=True)
            perfil.matricula = matricula
        perfil.save()

        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return url

    def form_invalid(self, form):
        """Exibe mensagem de erro quando o formulário é inválido."""
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Criar uma conta"
        context['botao'] = "Cadastrar"
        return context


class PerfilList(ListView):
    """
    Lista de perfis de usuários.
    Otimizada com select_related para reduzir queries ao banco de dados.
    """
    login_url = reverse_lazy('login')  
    model = Perfil
    template_name = 'cadastros/listas/userauth.html'
    paginate_by = 3

    def get_queryset(self):
        # Se o usuário é staff, ele pode ver todos os perfis
        if self.request.user.is_staff:
            queryset = Perfil.objects.select_related('usuario').all()
        else:
            # Usuário comum só pode ver o próprio perfil
            queryset = Perfil.objects.select_related('usuario').filter(usuario=self.request.user)
        
        # Aplicar o filtro de nome_completo, se existir
        txt_nome = self.request.GET.get('nome_completo')
        if txt_nome:
            queryset = queryset.filter(nome_completo__icontains=txt_nome)
        
        return queryset.order_by('-id')

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
    form_class = StaffPerfilForm
    success_url = reverse_lazy("listar-usersauth")

    def dispatch(self, request, *args, **kwargs):
        """Only allow staff to access this view"""
        if not request.user.is_staff:
            raise PermissionDenied("Apenas administradores podem editar matrícula e nome.")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        perfil = get_object_or_404(Perfil, pk=self.kwargs['pk'])
        return perfil
    
    def form_valid(self, form):
        """Marca a matrícula como utilizada se estiver sendo atribuída pela primeira vez."""
        perfil = form.save(commit=False)
        matricula = form.cleaned_data.get('matricula')
        
        # If matricula is being set for the first time, mark it as used
        if matricula and (not self.object.matricula or self.object.matricula != matricula):
            MatriculaDisponivel.objects.filter(
                matricula=matricula,
                utilizada=False
            ).update(utilizada=True)
        
        perfil.save()
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Exibe mensagem de erro quando o formulário é inválido."""
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        perfil = self.get_object()
        context['titulo'] = f"Editar Perfil de {perfil.usuario.username}"
        context['botao'] = "Salvar Alterações"
        context['usuario'] = perfil.usuario
        context['matricula_locked'] = perfil.matricula is not None and perfil.matricula != ''
        return context
    

def custom_logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def calcular_imc(request):
    """
    View para calcular e registrar o IMC do usuário.
    """
    if request.method == 'POST':
        form = IMCForm(request.POST)
        if form.is_valid():
            imc_registro = form.save(commit=False)
            imc_registro.user = request.user
            imc_registro.save()
            messages.success(request, f'IMC registrado com sucesso! Seu IMC atual é {imc_registro.imc:.2f}.')
            return redirect('progresso_imc')
    else:
        form = IMCForm()
    
    return render(request, 'calcular_imc.html', {'form': form})

@login_required
def progresso_imc(request):
    """
    Exibe o histórico de registros de IMC do usuário com estatísticas e análises.
    Otimizada para reduzir queries ao banco de dados.
    """
    registros = IMCRegistro.objects.filter(user=request.user).select_related('user').order_by('-data_registro')
    
    # Calcular estatísticas
    estatisticas = {}
    if registros.exists():
        imc_values = [r.imc for r in registros]
        peso_values = [r.peso for r in registros]
        
        estatisticas = {
            'total_registros': registros.count(),
            'imc_atual': imc_values[0] if imc_values else None,
            'imc_medio': sum(imc_values) / len(imc_values) if imc_values else None,
            'imc_maior': max(imc_values) if imc_values else None,
            'imc_menor': min(imc_values) if imc_values else None,
            'peso_atual': peso_values[0] if peso_values else None,
            'peso_maior': max(peso_values) if peso_values else None,
            'peso_menor': min(peso_values) if peso_values else None,
            'variacao_peso': peso_values[0] - peso_values[-1] if len(peso_values) > 1 else 0,
            'variacao_imc': imc_values[0] - imc_values[-1] if len(imc_values) > 1 else 0,
            'primeiro_registro': registros.last(),
            'ultimo_registro': registros.first(),
        }
        
        # Calcular valores absolutos para exibição
        estatisticas['variacao_imc_abs'] = abs(estatisticas['variacao_imc'])
        estatisticas['variacao_peso_abs'] = abs(estatisticas['variacao_peso'])
        
        # Determinar tendência
        if len(imc_values) >= 2:
            if imc_values[0] > imc_values[-1]:
                estatisticas['tendencia'] = 'diminuindo'
                estatisticas['tendencia_icon'] = 'fa-arrow-down'
                estatisticas['tendencia_color'] = 'success'
            elif imc_values[0] < imc_values[-1]:
                estatisticas['tendencia'] = 'aumentando'
                estatisticas['tendencia_icon'] = 'fa-arrow-up'
                estatisticas['tendencia_color'] = 'warning'
            else:
                estatisticas['tendencia'] = 'estável'
                estatisticas['tendencia_icon'] = 'fa-minus'
                estatisticas['tendencia_color'] = 'info'
        else:
            estatisticas['tendencia'] = None
    
    return render(request, 'progresso_imc.html', {
        'registros': registros,
        'estatisticas': estatisticas
    })

def apagar_imc(request, imc_id):
    """
    View para excluir um registro de IMC.
    Usuários só podem excluir seus próprios registros.
    """
    imc_registro = get_object_or_404(IMCRegistro, id=imc_id, user=request.user) 
    
    imc_registro.delete()
    messages.success(request, 'Registro de IMC excluído com sucesso!')
    
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
        """
        Adiciona dados de contexto para a visualização do perfil do usuário.
        Inclui histórico de IMC, estatísticas e problemas médicos.
        Otimizada com select_related para reduzir queries ao banco de dados.
        """
        context = super().get_context_data(**kwargs)
        perfil = self.get_object()

        # Obter histórico de IMC para este usuário (otimizado)
        imc_history = IMCRegistro.objects.filter(user=perfil.usuario).select_related('user').order_by('-data_registro')

        # Calcular estatísticas de IMC
        if imc_history:
            total_registros = imc_history.count()
            imc_sum = sum(registro.imc for registro in imc_history)
            imc_medio = imc_sum / total_registros
            ultimo_imc = imc_history[0].imc if imc_history else None
        else:
            total_registros = 0
            imc_medio = None
            ultimo_imc = None

        # Adicionar dados ao contexto (otimizado)
        context['imc_history'] = imc_history
        context['titulo'] = f"Perfil de {perfil.nome_completo or perfil.usuario.username}"
        context['total_registros'] = total_registros
        context['imc_medio'] = imc_medio
        context['ultimo_imc'] = ultimo_imc
        context['meus_problemas'] = ProblemaMedico.objects.filter(usuario=perfil.usuario).select_related('usuario')

        return context

@login_required
def adicionar_problema_medico(request):
    """
    View para adicionar um problema médico ao perfil do usuário.
    """
    if request.method == 'POST':
        form = ProblemaMedicoForm(request.POST)
        if form.is_valid():
            problema = form.save(commit=False)
            problema.usuario = request.user 
            problema.save()
            messages.success(request, 'Problema médico registrado com sucesso!')
            return redirect('detalhes-usuario', pk=request.user.id)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
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
    
    current_year = datetime.now().year
    year_prefix = f"{current_year}111"
    
    # Get all available (unused) matriculas
    matriculas_disponiveis = MatriculaDisponivel.objects.filter(utilizada=False).order_by('-data_criacao')
    
    if request.method == 'POST':
        # Generate new matricula: year + "111" + sequential number (4 digits with leading zeros)
        # Get all existing matriculas (both used and available)
        existing_matriculas_perfil = Perfil.objects.filter(
            matricula__startswith=year_prefix
        ).exclude(matricula__isnull=True).values_list('matricula', flat=True)
        
        existing_matriculas_disponiveis = MatriculaDisponivel.objects.filter(
            matricula__startswith=year_prefix
        ).values_list('matricula', flat=True)
        
        # Combine all existing matriculas
        all_existing = list(existing_matriculas_perfil) + list(existing_matriculas_disponiveis)
        
        if all_existing:
            # Extract the sequential numbers and find the maximum
            sequential_numbers = []
            for mat in all_existing:
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
        
        # Save the new matricula as available
        MatriculaDisponivel.objects.create(matricula=matricula)
        
        # Refresh the list of available matriculas
        matriculas_disponiveis = MatriculaDisponivel.objects.filter(utilizada=False).order_by('-data_criacao')
        
        context = {
            'matricula': matricula,
            'ano': current_year,
            'gerada': True,
            'matriculas_disponiveis': matriculas_disponiveis
        }
        
        return render(request, 'usuarios/criar_matricula.html', context)
    
    # GET request - show form to generate matrícula
    context = {
        'gerada': False,
        'matriculas_disponiveis': matriculas_disponiveis
    }
    return render(request, 'usuarios/criar_matricula.html', context)

def excluir_perfil(request, id):
    """
    View para excluir um perfil de usuário.
    Apenas staff pode excluir perfis.
    """
    if not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect('listar-usersauth')
    
    perfil = get_object_or_404(Perfil, id=id)
    perfil.delete()
    messages.success(request, 'Perfil excluído com sucesso!')
    return redirect('listar-usersauth')

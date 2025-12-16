from django.db.models.query import QuerySet
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .models import Campo, Exercicio, TrainingExercicio, Avaliacao
from django.urls import reverse_lazy
from .forms import TrainingExercicioForm, ExercicioForm
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django import forms
from django.contrib import messages

# Create Views
class CampoCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Campo
    fields = ['nome']
    form_class = ExercicioForm
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-campos')

class ExercicioCreate(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')  # Redireciona para a página de login se não autenticado
    group_required = u"Administrador"  # Restringe o acesso ao grupo "Administrador"
    model = Exercicio  # Modelo para o qual o formulário será gerado
    template_name = 'cadastros/form.html'  # Caminho para o template do formulário
    success_url = reverse_lazy('listar-exercicios')  # URL para redirecionamento após sucesso

    # Especificando os campos que aparecerão no formulário
    fields = ['nome', 'tipo', 'grupo', 'series', 'repeticoes', 'carga', 'tempo']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['titulo'] = "Cadastrar Exercício"  # Título para exibir no template
        context['botao'] = "Salvar"  # Texto do botão de submissão
        return context
    
class AvaliacaoCreate(GroupRequiredMixin, LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Avaliacao
    fields = ['usuario', 'data', 'hora', 'idade', 'peso', 'altura', 'pescoco', 
              'ombro_dir', 'ombro_esq', 'braco_relaxado_dir', 'braco_relaxado_esq', 
              'braco_contraido_dir', 'braco_contraido_esq', 'antebraco_dir', 
              'antebraco_esq', 'torax_relaxado', 'torax_contraido', 'cintura', 
              'quadril', 'coxa_dir', 'coxa_esq', 'panturrilha_dir', 'panturrilha_esq']
    template_name = 'cadastros/form_avaliacao.html'
    success_url = reverse_lazy('listar-avaliacoes')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['titulo'] = "Cadastrar Avaliação Fisica"
        context['botao'] = "Cadastrar Avaliação"

        return context


class TrainingExercicioCreate(LoginRequiredMixin, CreateView):
    """
    View para criar um novo programa de treinamento.
    """
    login_url = reverse_lazy('login')
    model = TrainingExercicio
    form_class = TrainingExercicioForm
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-training-exercicios')

    def form_valid(self, form):
        """Define automaticamente o usuário como o usuário logado e exibe mensagem de sucesso."""
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Programa de treinamento criado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Exibe mensagem de erro quando o formulário é inválido."""
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Remove usuario field from form for regular users
        if 'usuario' in form.fields:
            if not self.request.user.is_staff:
                # Hide usuario field for regular users - it will be set automatically
                form.fields['usuario'].widget = forms.HiddenInput()
                form.fields['usuario'].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cadastrar Treinamento'
        context['botao'] = 'Salvar'
        return context



# Update Views
class CampoUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Campo
    fields = ['nome']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-campos')

class ExercicioUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Exercicio
    fields = ['exercicio', 'tipo', 'grupo', 'descricao']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-exercicios')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['titulo'] = "Editar Exercício"
        context['botao'] = "Salvar"

        return context

class AvaliacaoUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Avaliacao
    fields = ['usuario', 'data', 'hora', 'idade', 'peso', 'altura', 'pescoco', 
              'ombro_dir', 'ombro_esq', 'braco_relaxado_dir', 'braco_relaxado_esq', 
              'braco_contraido_dir', 'braco_contraido_esq', 'antebraco_dir', 
              'antebraco_esq', 'torax_relaxado', 'torax_contraido', 'cintura', 
              'quadril', 'coxa_dir', 'coxa_esq', 'panturrilha_dir', 'panturrilha_esq']
    template_name = 'cadastros/form_avaliacao.html'
    success_url = reverse_lazy('listar-avaliacoes')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['titulo'] = "Editar Cadastro de Avaliação"
        context['botao'] = "Salvar"

        return context


class TrainingExercicioUpdate(LoginRequiredMixin, UpdateView):
    """
    View para editar um programa de treinamento existente.
    Usuários comuns só podem editar seus próprios programas.
    """
    login_url = reverse_lazy('login')
    model = TrainingExercicio
    form_class = TrainingExercicioForm
    template_name = 'cadastros/form_training_exercicio.html'
    success_url = reverse_lazy('listar-training-exercicios')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permissões antes de permitir a edição."""
        training_exercicio = get_object_or_404(TrainingExercicio, pk=self.kwargs['pk'])
        # Users can only edit their own programs, staff can edit any
        if not request.user.is_staff and training_exercicio.usuario != request.user:
            messages.error(request, "Você não tem permissão para editar este registro.")
            return HttpResponseForbidden("Você não tem permissão para editar este registro.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Exibe mensagem de sucesso após atualização bem-sucedida."""
        messages.success(self.request, 'Programa de treinamento atualizado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Exibe mensagem de erro quando o formulário é inválido."""
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return get_object_or_404(TrainingExercicio, pk=self.kwargs['pk'])

    def form_valid(self, form):
        # For regular users, ensure they can't change the usuario field
        if not self.request.user.is_staff:
            form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Remove usuario field from form for regular users
        if 'usuario' in form.fields:
            if not self.request.user.is_staff:
                # Hide usuario field for regular users - they can only edit their own programs
                form.fields['usuario'].widget = forms.HiddenInput()
                form.fields['usuario'].required = False
        return form



# Delete Views
class CampoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Campo
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-campos')

class ExercicioDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Exercicio
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-exercicios')

class AvaliacaoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    group_required = u"Administrador"
    model = Avaliacao
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-avaliacoes')

class TrainingExercicioDelete(LoginRequiredMixin, DeleteView):
    """
    View para excluir um programa de treinamento.
    Usuários comuns só podem excluir seus próprios programas.
    """
    login_url = reverse_lazy('login')
    model = TrainingExercicio
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-training-exercicios')

    def dispatch(self, request, *args, **kwargs):
        """Verifica permissões antes de permitir a exclusão."""
        training_exercicio = get_object_or_404(TrainingExercicio, pk=self.kwargs['pk'])
        # Users can only delete their own programs, staff can delete any
        if not request.user.is_staff and training_exercicio.usuario != request.user:
            messages.error(request, "Você não tem permissão para excluir este registro.")
            return redirect('listar-training-exercicios')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(TrainingExercicio, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        """Exibe mensagem de sucesso após exclusão bem-sucedida."""
        messages.success(request, 'Programa de treinamento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

    
# List Views
class CampoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Campo
    template_name = 'cadastros/listas/campo.html'

class ExercicioList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Exercicio
    template_name = 'cadastros/listas/exercicio.html'

class TrainingExercicioList(LoginRequiredMixin, ListView):
    """
    Lista de treinamentos com exercícios.
    Otimizada com select_related para reduzir queries ao banco de dados.
    """
    login_url = reverse_lazy('login')
    model = TrainingExercicio
    template_name = 'cadastros/listas/training_exercicio.html'
    paginate_by = 3
    context_object_name = 'programas'

    def get_queryset(self):
        # Se o usuário é staff, ele pode ver todos os programas
        if self.request.user.is_staff:
            queryset = TrainingExercicio.objects.select_related('usuario', 'exercicio').all()
        else:
            # Usuário comum só pode ver os próprios programas
            queryset = TrainingExercicio.objects.select_related('usuario', 'exercicio').filter(usuario=self.request.user)
        
        # Aplicar o filtro de nome_programa, se existir
        txt_nome = self.request.GET.get('nome_programa')
        if txt_nome:
            queryset = queryset.filter(nome_programa__icontains=txt_nome)
        
        return queryset.order_by('-id') 


class AvaliacaoList(LoginRequiredMixin, ListView):
    """
    Lista de avaliações físicas.
    Otimizada com select_related para reduzir queries ao banco de dados.
    """
    login_url = reverse_lazy('login')
    model = Avaliacao
    template_name = 'cadastros/listas/avaliacao.html'
    paginate_by = 1

    def get_queryset(self):
        # Se o usuário é staff, ele pode ver todas as avaliações
        if self.request.user.is_staff:
            queryset = Avaliacao.objects.select_related('usuario').all()
        else:
            # Usuário comum só pode ver as próprias avaliações
            queryset = Avaliacao.objects.select_related('usuario').filter(usuario=self.request.user)
        
        # Aplicar o filtro de nome_completo, se existir
        txt_nome = self.request.GET.get('nome_completo')
        if txt_nome:
            queryset = queryset.filter(nome_completo__icontains=txt_nome)
        
        return queryset.order_by('-data', '-hora')  




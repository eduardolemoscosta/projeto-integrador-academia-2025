from django import forms
from django.core.exceptions import ValidationError
from .models import TrainingExercicio, Exercicio

class TrainingExercicioForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de treinamentos com exercícios.
    Inclui validações para garantir dados consistentes.
    """
    class Meta:
        model = TrainingExercicio
        fields = ['usuario', 'exercicio', 'nome_programa', 'grupo', 'series', 'repeticoes', 'carga', 'tempo']
        widgets = {
            'nome_programa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do programa'}),
            'grupo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grupo muscular'}),
            'series': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
            'repeticoes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 1000}),
            'carga': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Carga em kg'}),
            'tempo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Tempo em minutos'}),
        }
        labels = {
            'nome_programa': 'Nome do Programa',
            'grupo': 'Grupo Muscular',
            'series': 'Séries',
            'repeticoes': 'Repetições',
            'carga': 'Carga (kg)',
            'tempo': 'Tempo (minutos)',
        }

    def clean_series(self):
        """Valida que o número de séries seja positivo."""
        series = self.cleaned_data.get('series')
        if series and series <= 0:
            raise ValidationError('O número de séries deve ser maior que zero.')
        if series and series > 50:
            raise ValidationError('O número de séries não pode ser maior que 50.')
        return series

    def clean_repeticoes(self):
        """Valida que o número de repetições seja positivo."""
        repeticoes = self.cleaned_data.get('repeticoes')
        if repeticoes and repeticoes <= 0:
            raise ValidationError('O número de repetições deve ser maior que zero.')
        if repeticoes and repeticoes > 1000:
            raise ValidationError('O número de repetições não pode ser maior que 1000.')
        return repeticoes

    def clean_carga(self):
        """Valida que a carga não seja negativa."""
        carga = self.cleaned_data.get('carga')
        if carga and carga < 0:
            raise ValidationError('A carga não pode ser negativa.')
        return carga

    def clean_tempo(self):
        """Valida que o tempo não seja negativo."""
        tempo = self.cleaned_data.get('tempo')
        if tempo and tempo < 0:
            raise ValidationError('O tempo não pode ser negativo.')
        return tempo

    def clean_nome_programa(self):
        """Valida que o nome do programa não esteja vazio."""
        nome_programa = self.cleaned_data.get('nome_programa')
        if nome_programa:
            nome_programa = nome_programa.strip()
            if len(nome_programa) < 3:
                raise ValidationError('O nome do programa deve ter pelo menos 3 caracteres.')
        return nome_programa

class ExercicioForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de exercícios.
    """
    class Meta:
        model = Exercicio
        fields = ['nome', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do exercício'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Exercício',
            'tipo': 'Tipo de Exercício',
        }

    def clean_nome(self):
        """Valida que o nome do exercício não esteja vazio."""
        nome = self.cleaned_data.get('nome')
        if nome:
            nome = nome.strip()
            if len(nome) < 2:
                raise ValidationError('O nome do exercício deve ter pelo menos 2 caracteres.')
        return nome
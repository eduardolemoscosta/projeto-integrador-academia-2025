from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import IMCRegistro

class UsuarioForm(UserCreationForm):
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Email'}))
    nome_completo = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Nome completo'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Nome de usuário'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control form-control-user', 'placeholder': 'Senha'})
        self.fields['password1'].help_text = 'Sua senha deve ter pelo menos 8 caracteres.'
        self.fields['password2'].widget.attrs.update({'class': 'form-control form-control-user', 'placeholder': 'Confirmar senha'})
        self.fields['password2'].help_text = 'Digite a mesma senha novamente para verificação.'

    def clean_email(self):
        e = self.cleaned_data.get('email')
        if User.objects.filter(email=e).exists():
            raise ValidationError(f"O email {e} já está em uso.")
        return e

class IMCForm(forms.ModelForm):
    class Meta:
        model = IMCRegistro
        fields = ['peso', 'altura']
        widgets = {
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso em kg'}),
            'altura': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Altura em metros'}),
        }


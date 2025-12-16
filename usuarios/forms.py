from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import IMCRegistro, ProblemaMedico, MatriculaDisponivel, Perfil

class UsuarioForm(UserCreationForm):
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Email'}))
    nome_completo = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Nome completo'}))
    matricula = forms.CharField(
        max_length=14, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user', 
            'placeholder': 'Matrícula (opcional)'
        }),
        help_text='Digite sua matrícula se você recebeu uma. Caso contrário, deixe em branco.'
    )

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
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            # Remove any whitespace
            matricula = matricula.strip()
            
            # Check if matricula is already assigned to another user
            if Perfil.objects.filter(matricula=matricula).exclude(usuario=self.instance if self.instance.pk else None).exists():
                raise ValidationError("Esta matrícula já está em uso por outro usuário.")
            
            # Check if matricula exists in available matriculas
            matricula_disponivel = MatriculaDisponivel.objects.filter(
                matricula=matricula,
                utilizada=False
            ).first()
            
            if not matricula_disponivel:
                raise ValidationError("Esta matrícula não está disponível ou já foi utilizada. Verifique se digitou corretamente.")
        
        return matricula

class IMCForm(forms.ModelForm):
    """
    Formulário para registro de IMC (Índice de Massa Corporal).
    Inclui validações para garantir valores realistas.
    """
    class Meta:
        model = IMCRegistro
        fields = ['peso', 'altura']
        widgets = {
            'peso': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Peso em kg',
                'step': '0.1',
                'min': '20',
                'max': '300'
            }),
            'altura': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Altura em metros (ex: 1.75)',
                'step': '0.01',
                'min': '0.5',
                'max': '2.5'
            }),
        }
        labels = {
            'peso': 'Peso (kg)',
            'altura': 'Altura (metros)',
        }

    def clean_peso(self):
        """Valida que o peso seja um valor realista."""
        peso = self.cleaned_data.get('peso')
        if peso:
            if peso < 20:
                raise ValidationError('O peso deve ser pelo menos 20 kg.')
            if peso > 300:
                raise ValidationError('O peso não pode ser maior que 300 kg.')
        return peso

    def clean_altura(self):
        """Valida que a altura seja um valor realista."""
        altura = self.cleaned_data.get('altura')
        if altura:
            if altura < 0.5:
                raise ValidationError('A altura deve ser pelo menos 0.5 metros.')
            if altura > 2.5:
                raise ValidationError('A altura não pode ser maior que 2.5 metros.')
        return altura

    def clean(self):
        """Validação cruzada entre peso e altura."""
        cleaned_data = super().clean()
        peso = cleaned_data.get('peso')
        altura = cleaned_data.get('altura')
        
        if peso and altura:
            # Calcular IMC para verificar se está em um range razoável
            imc = peso / (altura ** 2)
            if imc < 10:
                raise ValidationError('Os valores informados resultam em um IMC muito baixo. Verifique os dados.')
            if imc > 60:
                raise ValidationError('Os valores informados resultam em um IMC muito alto. Verifique os dados.')
        
        return cleaned_data

class ProblemaMedicoForm(forms.ModelForm):
    class Meta:
        model = ProblemaMedico
        fields = ['descricao'] 
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descreva o problema médico...'}),
        }
        labels = {
            'descricao': 'Descrição do Problema',
        }


class StaffPerfilForm(forms.ModelForm):
    """Form for staff to edit user profile with matricula validation"""
    class Meta:
        model = Perfil
        fields = ['nome_completo', 'matricula']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If matricula is already set, make it read-only
        if self.instance and self.instance.pk and self.instance.matricula:
            self.fields['matricula'].widget.attrs['readonly'] = True
            self.fields['matricula'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['matricula'].help_text = 'Esta matrícula está bloqueada e não pode ser alterada.'
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            # Remove any whitespace
            matricula = matricula.strip()
            
            # If matricula is already set, prevent changing it
            if self.instance and self.instance.pk and self.instance.matricula:
                if self.instance.matricula != matricula:
                    raise ValidationError("Esta matrícula está bloqueada e não pode ser alterada.")
                return matricula
            
            # Check if matricula is already assigned to another user
            if Perfil.objects.filter(matricula=matricula).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                raise ValidationError("Esta matrícula já está em uso por outro usuário.")
            
            # Check if matricula exists in available matriculas (only if it's a new assignment)
            matricula_disponivel = MatriculaDisponivel.objects.filter(
                matricula=matricula,
                utilizada=False
            ).first()
            
            if not matricula_disponivel:
                raise ValidationError("Esta matrícula não está disponível ou já foi utilizada. Verifique se digitou corretamente.")
        
        return matricula

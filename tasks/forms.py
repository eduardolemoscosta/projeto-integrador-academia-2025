from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Task
from django.forms import DateInput
from django.contrib.auth.models import User
from cadastros.models import TrainingExercicio

class TaskForm(forms.ModelForm):
    """
    Formulário para criação e edição de tarefas/eventos.
    Inclui validações para datas e horários.
    """
    class Meta:
        model = Task
        fields = [
            'usuario', 
            "title",
            "description",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Insira o título do evento"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Insira a descrição do evento", "rows": 4}
            ),
            "start_date": DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": DateInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": DateInput(attrs={"class": "form-control", "type": "time"}),
        }
        labels = {
            "title": "Título do Evento",
            "description": "Descrição",
            "start_date": "Data de Início",
            "end_date": "Data de Término",
            "start_time": "Hora de Início",
            "end_time": "Hora de Término",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide usuario field - it will be set automatically to the current staff user
        if 'usuario' in self.fields:
            del self.fields['usuario']

    def clean_title(self):
        """Valida que o título não esteja vazio."""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise ValidationError('O título deve ter pelo menos 3 caracteres.')
        return title

    def clean(self):
        """Validações cruzadas entre datas e horários."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Validar que a data de início não seja posterior à data de término
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError({
                    'end_date': 'A data de término não pode ser anterior à data de início.'
                })

        # Validar que se ambas as datas são iguais, o horário de término seja posterior ao de início
        if start_date and end_date and start_date == end_date:
            if start_time and end_time:
                if start_time >= end_time:
                    raise ValidationError({
                        'end_time': 'Quando a data de início e término são iguais, a hora de término deve ser posterior à hora de início.'
                    })

        return cleaned_data

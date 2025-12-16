from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from cadastros.models import TrainingExercicio

class Task(models.Model):
    """
    Modelo para representar tarefas/eventos no calendário.
    Usado para agendar eventos, aulas e outras atividades na academia.
    Valida automaticamente que a data de início não seja posterior à data de término.
    """
    id = models.BigAutoField(primary_key=True)

    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(verbose_name="Data de Término")
    total_subs = models.PositiveIntegerField(default=0, verbose_name="Total de Inscrições")
    subs = models.PositiveIntegerField(default=0, verbose_name="Inscrições Atuais")
    start_time = models.TimeField(verbose_name="Hora de Início")
    end_time = models.TimeField(verbose_name="Hora de Término")

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Tarefa/Evento"
        verbose_name_plural = "Tarefas/Eventos"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def clean(self):
        """
        Valida que as datas de início e término sejam consistentes.
        """
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('A data de início não pode ser posterior à data de fim.')
        elif self.start_date is None or self.end_date is None:
            raise ValidationError('Ambas as datas de início e fim devem ser fornecidas.')

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para validar os dados antes de salvar.
        """
        self.clean()
        super().save(*args, **kwargs)
from django.db import models
from datetime import timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User



def get_default_exercicio():
    """
    Retorna o primeiro exercício disponível como padrão.
    Usado como valor padrão para o campo exercicio em TrainingExercicio.
    """
    return Exercicio.objects.first()

class Campo(models.Model):
    """
    Modelo para representar campos de treinamento.
    """
    nome = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ['nome']

    def __str__(self):
        return f"[Campo: {self.nome}]"

class Exercicio(models.Model):
    """
    Modelo para representar exercícios físicos.
    Cada exercício possui um nome e um tipo (Força, Cardio ou Flexibilidade).
    """
    nome = models.CharField(max_length=100, default='Default Name')
    tipo = models.CharField(
        max_length=50, 
        choices=[
            ('Força', 'Força'), 
            ('Cardio', 'Cardio'), 
            ('Flexibilidade', 'Flexibilidade')
        ], 
        default='Força'
    )

    class Meta:
        verbose_name = "Exercício"
        verbose_name_plural = "Exercícios"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class TrainingExercicio(models.Model):
    """
    Modelo para representar programas de treinamento com exercícios específicos.
    Relaciona um exercício a um programa de treino com séries, repetições, carga e tempo.
    Cada treinamento pertence a um usuário específico.
    """
    exercicio = models.ForeignKey(
        Exercicio, 
        related_name='treinamentos', 
        on_delete=models.CASCADE, 
        default=get_default_exercicio
    )
    nome_programa = models.CharField(max_length=100)
    grupo = models.CharField(max_length=50, default='Desconhecido') 
    series = models.PositiveIntegerField(default=10)
    repeticoes = models.PositiveIntegerField(default=10)
    carga = models.IntegerField(default=0, verbose_name="Carga (kg)")
    tempo = models.IntegerField(default=0, verbose_name="Minutos (mn)")  
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL do Vídeo")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = "Programa de Treinamento"
        verbose_name_plural = "Programas de Treinamento"
        ordering = ['-id']

    def __str__(self):
        return f'{self.nome_programa} - {self.grupo}'
    

class Avaliacao(models.Model):
    """
    Modelo para representar avaliações físicas completas de usuários.
    Armazena medidas corporais detalhadas incluindo peso, altura, circunferências
    de diferentes partes do corpo e data/hora da avaliação.
    """
    nome_completo = models.CharField(max_length=50, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()  
    idade = models.PositiveIntegerField()  
    peso = models.DecimalField(max_digits=5, decimal_places=2)  
    altura = models.DecimalField(max_digits=4, decimal_places=2)  
    pescoco = models.DecimalField(max_digits=5, decimal_places=2)  
    ombro_dir = models.DecimalField(max_digits=5, decimal_places=2)
    ombro_esq = models.DecimalField(max_digits=5, decimal_places=2)
    braco_relaxado_dir = models.DecimalField(max_digits=5, decimal_places=2)
    braco_relaxado_esq = models.DecimalField(max_digits=5, decimal_places=2)
    braco_contraido_dir = models.DecimalField(max_digits=5, decimal_places=2)
    braco_contraido_esq = models.DecimalField(max_digits=5, decimal_places=2)
    antebraco_dir = models.DecimalField(max_digits=5, decimal_places=2)
    antebraco_esq = models.DecimalField(max_digits=5, decimal_places=2)
    torax_relaxado = models.DecimalField(max_digits=5, decimal_places=2)
    torax_contraido = models.DecimalField(max_digits=5, decimal_places=2)
    cintura = models.DecimalField(max_digits=5, decimal_places=2)
    quadril = models.DecimalField(max_digits=5, decimal_places=2)
    coxa_dir = models.DecimalField(max_digits=5, decimal_places=2)
    coxa_esq = models.DecimalField(max_digits=5, decimal_places=2)
    panturrilha_dir = models.DecimalField(max_digits=5, decimal_places=2)
    panturrilha_esq = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "Avaliação Física"
        verbose_name_plural = "Avaliações Físicas"
        ordering = ['-data', '-hora']

    def __str__(self):
        return f"Avaliação de {self.usuario.first_name} {self.usuario.last_name} | Data: {self.data} | Hora: {self.hora}"

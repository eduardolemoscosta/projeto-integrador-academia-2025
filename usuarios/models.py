from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Perfil(models.Model):
    nome_completo = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=100, null=True)
    matricula = models.CharField(max_length=14, null=True, unique=True, verbose_name="MATRICULA")
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)


class IMCRegistro(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    peso = models.FloatField()
    altura = models.FloatField()
    imc = models.FloatField(editable=False)
    data_registro = models.DateTimeField(default=timezone.now)

    def calcular_imc(self):
        return self.peso / (self.altura ** 2)

    def save(self, *args, **kwargs):
        self.imc = self.calcular_imc()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.data_registro.strftime("%d/%m/%Y")}'

class ProblemaMedico(models.Model):
    # Esta linha liga o problema ao usuário
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problemas")

    descricao = models.TextField()

    data_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.descricao[:30]}"


class MatriculaDisponivel(models.Model):
    """Model to store generated but unused matriculas"""
    matricula = models.CharField(max_length=14, unique=True, verbose_name="MATRICULA")
    data_criacao = models.DateTimeField(auto_now_add=True)
    utilizada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Matrícula Disponível"
        verbose_name_plural = "Matrículas Disponíveis"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.matricula} - {'Utilizada' if self.utilizada else 'Disponível'}"
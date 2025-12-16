from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Perfil(models.Model):
    """
    Modelo para representar o perfil estendido de um usuário.
    Armazena informações adicionais como nome completo, email e matrícula.
    Relaciona-se com o modelo User do Django através de uma relação OneToOne.
    """
    nome_completo = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=100, null=True)
    matricula = models.CharField(max_length=14, null=True, unique=True, verbose_name="MATRICULA")
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo or self.usuario.username} - {self.matricula or 'Sem matrícula'}"


class IMCRegistro(models.Model):
    """
    Modelo para registrar o histórico de IMC (Índice de Massa Corporal) de usuários.
    Calcula automaticamente o IMC ao salvar o registro.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    peso = models.FloatField()
    altura = models.FloatField()
    imc = models.FloatField(editable=False)
    data_registro = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Registro de IMC"
        verbose_name_plural = "Registros de IMC"
        ordering = ['-data_registro']

    def calcular_imc(self):
        """
        Calcula o IMC baseado no peso e altura.
        Fórmula: IMC = peso / (altura²)
        """
        return self.peso / (self.altura ** 2)

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para calcular o IMC automaticamente."""
        self.imc = self.calcular_imc()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - IMC: {self.imc:.2f} - {self.data_registro.strftime("%d/%m/%Y")}'

class ProblemaMedico(models.Model):
    """
    Modelo para registrar problemas médicos de usuários.
    Permite que usuários informem condições de saúde relevantes para o treinamento.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="problemas")
    descricao = models.TextField()
    data_registro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Problema Médico"
        verbose_name_plural = "Problemas Médicos"
        ordering = ['-data_registro']

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
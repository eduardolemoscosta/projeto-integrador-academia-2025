from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil, MatriculaDisponivel


@receiver(pre_save, sender=User)
def grant_staff_permissions(sender, instance, **kwargs):
    """
    Automatically grant staff and admin permissions to users with emails
    ending in '@escolar.ifrn.edu.br'
    """
    if instance.email and instance.email.endswith('@escolar.ifrn.edu.br'):
        # Grant staff and superuser permissions
        instance.is_staff = True
        instance.is_superuser = True


@receiver(post_save, sender=Perfil)
def mark_matricula_as_used(sender, instance, created, **kwargs):
    """
    Mark a matricula as used when it's assigned to a Perfil
    """
    if instance.matricula:
        MatriculaDisponivel.objects.filter(
            matricula=instance.matricula,
            utilizada=False
        ).update(utilizada=True)


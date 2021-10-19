from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    dni = models.IntegerField(default=0)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    inquilino = models.BooleanField(default=False)
    propietario = models.BooleanField(default=False)
    descripcion = models.TextField(max_length=400, blank=True)
    image = models.ImageField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    average = models.IntegerField(default=0)

class PermiteScore(models.Model):
    id = models.AutoField(primary_key=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propietario_user")
    inquilino = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquilino_user")
    active = models.BooleanField(default=False)

    def __str__(self):
        return f'N°{self.id} - {self.inquilino} permite que {self.propietario} le ponga un score'

class Score(models.Model):
    id = models.AutoField(primary_key=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propietario_score")
    inquilino = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inquilino_score")
    puntaje = models.IntegerField()
    desde = models.DateField()
    hasta = models.DateField()
    time = models.CharField(max_length=12)
    comentario = models.CharField(max_length=400)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'N°{self.id} - {self.propietario} puntuó a {self.inquilino} con: "{self.puntaje}" comentando {self.comentario}'

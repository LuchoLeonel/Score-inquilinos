from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Score, User, PermiteScore
from .util import comparar, relacion_score, relacion_terminada, allowToScore, allowToBeScored, my_score
from .util import check_scores, amount_scores, render_profile, render_register, render_update, render_password, calcular_time


class NewTaskForm(forms.Form):
    name = forms.CharField(label="search")

#class New_user(forms.Form):
    #dni = models.IntegerField(default=0)
    #nombre = models.CharField(label="nombre", max_length=50, help_text="Nombre")
    #apellido = models.CharField(label="apellido", max_length=50, help_text="Apellido")
    #inquilino = models.BooleanField(label="inquilino", default=False)
    #propietario = models.BooleanField(label="inquilino", default=False)
    #image = models.ImageField(label="image", null=True, blank=True)


# Create your views here.
def index(request):
    # Cargamos los usuarios existentes y renderizamos el index.
    usuarios = User.objects.all()
    return render(request, "score/index.html", {
        "usuarios": usuarios,
        "tipo": "usuarios",
    })

def inquilinos(request):
    # Cargamos unicamente los inquilinos y renderizamos el index.
    inquilinos = User.objects.filter(inquilino=True)
    return render(request, "score/index.html", {
        "usuarios": inquilinos,
        "tipo": "inquilinos",
    })

def login_view(request):
    if request.method == "POST":
        # Tratamos de loguearnos como usuarios.
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Si se autenticó el usuario cargamos el index, de lo contrario mostramos que hubo un error.
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "score/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "score/login.html")


@login_required(login_url='login')
def logout_view(request):
    # Deslogueamos al usuario.
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        # Cargamos todos los datos a variables.
        username = request.POST["username"]
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        email = request.POST["email"]
        dni = request.POST["dni"]
        if request.FILES:
            image = request.FILES["adjunto"]
            image.name = username
        else:
            image = ""
        inquilino = True if request.POST.get("inquilino") == "si" else False
        propietario = True if request.POST.get("propietario") == "si" else False

        # Nos aseguramos que todo esté bien con el password.
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            # Función que cree, está en util.py
            return render_register(request, "Passwords must match.")

        if len(password) <= 1:
            return render_register(request, "Passwords must have 8 characters.")

        # Corroboramos que el nombre de usuario, mail y DNI no hayan sido usados.
        users = User.objects.values()
        for user in users:
            if user["username"] == username:
                return render_register(request, "Username already taken.")

            if user["email"] == email:
                return render_register(request, "Email already taken.")

            if not dni:
                return render_register(request, "No DNI was given.")

            if int(user["dni"]) == int(dni):
                return render_register(request, "DNI already registred.")

        # Tratamos de crear un nuevo usuario.
        try:
            user = User.objects.create_user(username = username, dni = dni, nombre = nombre, apellido = apellido,
                email = email, image = image, password = password, inquilino = inquilino, propietario = propietario)
            user.save()
        except (IntegrityError):
            return render_register(request, "Error.")
        
        # Logueamos el usuario y redireccionamos al índice.
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        return render(request, "score/register.html")

@login_required(login_url='login')
def update(request):
    user_actual = User.objects.get(id = request.user.id)
    if request.method == "POST":
        # Cargamos lo datos ingresados.
        username = request.POST["username"]
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        email = request.POST["email"]
        descripcion = request.POST["descripcion"]
        inquilino = True if request.POST.get("inquilino") == "si" else False
        propietario = True if request.POST.get("propietario") == "si" else False

        # Corroboramos que el nombre de usuario, mail y DNI no hayan sido usados.
        users = User.objects.exclude(id = user_actual.id).values()
        for user in users:
            if user["username"] == username:
                return render_update(request, user_actual, "Username already taken.")

            if user["email"] == email:
                return render_update(request, user_actual, "Email already taken.")
        
        #Cargamos la imagen nueva (si tiene)
        if request.FILES:
            image = request.FILES["adjunto"]
            image.name = username
            user_actual.image = image
        # Sobreescribimos los valores, guardamos y redireccionamos al perfil.
        user_actual.username = username
        user_actual.nombre = nombre
        user_actual.apellido = apellido
        user_actual.email = email
        user_actual.propietario = propietario
        user_actual.inquilino = inquilino
        user_actual.descripcion = descripcion
        user_actual.save()
        return HttpResponseRedirect(reverse("profile", kwargs={'id': user_actual.id}))

    if request.method == "GET":
        return render_update(request, user_actual, False)

@login_required(login_url='login')
def changePassword(request):
    usuario = User.objects.get(id = request.user.id)
    if request.method == "POST":
        # Cargamos los datos ingresados.
        password = request.POST["password"]
        newPassword = request.POST["newPassword"]
        confirmNewPassowrd = request.POST["confirmNewPassowrd"]

        # Chequeamos que todo este bien con los passwords.
        if not usuario.check_password(password):
            return render_password(request, usuario, "Enter the right password.")
        if newPassword != confirmNewPassowrd:
            return render_password(request, usuario, "Passwords must match.")
        if len(newPassword) <= 1:
            return render_password(request, usuario, "Passwords must have 8 characters.")
        
        # Guardamos el nuevo password, logueamos y redireccionamos.
        usuario.set_password(newPassword)
        usuario.save()
        login(request, usuario)
        return HttpResponseRedirect(reverse("profile", kwargs={'id': usuario.id}))
    if request.method == "GET":
        return render_password(request, usuario, False)


def profile(request, id):
    # Cargamos el usuario, los scores que otros usuarios hicieron de él y calculamos el average score.
    usuario = User.objects.get(id=id)
    # check_scores es una función que te devuelve los scores del usuario. Está en util.py
    scores = check_scores(usuario)
    # average_score es una función que calcula el promedio de todos los scores. Está en util.py
    average_score = amount_scores(scores)
    
    if request.method == "POST":
        # Cargamos el usuario logueado, y lo datos ingresados.
        user = User.objects.get(id=request.user.id)
        scoring = request.POST["scoring"]
        desde = request.POST["desde"]
        hasta = request.POST["hasta"]
        
        # relacion_score es una función que si el usuario del perfil le autorizó al usuario logueado que lo califique, te devuelve ese model.
        relacion = relacion_score(user, usuario)
        # Corroboramos que todo está en orden.
        if not relacion:
            # render_profile es una función en util.py que renderiza la página del profile.
            return render_profile(request, usuario, scores, "No se pudo guardar, por favor recarga la página.")

        if not desde or not hasta:
            return render_profile(request, usuario, scores, "Por favor ingrese una fecha para calificar.")

        if hasta < desde or datetime.now() < datetime.strptime(request.POST["hasta"], '%Y-%m-%d'):
            return render_profile(request, usuario, scores, "Por favor ingrese una fecha correcta.")

        # calcular_time es una función que calcula cuanto tiempo se vivió el usuario en ese lugar tomando dos parametros (desde, hasta).
        time = calcular_time(desde, hasta)
        comentario = request.POST["comentario"]
        # Tratamos de crear el score.
        try:
            crear_score = Score(inquilino = usuario, propietario = user, puntaje = scoring,
                desde = desde, hasta = hasta, time = time, comentario=comentario)
            crear_score.save()
            # Cambiamos la relación.active a false para que el usuario ya no lo pueda volver a calificar
            relacion.active = False
            relacion.save()
            # Cargamos todos los scores del usuario y calculamos el nuevo promedio.
            scores = check_scores(usuario)
            average_score = amount_scores(scores)
            usuario.average = average_score
            usuario.save()
        except (ValidationError):
            return render_profile(request, usuario, scores, "Inserte un formato de fecha válido. Ej: 2021-04-13")
    
    return render_profile(request, usuario, scores, False)

def buscar(request):
    # Cargamos los usuarios.
    users = User.objects.all()
    if request.method == "POST":
        name = request.POST["buscar"]
        lista = set()
        #Buscamos entre los usuarios si hay alguna coincidencia.
        for user in users:
            # comparar es un función que compara si hay alguna coincidencia de username, nombre, apellido o dni.
            iguales = comparar(user, name)
            # Si hay coincidencia se agrega el usuario a la lista vacía que se creó anteriormente.
            if iguales == True:
                lista.add(user)
        return render(request, "score/index.html", {
            "usuarios": lista,
            "tipo": "usuarios encontrados",
        })
    else:
        return render(request, "score/index.html", {
            "usuarios": usuarios,
            "tipo": "usuarios",
            "message": "Error."
        })


@csrf_exempt
@login_required(login_url='login')
def allowScore(request, id, id_user):
    if request.method == "POST":
        #Cargamos el propietario y el inquilino.
        propietario = User.objects.get(id=id)
        inquilino = User.objects.get(id=id_user)
        # Corroboramos si tienen una relación activa (si no lo puntuó todavia) o tienen una relación terminada (ya lo puntuó).
        activa = allowToScore(propietario, inquilino)
        terminada = relacion_terminada(propietario, inquilino)
        # Si alguna es correcta retornamos falso porque no puede volver a permitirle que lo puntue.
        if terminada or activa:
            return HttpResponse(False)
        # Creamos la relación activa que lo va a permitir puntuar y retornamos verdaero.
        crear_permitir_score = PermiteScore(inquilino = inquilino, propietario = propietario, active=True)
        crear_permitir_score.save()
        return HttpResponse(True)
        

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
    usuarios = User.objects.all()
    return render(request, "score/index.html", {
        "usuarios": usuarios,
        "tipo": "usuarios",
    })

def inquilinos(request):
    inquilinos = User.objects.filter(inquilino=True)
    return render(request, "score/index.html", {
        "usuarios": inquilinos,
        "tipo": "inquilinos",
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
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

        # Attempt to create new user
        try:
            user = User.objects.create_user(username = username, dni = dni, nombre = nombre, apellido = apellido,
                email = email, image = image, password = password, inquilino = inquilino, propietario = propietario)
            user.save()
        except (IntegrityError):
            return render_register(request, "Error.")

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        return render(request, "score/register.html")

@login_required(login_url='login')
def update(request):
    user_actual = User.objects.get(id = request.user.id)
    if request.method == "POST":
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
        
        if request.FILES:
            image = request.FILES["adjunto"]
            image.name = username
            user_actual.image = image
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
        password = request.POST["password"]
        newPassword = request.POST["newPassword"]
        confirmNewPassowrd = request.POST["confirmNewPassowrd"]
        if not usuario.check_password(password):
            return render_password(request, usuario, "Enter the right password.")
        if newPassword != confirmNewPassowrd:
            return render_password(request, usuario, "Passwords must match.")
        if len(newPassword) <= 1:
            return render_password(request, usuario, "Passwords must have 8 characters.")
        usuario.set_password(newPassword)
        usuario.save()
        login(request, usuario)
        return HttpResponseRedirect(reverse("profile", kwargs={'id': usuario.id}))
    if request.method == "GET":
        return render_password(request, usuario, False)


def profile(request, id):
    usuario = User.objects.get(id=id)
    scores = check_scores(usuario)
    average_score = amount_scores(scores)
    
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        scoring = request.POST["scoring"]
        desde = request.POST["desde"]
        hasta = request.POST["hasta"]
        
        relacion = relacion_score(user, usuario)
        if not relacion:
            return render_profile(request, usuario, scores, "No se pudo guardar, por favor recarga la página.")

        if not desde or not hasta:
            return render_profile(request, usuario, scores, "Por favor ingrese una fecha para calificar.")

        if hasta < desde or datetime.now() < datetime.strptime(request.POST["hasta"], '%Y-%m-%d'):
            return render_profile(request, usuario, scores, "Por favor ingrese una fecha correcta.")

        time = calcular_time(desde, hasta)
        comentario = request.POST["comentario"]
        try:
            crear_score = Score(inquilino = usuario, propietario = user, puntaje = scoring,
                desde = desde, hasta = hasta, time = time, comentario=comentario)
            crear_score.save()
            relacion.active = False
            relacion.save()
            scores = check_scores(usuario)
            average_score = amount_scores(scores)
            usuario.average = average_score
            usuario.save()
        except (ValidationError):
            return render_profile(request, usuario, scores, "Inserte un formato de fecha válido. Ej: 2021-04-13")
    
    return render_profile(request, usuario, scores, False)

def buscar(request):
    users = User.objects.all()
    if request.method == "POST":
        name = request.POST["buscar"]
        lista = set()
        for user in users:
            iguales = comparar(user, name)
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
        propietario = User.objects.get(id=id)
        inquilino = User.objects.get(id=id_user)
        activa = allowToScore(propietario, inquilino)
        terminada = relacion_terminada(propietario, inquilino)
        if terminada or activa:
            return HttpResponse(False)
        crear_permitir_score = PermiteScore(inquilino = inquilino, propietario = propietario, active=True)
        crear_permitir_score.save()
        return HttpResponse(True)
        

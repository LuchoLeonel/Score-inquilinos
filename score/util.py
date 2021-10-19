from django.core.exceptions import ObjectDoesNotExist
from .models import Score, User, PermiteScore
from django.shortcuts import render
from django.contrib.auth import authenticate
from datetime import datetime

def comparar(user, name):
    nombre = name.casefold()
    dni = int(user.dni)
    user = [user.username.casefold(), user.nombre.casefold(), user.apellido.casefold()]
    if nombre in user:
        return True
    if nombre.isnumeric() and int(nombre) == dni:
        return True
    return False


def relacion_score(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(propietario=usuario_1, inquilino=usuario_2, active=True)
    except (ObjectDoesNotExist):
        permite = False
    return permite


def allowToScore(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(inquilino=usuario_1, propietario=usuario_2, active=True)
    except (ObjectDoesNotExist):
        permite = False

    if permite:
        allow = True
    else:
        allow = False
    return allow

def allowToBeScored(usuario_1, usuario_2):
    try:
        permite_2 = PermiteScore.objects.get(propietario=usuario_1, inquilino=usuario_2, active=True)
    except (ObjectDoesNotExist):
        permite_2 = False

    if permite_2:
        allow = True
    else:
        allow = False
    return allow


def relacion_terminada(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(propietario=usuario_1, inquilino=usuario_2, active=False)
    except (ObjectDoesNotExist):
        permite = False
    return permite

def my_score(usuario_1, usuario_2):
    try:
        my_score = Score.objects.get(inquilino=usuario_1, propietario=usuario_2)
    except (ObjectDoesNotExist):
        my_score = False
    return my_score

def they_score(usuario_1, usuario_2):
    try:
        my_score = Score.objects.get(propietario=usuario_1, inquilino=usuario_2)
    except (ObjectDoesNotExist):
        my_score = False
    return my_score

def check_scores(usuario):
    try:
        scores = Score.objects.filter(inquilino=usuario)
    except (ObjectDoesNotExist):
        scores = False            
    return scores

def amount_scores(scores):
    amount = 0
    for score in scores:
        amount += score.puntaje
    if amount != 0:
        average = amount / len(scores)
    else:
        average = 0
    return int(average)

def render_profile(request, usuario, scores, message):
 
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        allow = {
            "allow_to_score": allowToScore(usuario, user),
            "allow_to_be_scored": allowToBeScored(usuario, user),
            "my_score": my_score(usuario, user),
            "they_score": they_score(usuario, user)}
    else:
        allow = {
            "allow_to_score": False,
            "allow_to_be_scored": False,
            "my_score": False,
            "they_score": False}

    return render(request, "score/profile.html", {
        "usuario": usuario,
        "message": message,
        "scores": scores,
        "allow": allow,
        })


def render_register(request, message):
    return render(request, "score/register.html", {
        "message": message,
        })

def render_update(request, usuario, message):
    return render(request, "score/update.html", {
        "usuario": usuario,
        "message": message
        })

def render_password(request, usuario, message):
    return render(request, "score/password.html", {
        "usuario": usuario,
        "message": message
        })

def calcular_time(desde, hasta):
    tiempo = datetime.strptime(hasta, '%Y-%m-%d') - datetime.strptime(desde, '%Y-%m-%d')
    days = tiempo.days
    year = 0
    month = 0
    while days >= 365:
        year += 1
        days -= 365
    while days >= 30:
        month += 1
        days -= 30

    time = f"{year} years" if year > 0 else ""
    time += f" {month} months" if month > 0 else ""
    return time
from django.core.exceptions import ObjectDoesNotExist
from .models import Score, User, PermiteScore
from django.shortcuts import render
from django.contrib.auth import authenticate
from datetime import datetime

# comparar es un función que compara si hay alguna coincidencia de username, nombre, apellido o dni.
def comparar(user, name):
    # Pasamos el name a minuscula y el dni del usuario a integer.
    nombre = name.casefold()
    dni = int(user.dni)
    # Creamos una lista con los valores que vamos a chequear.
    user = [user.username.casefold(), user.nombre.casefold(), user.apellido.casefold()]
    if nombre in user:
        return True
    if nombre.isnumeric() and int(nombre) == dni:
        return True
    # Si no hay coincidencia retorna falso.
    return False


# relacion_score es una función que si el usuario del perfil le autorizó al usuario logueado que lo califique, te devuelve ese model.
def relacion_score(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(propietario=usuario_1, inquilino=usuario_2, active=True)
    except (ObjectDoesNotExist):
        permite = False
    return permite

# Corroboramos si tienen una relación activa (si el usuario_1 le permitió al usuario_2 puntuarlo pero todavìa no lo hizo)
def allowToScore(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(inquilino=usuario_1, propietario=usuario_2, active=True)
    except (ObjectDoesNotExist):
        permite = False

    # Devolvemos un booleano.
    if permite:
        allow = True
    else:
        allow = False
    return allow


# Corroboramos la contraparte (si el usuario_2 le permitió al usuario_1 puntuarlo pero todavìa no lo hizo).
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


# Corroboramos si hay una relación terminada porque el usuario_1 ya puntuó al usuario_2.
def relacion_terminada(usuario_1, usuario_2):
    try:
        permite = PermiteScore.objects.get(propietario=usuario_1, inquilino=usuario_2, active=False)
    except (ObjectDoesNotExist):
        permite = False
    return permite


# Corroboramos si el usuario_2 ya puntuó al usuario_1 y si es correcto devolvemos el valor.
def my_score(usuario_1, usuario_2):
    try:
        my_score = Score.objects.get(inquilino=usuario_1, propietario=usuario_2)
    except (ObjectDoesNotExist):
        my_score = False
    return my_score

# Corroboramos la contraparte (Si el usuario_1 ya puntuó al usuario_2) y si es correcto devolvemos el valor.
def they_score(usuario_1, usuario_2):
    try:
        my_score = Score.objects.get(propietario=usuario_1, inquilino=usuario_2)
    except (ObjectDoesNotExist):
        my_score = False
    return my_score

# Corroboramos si hay Scores y si existen devolvemos los valores.
def check_scores(usuario):
    try:
        scores = Score.objects.filter(inquilino=usuario)
    except (ObjectDoesNotExist):
        scores = False            
    return scores


# Calculamos el promedio de los scores de un usuario.
def amount_scores(scores):
    amount = 0
    for score in scores:
        amount += score.puntaje
    if amount != 0:
        average = amount / len(scores)
    else:
        average = 0
    return int(average)


# Renderizamos el perfil del usuario.
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

# Renderizamos la página de registro.
def render_register(request, message):
    return render(request, "score/register.html", {
        "message": message,
        })

def render_update(request, usuario, message):
    return render(request, "score/update.html", {
        "usuario": usuario,
        "message": message
        })

# Renderizamos la página para cambiar el password.
def render_password(request, usuario, message):
    return render(request, "score/password.html", {
        "usuario": usuario,
        "message": message
        })

# Calculamos el tiempo que hay entre la fecha que empezó el alquiler y la fecha que terminó.
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
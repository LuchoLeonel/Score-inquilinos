from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inquilinos", views.inquilinos, name="inquilinos"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("update", views.update, name="update"),
    path("changePassword", views.changePassword, name="changePassword"),
    path("buscar", views.buscar, name="buscar"),
    path("allowScore/<int:id>/<int:id_user>", views.allowScore, name="allowScore")
]
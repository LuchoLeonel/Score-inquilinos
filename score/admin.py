from django.contrib import admin

from .models import User, Score, PermiteScore

# Register your models here.
admin.site.register(User)
admin.site.register(Score)
admin.site.register(PermiteScore)

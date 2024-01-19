from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),
    path("survey", survey, name="survey"),
]

from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),
    path("survey", survey, name="survey"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
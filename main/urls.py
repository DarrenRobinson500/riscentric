from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),
    path("question_set/<id>", question_set, name="question_set"),
    path("survey/<id>", survey, name="survey"),

    path("files", files, name="files"),
    path("file_upload", file_upload, name="file_upload"),
    path("file_view/<id>", file_view, name="file_view"),
    path("file_to_db/<id>", file_to_db, name="file_to_db"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
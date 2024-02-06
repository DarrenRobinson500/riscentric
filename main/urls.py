from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),
    path("set_current_company/<id>", set_current_company, name="set_current_company"),
    path("question_set/<id>", question_set, name="question_set"),
    path("survey/<id>", survey, name="survey"),
    path("people", people, name="people"),
    path("questions", questions, name="questions"),

    path("files", files, name="files"),
    path("file_upload", file_upload, name="file_upload"),
    # path("file_view/<id>", file_view, name="file_view"),
    path("file_to_db_questions/<id>", file_to_db_questions, name="file_to_db_questions"),
    path("file_to_db_employees/<id>", file_to_db_employees, name="file_to_db_employees"),

    path("email", email, name="email"),
    path("email_send/<id>", email_send, name="email_send"),
    path("email_view", email_view, name="email_view"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
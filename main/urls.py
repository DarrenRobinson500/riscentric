from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf import settings # new
from  django.conf.urls.static import static #new

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("home", home, name="home"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),
    path("company_new", company_new, name="company_new"),
    path("company_edit", company_edit, name="company_edit"),
    path("company_delete/<id>", company_delete, name="company_delete"),
    path("set_current_company/<id>", set_current_company, name="set_current_company"),
    # path("question_set/<id>", question_set, name="question_set"),
    path("survey/<email_id>", survey, name="survey"),
    path("survey_complete/<email_id>/<answer_string>", survey_complete, name="survey_complete"),
    path("survey_admin/<email_id>/<answer_string>", survey_admin, name="survey_admin"),
    path("people", people, name="people"),
    path("questions", questions, name="questions"),
    path("pings", pings, name="pings"),
    path("ping/<id>", ping, name="ping"),
    path("ping/<id>/<company_id>", ping, name="ping"),
    path("ping_delete/<id>", ping_delete, name="ping_delete"),
    path("ping_create", ping_create, name="ping_create"),
    path("ping_save", ping_save, name="ping_save"),
    path("logic", logic, name="logic"),
    path("download", download, name="download"),
    path("download/<ping_id>", download, name="download"),

    path("files", files, name="files"),
    path("file_upload", file_upload, name="file_upload"),
    # path("file_link", file_link, name="file_link"),
    # path("view_url/<id>", view_url, name="view_url"),
    path("file_to_db/<id>", file_to_db, name="file_to_db"),
    path("change_sheet_name/<id>/<current_sheet>", change_sheet_name, name="change_sheet_name"),

    # path("file_view/<id>", file_view, name="file_view"),
    # path("file_to_db_questions/<id>", file_to_db_questions, name="file_to_db_questions"),
    # path("file_to_db_employees/<id>", file_to_db_employees, name="file_to_db_employees"),
    # path("link_to_db_questions/<id>", link_to_db_questions, name="link_to_db_questions"),
    # path("link_to_db_employees/<id>", link_to_db_employees, name="link_to_db_employees"),

    path("email", email, name="email"),
    path("email_send/<id>", email_send, name="email_send"),
    path("email_view/<id>/<admin>", email_view, name="email_view"),

    path("new/<model_str>", new, name="new"),
    path("list_view/<model_str>", list_view, name="list_view"),
    path("item/<model_str>/<id>", item, name="item"),
    path("new/<model_str>", new, name="new"),
    path("edit/<model_str>/<id>", edit, name="edit"),
    path("toggle_value/<id>/<parameter>", toggle_value, name="toggle_value"),
    path("delete/<model_str>/<id>", delete, name="delete"),
    path("development", development, name="development"),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)

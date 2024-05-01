from django.forms import *
from .models import *

class NewCompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ("name", )
        widgets = {"name": TextInput(attrs={"class": "form-control", "placeholder": ""}),}

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ("name", "colour", "colour_text", "email_subject", "email_text")
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "colour": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "colour_text": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "email_subject": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "email_text": Textarea(attrs={"class": "form-control", "placeholder": ""}),
        }

class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ("name", "type", "document")
        widgets = {
            "type": Select(attrs={"class": "form-control"}),
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "document": FileInput(attrs={"class": "form-control", "placeholder": ""}
            ),
        }

class LinkForm(ModelForm):
    class Meta:
        model = File
        fields = ("url", )
        widgets = {
            "url": TextInput(attrs={"class": "form-control", "placeholder": ""},
            ),
        }

class To_DoForm(ModelForm):
    class Meta:
        model = To_do
        fields = ("name", "priority", )
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "priority": TextInput(attrs={"class": "form-control", "placeholder": ""}),
        }


form_library = {
    To_do: To_DoForm,
}

def get_form(model):
    try:    return form_library[model]
    except: return

def get_model(model_str):
    for model in all_models:
        if model.model_name == model_str:
            return model, get_form(model)
    return None
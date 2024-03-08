from django.forms import *
from .models import *

class NewCompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ("name", )
        widgets = {"name": TextInput(attrs={"class": "form-control", "placeholder": ""}),}

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
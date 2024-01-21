from django.forms import *
from .models import *

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
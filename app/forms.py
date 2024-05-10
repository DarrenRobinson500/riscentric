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
        fields = ("name", "colour", "colour_text", "email_subject", "email_text", "thankyou_text")
        widgets = {
            "name": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "colour": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "colour_text": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "email_subject": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "email_text": Textarea(attrs={"class": "form-control", "placeholder": ""}),
            "thankyou_text": TextInput(attrs={"class": "form-control", "placeholder": ""}),
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

class LogicForm(ModelForm):
    class Meta:
        model = Logic
        fields = ("last_question", "last_answer", "next_question",)
        widgets = {
            "last_question": Select(attrs={"class": "form-control"}),
            "last_answer": TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "next_question": Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the selected company (assuming it's passed as an argument)
        the_company = kwargs.get('initial', {}).get('company')
        print("Logic Form:", the_company)

        # Filter the base_rate choices based on the selected company
        self.fields['next_question'].queryset = Question.objects.filter(company=the_company)

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
    Logic: LogicForm
}

def get_form(model):
    try:    return form_library[model]
    except: return

def get_model(model_str):
    for model in all_models:
        print(model.model_name, model_str, model.model_name == model_str)
        if model.model_name == model_str:
            print("Get model", model, get_form(model))
            return model, get_form(model)
    return None, None
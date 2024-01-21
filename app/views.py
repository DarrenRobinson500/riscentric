from django.shortcuts import render, redirect
from .forms import *

def home(request):
    responses = Response.objects.all()
    questions = Question.objects.all()
    context = {"responses": responses, 'questions': questions}
    return render(request, "home.html", context)

def survey(request):
    question_set = QuestionSet.objects.all().first()
    if request.method == "POST":
        response = Response()
        response.save()
        for key, value in request.POST.items():
            print(f"{key}: {value}")
            if key != "csrfmiddlewaretoken":
                question = Question.objects.filter(id=key).first()
                answer = value
                response_ind = ResponseInd(question=question, answer_text=answer, response=response)
                response_ind.save()
        return redirect('home')

    context = {"question_set": question_set}

    return render(request, "survey.html", context)

def files(request):
    list = File.objects.all().order_by("name").order_by("-time_stamp")
    context = {"list": list, }
    return render(request, "files.html", context)

def upload(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.type = "File for Upload"
            new_file.save()
            return redirect("files")
    else:
        form = FileForm()
    return render(request, "upload.html", {"form": form})
from django.shortcuts import render
from .models import *

def home(request):
    responses = Response.objects.all()
    context = {"responses": responses}
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

    context = {"question_set": question_set}

    return render(request, "survey.html", context)

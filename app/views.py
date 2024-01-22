from django.shortcuts import render, redirect
from .forms import *
import openpyxl as xl
import boto3
from tempfile import NamedTemporaryFile
from django.conf import settings

def files(request):
    list = File.objects.all().order_by("name").order_by("-time_stamp")
    context = {"list": list, }
    return render(request, "files.html", context)

def file_upload(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.type = "File for Upload"
            new_file.save()
            return redirect("files")
    else:
        form = FileForm()
    return render(request, "file_upload.html", {"form": form})

def load_spreadsheet_from_s3(id):
    file = File.objects.filter(id=id).first()
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    path = str(file.document.url)
    path = path[path.find("files"):path.find("xlsx") + 4]
    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource('s3')
    with NamedTemporaryFile(suffix='.xlsx') as tmp:
        s3.Bucket(bucket_name).download_file(path, tmp.name)
        workbook = xl.load_workbook(tmp.name)
    return workbook

def get_set_and_questions(id):
    wb = load_spreadsheet_from_s3(id)
    sheet = wb.active
    question_set = sheet.cell(1, 1).value
    questions = []
    for row in range(2, sheet.max_row + 1):
        question = sheet.cell(row, 1).value
        if question:
            more_choices, col, choices = True, 2, []
            while more_choices and col < 10:
                choice = sheet.cell(row, col).value
                if not choice:
                    more_choices = False
                else:
                    choices.append(choice)
                    col += 1
                print(row, col, choice)
            questions.append((question, choices))
    return question_set, questions

def file_view(request, id):
    question_set, questions = get_set_and_questions(id)
    context = {"question_set": question_set, "questions": questions, 'id': id}
    return render(request, 'file_view.html', context)

def file_to_db(request, id):
    question_set_string, questions = get_set_and_questions(id)
    question_set = QuestionSet(description=question_set_string, date=date.today())
    question_set.save()
    for question, choices in questions:
        # choices = ['yes', 'no', 'maybe']
        choices_string = ','.join(choices)
        Question(question_set=question_set, question=question, choices=choices_string).save()
    return redirect('home')

def home(request):
    responses = Response.objects.all()
    questions = Question.objects.all()
    question_sets = QuestionSet.objects.all()
    context = {"responses": responses, 'questions': questions, 'question_sets': question_sets}
    return render(request, "home.html", context)

def question_set(request, id):
    question_set = QuestionSet.objects.get(id=id)
    context = {'question_set': question_set}
    return render(request, "question_set.html", context)

def survey(request, id):
    question_set = QuestionSet.objects.get(id=id)
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



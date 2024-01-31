from django.shortcuts import render, redirect
import openpyxl as xl
import boto3
from tempfile import NamedTemporaryFile
from django.conf import settings

from .forms import *
from .emails import *

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

def file_to_db_employees(request, id):
    wb = load_spreadsheet_from_s3(id)
    sheet = wb.active
    name = sheet.cell(1, 1).value
    company = Company(name=name)
    company.save()
    for row in range(3, sheet.max_row + 1):
        firstname = sheet.cell(row, 1).value
        surname = sheet.cell(row, 2).value
        email = sheet.cell(row, 3).value
        area = sheet.cell(row, 4).value
        Person(company=company, firstname=firstname, surname=surname, email=email, area=area).save()
    return redirect(f'company/{company.id}')

def file_to_db_questions(request, id):
    wb = load_spreadsheet_from_s3(id)
    sheet = wb.active
    name = sheet.cell(1, 1).value
    existing = QuestionSet.objects.filter(name=name)
    if len(existing) == 0:
        question_set = QuestionSet(name=name, date=date.today())
    else:
        question_set = existing.first()
    question_set.save()
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
            choices_string = ','.join(choices)
            existing = Question.objects.filter(question_set=question_set, question=question)
            if len(existing) == 0:
                Question(question_set=question_set, question=question, choices=choices_string).save()
    return redirect('home')

def file_view(request, id):
    question_set, questions = get_set_and_questions(id)
    context = {"question_set": question_set, "questions": questions, 'id': id}
    return render(request, 'file_view.html', context)

def home(request, id):
    companies = Company.objects.all()
    context = {'companies': companies}
    return render(request, "question_sets.html", context)

def company_view(request, id):
    company = Company.objects.get(id=id)
    context = {'company': company}
    return render(request, "company_view.html", context)

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

def email(request):
    context = {}
    return render(request, "email.html", context)

def email_send(request):
    question_set = QuestionSet.objects.all().first()
    context_email = {"question_set": question_set}
    send_email_logic(context_email)
    context = {}
    return render(request, "email.html", context)

def email_view(request):
    question_set = QuestionSet.objects.all().first()
    context = {"question_set": question_set}
    return render(request, "email_template.html", context)

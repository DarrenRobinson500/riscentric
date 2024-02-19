from django.shortcuts import render, redirect
import openpyxl as xl
import boto3
from tempfile import NamedTemporaryFile
from django.conf import settings

from .forms import *
from .emails import *

def files(request):
    general = General.objects.all().first()
    context = {"company": general.company}
    return render(request, "files.html", context)

def file_upload(request):
    general = General.objects.all().first()
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.company = general.company
            new_file.save()
            print("Saved:", new_file, general.company, new_file.company)
            return redirect("files")
    else:
        form = FileForm()
    return render(request, "file_upload.html", {"form": form, 'company': general.company})

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
    general = General.objects.all().first()

    for row in range(3, sheet.max_row + 1):
        firstname = sheet.cell(row, 1).value
        surname = sheet.cell(row, 2).value
        email = sheet.cell(row, 3).value
        area = sheet.cell(row, 4).value
        Person(company=general.company, firstname=firstname, surname=surname, email=email, area=area).save()
    return redirect(f'home')

def file_to_db_questions(request, id):
    general = General.objects.all().first()
    wb = load_spreadsheet_from_s3(id)
    sheet = wb.active
    name = sheet.cell(1, 1).value
    existing = QuestionSet.objects.filter(name=name)
    if len(existing) == 0:
        question_set = QuestionSet(name=name, date=date.today(), company=general.company)
    else:
        question_set = existing.first()
    question_set.save()
    for row in range(2, sheet.max_row + 1):
        question = sheet.cell(row, 1).value
        if question:
            scheduled_date = sheet.cell(row, 2).value
            more_choices, col, choices = True, 3, []
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
                Question(question_set=question_set, schedule_date=scheduled_date, question=question, choices=choices_string).save()
    return redirect('questions')

def file_view(request, id):
    general = General.objects.all().first()
    question_set, questions = get_set_and_questions(id)
    context = {"question_set": question_set, "questions": questions, 'id': id, 'company': general.company}
    return render(request, 'file_view.html', context)

def home(request):
    general = General.objects.all().first()
    general.company = None
    general.save()
    companies = Company.objects.all()
    context = {'companies': companies, 'company': general.company}
    return render(request, "home.html", context)

def set_current_company(request, id):
    general = General.objects.all().first()
    general.company = Company.objects.get(id=id)
    general.save()
    return redirect('questions')

def questions(request):
    general = General.objects.all().first()
    context = {'company': general.company}
    return render(request, "questions.html", context)

def question_set(request, id):
    general = General.objects.all().first()
    question_set = QuestionSet.objects.get(id=id)
    context = {'question_set': question_set, 'company': general.company}
    return render(request, "question_set.html", context)

def people(request):
    general = General.objects.all().first()
    context = {'company': general.company}
    return render(request, "people.html", context)

def survey(request, email_id):
    general = General.objects.all().first()
    email = Email.objects.get(id=email_id)
    person = email.person
    question = email.question
    print("Survey person:", person)
    print("Survey question:", question)
    context = {"email": email, 'company': general.company}
    return render(request, "survey.html", context)

def survey_complete(request, email_id, answer_string):
    email = Email.objects.get(id=email_id)
    email.answer = answer_string
    email.save()
    context = {"email": email, 'company': email.person.company}
    return render(request, "survey_complete.html", context)

def email(request):
    general = General.objects.all().first()
    context = {'company': general.company}
    return render(request, "email.html", context)

def email_send(request, id):
    # general = General.objects.all().first()
    question = Question.objects.get(id=id)
    person = question.question_set.company.people().first()
    send_email_logic(question, question.question_set.company.people())
    context = {'company': person.company, 'person': person, 'question': question}
    return render(request, "email_template.html", context)

def email_view(request, id):
    general = General.objects.all().first()
    question = Question.objects.get(id=id)
    context = {"question": question, 'company': general.company}
    return render(request, "email_view.html", context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import openpyxl as xl
import boto3
from tempfile import NamedTemporaryFile
from django.conf import settings
import io
import pandas as pd
# from office365.sharepoint.file import File
from pandas import ExcelWriter
from django.http import HttpResponse

from .forms import *
from .emails import *
from .excel import *
from .df_formats import *

# --------------------
# ------ HOME ---------
# --------------------

def home(request):
    if not request.user.is_authenticated: return redirect("login")
    riscentric = Company.objects.filter(name="Riscentric").first()
    general = General.objects.all().first()
    if not general:
        general = General(name="main")
    general.company = riscentric
    general.save()
    companies = Company.objects.exclude(name="Riscentric").order_by("name")
    context = {'companies': companies, 'company': general.company}
    return render(request, "home.html", context)

def set_current_company(request, id):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    general.company = Company.objects.get(id=id)
    general.save()
    if len(general.company.pings()) > 0:
        return redirect('pings')
    return redirect('files')

# -----------------------------
# --------AUTHENTICATION=------
# -----------------------------

def login_user(request):
    if request.user.is_authenticated: return redirect("home")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ("Error logging in."))
            return redirect('login')
    else:
        context = {}
        return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect("login")

# -----------------------
# ---- New Company ------
# -----------------------

def company_new(request):
    if not request.user.is_authenticated: return redirect("login")
    riscentric = Company.objects.filter(name="Riscentric").first()
    general = General.objects.all().first()
    general.company = riscentric
    general.save()
    form = NewCompanyForm()
    print("method:", request.method)
    if request.method == "POST":
        form = NewCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
        else:
            for key, string in form.errors.items():
                print(key, string)
    context = {"form": form, "company": general.company}
    return render(request, "new_company.html", context)

def company_delete(request, id):
    if not request.user.is_authenticated: return redirect("login")
    company = Company.objects.get(id=id)
    company.delete()
    return redirect('home')

# ---------------------
# ---- Utilities ------
# ---------------------

def download(request, ping_id=None):
    if not request.user.is_authenticated: return redirect("login")

    writer = ExcelWriter('Responses.xlsx', engine='xlsxwriter')

    model = Person_Question
    print("Saving:", model)

    general = General.objects.all().first()

    if ping_id:
        ping = Ping.objects.get(id=ping_id)
        data = model.objects.filter(company=general.company, ping=ping)
    else:
        data = model.objects.filter(company=general.company)

    df = pd.DataFrame(list(data.values()))

    company = df.apply(get_company, axis=1)
    ping = df.apply(get_ping, axis=1)
    person = df.apply(get_person, axis=1)
    area = df.apply(get_area, axis=1)
    question = df.apply(get_question, axis=1)
    df = pd.concat([company, ping, person, area, question, df], axis=1)

    today = datetime.today()
    df.to_excel(writer, sheet_name=f'{today.date()}', index=False)
    writer.close()

    # Create an HttpResponse object with the Excel file
    response = HttpResponse(open('Responses.xlsx', 'rb').read(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Responses.xlsx"'

    return response

def get_company(row):
    try: return Company.objects.get(id=row['company_id']).name
    except: return ""
def get_ping(row):
    try: return Ping.objects.get(id=row['ping_id']).name
    except: return ""
def get_person(row):
    try: return Person.objects.get(id=row['person_id']).email_address
    except: return ""
def get_area(row):
    try: return Person.objects.get(id=row['person_id']).area
    except: return ""
def get_question(row):
    try: return Question.objects.get(id=row['question_id']).question
    except: return ""

# ---------------------
# ---- People ------
# ---------------------

def people(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    people = Person.objects.filter(company=general.company)
    context = {'company': general.company, 'people': people}
    return render(request, "people.html", context)

# ---------------------
# ---- Questions ------
# ---------------------

def questions(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    questions = Question.objects.filter(company=general.company)
    context = {'company': general.company, 'questions': questions}
    return render(request, "questions.html", context)

# -----------------
# ---- Pings ------
# -----------------

def pings(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    pings = Ping.objects.filter(company=general.company).order_by('name')
    context = {'pings': pings, 'company': general.company}
    return render(request, "pings.html", context)

def ping(request, id, company_id=None):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()

    if company_id:
        general.company = Company.objects.get(id=id)
        general.save()
        general = General.objects.all().first()

    ping = Ping.objects.get(id=id)
    context = {'ping': ping, 'company': general.company}
    return render(request, "ping.html", context)

def ping_delete(request, id):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    ping = Ping.objects.get(id=id)
    ping.delete()
    return redirect('pings')

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
    general = General.objects.all().first()
    email = Email.objects.get(id=email_id)
    email.answer = answer_string
    email.save()
    email.person_question.answer = answer_string
    email.person_question.save()

    context = {"email": email, 'company': general.company}
    return render(request, "survey_complete.html", context)

def survey_admin(request, email_id, answer_string):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    email = Email.objects.get(id=email_id)
    email.answer = answer_string
    email.save()
    email.person_question.answer = answer_string
    email.person_question.save()

    context = {"email": email, 'company': general.company}
    return redirect('email_view', email.ping.id, "True")

# -----------------
# ---- Emails ------
# -----------------

def email(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    context = {'company': general.company}
    return render(request, "email.html", context)

def email_send(request, id):
    if not request.user.is_authenticated: return redirect("login")
    # general = General.objects.all().first()
    ping = Ping.objects.get(id=id)
    send_email_logic(ping)
    person_question = ping.person_questions().first()
    context = {'company': ping.company, 'person': person_question.person, 'question': person_question.question, 'email': person_question.emails().first()}
    return render(request, "email_template.html", context)

def email_view(request, id, admin):
    if not request.user.is_authenticated: return redirect("login")
    if admin == "True": admin = True
    else: admin = False
    general = General.objects.all().first()
    ping = Ping.objects.get(id=id)
    context = {"ping": ping, 'company': general.company, "admin": admin}
    return render(request, "email_view.html", context)



# ---------------------------
# ---- File Management ------
# ---------------------------

def files(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    companies = Company.objects.all()
    for company in companies:
        print()
        print(company)
        for files in company.files():
            print(file)


    context = {"company": general.company}
    return render(request, "files.html", context)

def file_upload(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.company = general.company
            new_file.save()
            print("Saved File:", new_file, general.company, new_file.company)
            return redirect("files")
    else:
        form = FileForm()
    return render(request, "file_upload.html", {"form": form, 'company': general.company})

def view_url(request, id):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    file = File.objects.filter(id=id).first()
    print("Getting DFs from Link")
    df_people, df_questions, df_pings = dfs_from_link(file.url)

    print("Converting DFs to HTML")
    df_people_html = df_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
    df_questions_html = df_questions.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
    df_pings_html = df_pings.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load people into DB and create HTML
    print("Loading people into DB")
    df_to_db_employee(df_people)
    db_people = Person.objects.filter(company=general.company)
    db_people = pd.DataFrame.from_records(db_people.values())
    db_people_html = db_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load questions into DB and create HTML
    print("Loading questions into DB")
    df_to_db_questions(df_questions)
    db_questions = Question.objects.filter(company=general.company)
    db_questions = pd.DataFrame.from_records(db_questions.values())
    db_questions_html = db_questions.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load pings into DB and create HTML
    print("Loading pings into DB")
    df_to_db_pings(df_pings)
    db_pings = Person_Question.objects.filter(company=general.company)
    db_pings = pd.DataFrame.from_records(db_pings.values())
    db_pings['company_id'] = db_pings['company_id'].map(company_names)
    db_pings['ping_id'] = db_pings['ping_id'].map(ping_names)
    db_pings['person_id'] = db_pings['person_id'].map(people_names)
    db_pings['question_id'] = db_pings['question_id'].map(question_names)
    db_pings_html = db_pings.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    data_set = [("People", df_people_html, db_people_html), ("Questions", df_questions_html, db_questions_html), ("Pings", df_pings_html, db_pings_html)]

    print("Creating HTML")
    context = {"company": general.company, 'data_set': data_set, 'file': file}
    return render(request, "view_url.html", context)

def file_to_db_all(request, id):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    file = File.objects.filter(id=id).first()
    print("Getting DFs from Link")
    df_people, df_questions, df_pings = dfs_from_file(file.document)

    print("Converting DFs to HTML")
    df_people_html = df_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
    df_questions_html = df_questions.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
    df_pings_html = df_pings.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load people into DB and create HTML
    print("Loading people into DB")
    df_to_db_employee(df_people)
    db_people = Person.objects.filter(company=general.company)
    db_people = pd.DataFrame.from_records(db_people.values())
    db_people_html = db_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load questions into DB and create HTML
    print("Loading questions into DB")
    df_to_db_questions(df_questions)
    db_questions = Question.objects.filter(company=general.company)
    db_questions = pd.DataFrame.from_records(db_questions.values())
    db_questions_html = db_questions.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    # Load pings into DB and create HTML
    print("Loading pings into DB")
    df_to_db_pings(df_pings)
    db_pings = Person_Question.objects.filter(company=general.company)
    db_pings = pd.DataFrame.from_records(db_pings.values())
    db_pings['company_id'] = db_pings['company_id'].map(company_names)
    db_pings['ping_id'] = db_pings['ping_id'].map(ping_names)
    db_pings['person_id'] = db_pings['person_id'].map(people_names)
    db_pings['question_id'] = db_pings['question_id'].map(question_names)
    db_pings_html = db_pings.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)

    data_set = [("People", df_people_html, db_people_html), ("Questions", df_questions_html, db_questions_html), ("Pings", df_pings_html, db_pings_html)]

    print("Creating HTML")
    context = {"company": general.company, 'data_set': data_set, 'file': file}
    return render(request, "view_url.html", context)


def file_link(request):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    if request.method == "POST":
        form = LinkForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.company = general.company
            new_file.save()
            print("Saved Link:", new_file, general.company, new_file.company)
            return redirect("files")
    else:
        form = LinkForm()
    return render(request, "file_link.html", {"form": form, 'company': general.company})

# def link_to_db_employees(request, id):
#     file = File.objects.filter(id=id).first()
#     wb = excel_from_link(file.url)
#     spreadsheet_to_db_employee(wb)
#     return redirect('people')

# def spreadsheet_to_db_employee(wb):
#     sheet = wb.active
#     general = General.objects.all().first()
#
#     for row in range(2, sheet.max_row + 1):
#         firstname = sheet.cell(row, 1).value
#         surname = sheet.cell(row, 2).value
#         email_address = sheet.cell(row, 3).value
#         area = sheet.cell(row, 4).value
#         if not Person.objects.filter(column_name=email_address).exists():
#             print("Adding:", firstname, surname, email, area)
#             Person(company=general.company, firstname=firstname, surname=surname, email_address=email_address, area=area).save()
#         else:
#             print("Already exists:", firstname, surname, email, area)
#
#
# def link_to_db_questions(request, id):
#     file = File.objects.filter(id=id).first()
#     wb = excel_from_link(file.url)
#     spreadsheet_to_db_questions(wb)
#     return redirect('questions')
#
# def spreadsheet_to_db_questions(wb):
#     general = General.objects.all().first()
#     sheet = wb.active
#     name = sheet.cell(1, 1).value
#     existing = QuestionSet.objects.filter(name=name)
#     if len(existing) == 0:
#         question_set = QuestionSet(name=name, date=date.today(), company=general.company)
#     else:
#         question_set = existing.first()
#     question_set.save()
#     for row in range(2, sheet.max_row + 1):
#         question = sheet.cell(row, 1).value
#         if question:
#             scheduled_date = sheet.cell(row, 2).value
#             more_choices, col, choices = True, 3, []
#             while more_choices and col < 10:
#                 choice = sheet.cell(row, col).value
#                 if not choice:
#                     more_choices = False
#                 else:
#                     choices.append(choice)
#                     col += 1
#             choices_string = ','.join(choices)
#             existing = Question.objects.filter(question_set=question_set, question=question)
#             if len(existing) == 0:
#                 Question(question_set=question_set, schedule_date=scheduled_date, question=question, choices=choices_string).save()


# ------------------------------
# ------ TO BE DELETED ---------
# ------------------------------

# def load_spreadsheet_from_s3(id):
#     file = File.objects.filter(id=id).first()
#     bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     path = str(file.document.url)
#     path = path[path.find("files"):path.find("xlsx") + 4]
#     session = boto3.Session(
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     )
#     s3 = session.resource('s3')
#     with NamedTemporaryFile(suffix='.xlsx') as tmp:
#         s3.Bucket(bucket_name).download_file(path, tmp.name)
#         workbook = xl.load_workbook(tmp.name)
#     return workbook
#
# def file_to_db_employees(request, id):
#     # wb = load_spreadsheet_from_s3(id)
#     file = File.objects.filter(id=id).first()
#     path = file.document.path
#     wb = xl.load_workbook(path)
#     spreadsheet_to_db_employee(wb)
#     return redirect(f'people')
#
# def file_to_db_questions(request, id):
#     general = General.objects.all().first()
#     # wb = load_spreadsheet_from_s3(id)
#     file = File.objects.filter(id=id).first()
#     path = file.document.path
#     wb = xl.load_workbook(path)
#     spreadsheet_to_db_questions(wb)
#     return redirect('questions')
#
# def file_view(request, id):
#     general = General.objects.all().first()
#     question_set, questions = get_set_and_questions(id)
#     context = {"question_set": question_set, "questions": questions, 'id': id, 'company': general.company}
#     return render(request, 'file_view.html', context)

# def get_spreadsheet_data(file):
#
#     # Replace with your OneDrive file URL
#     file_url = 'https://onedrive.com/yourfile.xlsx'
#
#     # Read the file into a pandas DataFrame
#     response = File.open_binary(ctx, file_url)
#     bytes_file_obj = io.BytesIO()
#     bytes_file_obj.write(response.content)
#     bytes_file_obj.seek(0)
#     df = pd.read_excel(bytes_file_obj)
#
#     print(df)

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
from .email_microsoft_test import *

# --------------------
# ------ HOME ---------
# --------------------

def home(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    companies = Company.objects.exclude(name="Riscentric").order_by("name")
    context = {'companies': companies, 'company': company, }
    return render(request, "home.html", context)

def set_current_company(request, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    user.company = Company.objects.get(id=id)
    user.save()
    # if len(user.company.pings()) > 0:
    #     return redirect('pings')
    return redirect('company_edit')

# -----------------------------
# --------AUTHENTICATION=------
# -----------------------------

def get_user(request):
    user = CustomUser.objects.filter(user=request.user).first()
    if not user:
        user = CustomUser(user=request.user)
        user.save()
    if not user.company:
        user.company = Company.objects.filter(name="Riscentric").first()
    if not user.company:
        default = Company(name="Riscentric")
        default.save()
        user.company = default
        user.save()

    return user, user.company

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

# -------------------
# ---- Company ------
# -------------------

def company_new(request):
    if not request.user.is_authenticated: return redirect("login")
    riscentric = Company.objects.filter(name="Riscentric").first()
    general = General.objects.all().first()
    if general is None:
        general = General(name="main")
        general.save()
    else:
        print(general)
    company = riscentric
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
    context = {"form": form, "company": company}
    return render(request, "company_new.html", context)

def company_delete(request, id):
    if not request.user.is_authenticated: return redirect("login")
    company = Company.objects.get(id=id)
    company.delete()
    return redirect('home')

def company_edit(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    form = CompanyForm(instance=company)
    if request.method == "POST":
        form = CompanyForm(request.POST or None, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_edit")
    context = {"form": form, "company": company}
    return render(request, "company_edit.html", context)

def company_activate(request, id):
    company = Company.objects.get(id=id)
    company.active = not company.active
    company.save()
    return redirect("home")

# ---------------------
# ---- Utilities ------
# ---------------------

def download(request, ping_id=None):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)

    writer = ExcelWriter('Responses.xlsx', engine='xlsxwriter')

    model = Person_Question

    if ping_id:
        ping = Ping.objects.get(id=ping_id)
        data = model.objects.filter(company=company, ping=ping)
    else:
        data = model.objects.filter(company=company)

    df = pd.DataFrame(list(data.values()))

    company = df.apply(get_company, axis=1)
    print(type(company))
    ping = df.apply(get_ping, axis=1)
    person = df.apply(get_person, axis=1)
    area = df.apply(get_area, axis=1)
    question = df.apply(get_question, axis=1)
    send_date = df.apply(get_send_date, axis=1)
    answer_date = df.apply(get_answer_date, axis=1)
    # df.columns = ['Company', 'Ping', 'Email', 'Area']
    df = pd.concat([company, ping, person, area, question, df, send_date, answer_date], axis=1)
    df.rename(columns={0: 'Company', 1: 'Ping', 2: 'Email', 3: 'Team', 4: 'Question', 5: 'Send Date', 6: 'Answer Date'}, inplace=True)
    print("df.columns")
    print(df.columns)
    if 'answer_date' in df.columns: del df['answer_date']
    if 'send_date' in df.columns: del df['send_date']

    today = datetime.today().strftime("%B %d, %Y") + "X"
    df.to_excel(writer, sheet_name=f'{today}', index=False)
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
def get_answer_date(row):
    try:
        date_string = row['answer_date'].strftime('%Y-%m-%d %H:%M:%S')
        print(type(date_string))
        return date_string
    except:
        return ""
def get_send_date(row):
    try:
        date_string = row['send_date'].strftime('%Y-%m-%d %H:%M:%S')
        print(type(date_string))
        return date_string
    except:
        return ""

# ---------------------
# ---- People ------
# ---------------------

def people(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    people = Person.objects.filter(company=company)
    context = {'company': company, 'people': people}
    return render(request, "people.html", context)

# ---------------------
# ---- Questions ------
# ---------------------

def questions(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    # questions = Question.objects.filter(company=company)
    context = {'company': company}
    return render(request, "questions.html", context)

# -----------------
# ---- Pings ------
# -----------------

def pings(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    pings = Ping.objects.filter(company=company).order_by('number')
    print("Pings", pings)
    context = {'pings': pings, 'company': company}
    return render(request, "pings.html", context)

def ping(request, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    ping = Ping.objects.get(id=id)
    context = {'ping': ping, 'company': company}
    return render(request, "ping.html", context)

def ping_delete(request, id):
    if not request.user.is_authenticated: return redirect("login")
    general = General.objects.all().first()
    ping = Ping.objects.get(id=id)
    ping.delete()
    return redirect('pings')

def ping_create(request, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    ping = Ping.objects.get(id=id)
    context = {'company': company, 'ping': ping}
    return render(request, "ping_create.html", context)

def ping_save(request, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    last_ping = Ping.objects.get(id=id)
    print("Ping Save:", last_ping)
    number = last_ping.number + 1
    name = f"Round {number}"
    ping = Ping(name=name, company=company, number=number)
    ping.save()
    for person_question in last_ping.person_questions():
        logic = person_question.next_question_logic()
        if logic:
            print("Ping Save:", person_question)
            Person_Question(company=company, ping=ping, person=person_question.person, question=logic.next_question).save()
        else:
            print("Ping Save - No logic")
    return redirect('pings')

def survey(request, email_id):
    # user, company = get_user(request)
    email = Email.objects.get(id=email_id)
    company = email.company
    person = email.person
    question = email.question
    person_question = email.person_question
    person_question.viewed = True
    if person_question.answer == "None": person_question.answer = "Viewed"
    person_question.save()
    # print("Survey person:", person)
    # print("Survey question:", question)
    context = {"email": email, 'company': company}
    return render(request, "survey.html", context)

def survey_complete(request, email_id, answer_string):
    email = Email.objects.get(id=email_id)
    email.answer = answer_string
    email.answer_date = datetime.now()
    email.save()
    email.person_question.answer = answer_string
    email.person_question.answer_date = datetime.now()
    email.person_question.save()

    context = {"email": email, 'company': email.company}
    return render(request, "survey_complete.html", context)

def survey_admin(request, email_id, answer_string):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    email = Email.objects.get(id=email_id)
    if answer_string == "None": answer_string = None
    email.answer = answer_string
    email.answer_date = datetime.now()
    email.save()
    email.person_question.answer = answer_string
    email.person_question.answer_date = datetime.now()
    email.person_question.save()

    context = {"email": email, 'company': company}
    return redirect('email_view', email.ping.id, "True")

# -----------------
# ---- Logic ------
# -----------------

def logic(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    context = {'company': company}
    return render(request, "logic.html", context)

# -----------------
# ---- Emails ------
# -----------------

def email(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    context = {'company': company}
    return render(request, "email.html", context)

def email_send(request, id):
    if not request.user.is_authenticated: return redirect("login")
    ping = Ping.objects.get(id=id)
    email_send_logic(ping)
    return redirect('email_view', ping.id, False)

def email_send_ind(request, id):
    if not request.user.is_authenticated: return redirect("login")
    person_question = Person_Question.objects.get(id=id)
    ping = person_question.ping
    email_send_ind_logic(person_question)
    return redirect('ping', ping.id)

def email_resend(request, id):
    if not request.user.is_authenticated: return redirect("login")
    email = Email.objects.get(id=id)
    email_resend_logic(email)
    return redirect('email_view', email.ping.id, False)

def email_resend_multi(request, id):
    if not request.user.is_authenticated: return redirect("login")
    ping = Ping.objects.get(id=id)
    person_questions = Person_Question.objects.filter(ping=ping, send_date__isnull=True)
    for person_question in person_questions:
        email_send_ind_logic(person_question)
    #
    # email = Email.objects.get(id=id)
    # email_resend_logic(email)
    return redirect('ping', ping.id)

def email_view(request, id, admin):
    if not request.user.is_authenticated: return redirect("login")
    if admin == "True": admin = True
    else: admin = False
    user, company = get_user(request)
    ping = Ping.objects.get(id=id)
    context = {"ping": ping, 'company': company, "admin": admin}
    return render(request, "email_view.html", context)

# ------------------------
# ---- Final Emails ------
# ------------------------

def final_email_1(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    people = Person.objects.filter(company=company)
    answered = 0
    for person in people:
        if person.has_answered_r(): answered += 1
    message = f"{answered} of {len(people)} people have responded."
    context = {'company': company, 'people': people, "message": message}
    return render(request, "final_email_1.html", context)

def final_email_2_send_ind(request, id):
    if not request.user.is_authenticated: return redirect("login")
    person = Person.objects.get(id=id)
    email = email_send_review_logic(person)
    questions = Question.objects.filter(company=person.company, ref="R")
    for question in questions:
        print(f"Adding question '{question}' to '{person}")
        existing = Person_Question_R.objects.filter(company=person.company, person=person, question=question)
        if not existing:
            free_text = False
            if question.choices == "Free Text": free_text = True
            Person_Question_R(company=person.company, person=person, question=question, email=email, free_text=free_text, send_date=datetime.now().date()).save()
    return redirect('final_email_1')

def final_email_3_survey(request, id):
    print("Final email 3")
    email = Email_r.objects.get(id=id)
    if request.method == "POST":
        person_question = Person_Question_R.objects.filter(email=email, free_text=True).first()
        print("Person question:", person_question)
        form = FreeTextForm(request.POST, instance=person_question)
        if form.is_valid():
            print("Saved form")
            form.save()
            context = {"email": email, 'company': email.company}
            return render(request, "final_email_5_thank_you.html", context)
    person_question = email.person.next_question_r()
    if not person_question:
        context = {"email": email, 'company': email.company}
        return render(request, "final_email_5_thank_you.html", context)
    person_question.answer = ""
    person_question.save()
    form = FreeTextForm(instance=person_question)

    context = {"form": form, "company": email.company, "email": email, "person": email.person, "person_question": person_question}

    return render(request, "final_email_3_survey.html", context)

def final_email_4_answer(request, person_question_id, answer_string):
    print("Final email 4")
    person_question = Person_Question_R.objects.get(id=person_question_id)
    person_question.answer = answer_string
    person_question.answer_date = datetime.now()
    person_question.save()
    email = person_question.email
    email.answer = answer_string
    email.save()
    person_question.save()

    next_question = person_question.person.next_question_r()
    if next_question:
        return redirect("final_email_3_survey", email.id)
    else:
        context = {"email": email, 'company': email.company}
        return render(request, "final_email_5_thank_you.html", context)

def download_r(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    writer = ExcelWriter('Responses_r.xlsx', engine='xlsxwriter')

    model = Person_Question_R
    data = model.objects.filter(company=company)
    df = pd.DataFrame(list(data.values()))

    company = df.apply(get_company, axis=1)
    person = df.apply(get_person, axis=1)
    area = df.apply(get_area, axis=1)
    question = df.apply(get_question, axis=1)
    send_date = df.apply(get_send_date, axis=1)
    answer_date = df.apply(get_answer_date, axis=1)
    df = pd.concat([company, person, area, question, df, send_date, answer_date], axis=1)
    df.rename(columns={0: 'Company', 1: 'Email', 2: 'Area', 3: 'Question', 4: 'Send Date', 5: 'Answer Date'}, inplace=True)
    if 'answer_date' in df.columns: del df['answer_date']
    if 'send_date' in df.columns: del df['send_date']

    today = datetime.today().strftime("%B %d, %Y") + "X"
    df.to_excel(writer, sheet_name=f'{today}', index=False)
    writer.close()

    # Create an HttpResponse object with the Excel file
    response = HttpResponse(open('Responses_r.xlsx', 'rb').read(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Responses_r.xlsx"'

    return response

# ---------------------------
# ---- File Management ------
# ---------------------------

def files(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)

    context = {"company": company}
    return render(request, "files.html", context)

def file_upload(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            new_file.company = company
            new_file.save()
            print("Saved File:", new_file, company, new_file.company)
            return redirect("files")
    else:
        form = FileForm()
    return render(request, "file_upload.html", {"form": form, 'company': company})

def file_to_db(request, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    file_object = File.objects.filter(id=id).first()
    file = file_object.document
    data_set = []
    if "People" in file_object.type:
        df_people = pd.read_excel(file, sheet_name="People")
        # df_people_html = df_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        df_to_db_people(df_people, company)
        db_people = Person.objects.filter(company=company)
        db_people = pd.DataFrame.from_records(db_people.values())
        db_people['company_id'] = db_people['company_id'].map(company_names)
        db_people_html = db_people.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        data_set.append(("People", file_object.html_people, db_people_html))

    if "Questions" in file_object.type:
        df_questions = pd.read_excel(file, sheet_name="Questions")
        df_to_db_questions(df_questions, company)
        db = Question.objects.filter(company=company)
        db = pd.DataFrame.from_records(db.values())
        db = db.sort_values(by=['ref'])
        db = convert_id_to_string(db)
        db_questions_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        data_set.append(("Questions", file_object.html_questions, db_questions_html))

    if "Pings" in file_object.type:
        df_pings = pd.read_excel(file, sheet_name="Pings")
        df_to_db_pings(df_pings, company)
        db = Person_Question.objects.filter(company=company)
        db = pd.DataFrame.from_records(db.values())
        db = convert_id_to_string(db)
        db_pings_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        data_set.append(("Pings", file_object.html_pings, db_pings_html))

    if "Logic" in file_object.type:
        df = pd.read_excel(file, sheet_name="Logic")
        df_to_db_logic(df, company)
        db = Logic.objects.filter(company=company)
        db = pd.DataFrame.from_records(db.values())
        db = convert_id_to_string(db)
        db_html = db.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        data_set.append(("Logic", file_object.html_logic, db_html))

    context = {"company": company, 'data_set': data_set, 'file': file}
    return render(request, "file_to_db.html", context)

def convert_id_to_string(df):
    foreign_keys = [
        ('company_id', company_names),
        ('person_id', people_names),
        ('ping_id', ping_names),
        ('question_id', question_names),
        ('last_question_id', question_names),
        ('next_question_id', question_names), ]
    for name_string, map_name in foreign_keys:
        if name_string in df.columns:
            df[name_string] = df[name_string].map(map_name)
    return df

def change_sheet_name(request, id, current_sheet):
    file = File.objects.get(id=id)
    file.rename_sheet(current_sheet)
    return redirect("files")

# -----------------------
# ---- Development ------
# -----------------------

def development(request):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    items = To_do.objects.all()
    model_str = "to_do"
    context = {'company': company, 'items': items, 'model_str': model_str}
    return render(request, "to_do.html", context)

def toggle_value(request, id, parameter):
    to_do = To_do.objects.get(id=id)
    if parameter == "open": to_do.open = not to_do.open
    if parameter == "priority_down": to_do.priority = max(to_do.priority - 1, 1)
    if parameter == "priority_up": to_do.priority = to_do.priority + 1
    if parameter == "owner":
        if to_do.owner == "Darren": to_do.owner = "Simone"
        else: to_do.owner = "Darren"
    to_do.save()
    return redirect('list_view', 'to_do')


# ------------------------------
# ---- Generic Functions  ------
# ------------------------------

def list_view(request, model_str):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    model, form = get_model(model_str)
    items = model.objects.all()
    if model_str == "to_do":
        items = items.order_by('priority', 'name')
    context = {'company': company, 'items': items, 'model_str': model_str, }
    return render(request, model_str + "s.html", context)

def item(request, model_str, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    context = {'company': company, 'item': item, 'model_str': model_str, }
    return render(request, model_str + ".html", context)

def new(request, model_str):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    model, form = get_model(model_str)
    if request.method == 'POST':
        if model_str == "logic":
            form = form(request.POST, company=company)
        else:
            form = form(request.POST)
        if form.is_valid():
            new = form.save()
            if model_str == "period": new.create_files()
            return redirect('list_view', model_str)
    if model_str == "logic":
        form = form(company=company)
    else:
        form = form()
    context = {'company': company, 'form':form, 'model_str': model_str, 'mode': 'New'}
    return render(request, 'new.html', context)

def edit(request, model_str, id):
    if not request.user.is_authenticated: return redirect("login")
    user, company = get_user(request)
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    if request.method == 'POST':
        if model_str == "logic":
            form = form(request.POST or None, instance=item, initial={'company': company})
        else:
            form = form(request.POST or None, instance=item)
        if form.is_valid():
            new = form.save()
            if model_str == "period":
                new.create_file()
            if model_str == "logic":
                return redirect('logic')
            return redirect('list_view', model_str)
    form = form(instance=item, initial={'company': company})
    context = {'company': company, 'form':form, 'model_str': model_str, 'mode': 'Edit'}
    return render(request, 'new.html', context)

def delete(request, model_str, id):
    model, form = get_model(model_str)
    item = model.objects.get(id=id)
    if item: item.delete()
    return redirect("list_view", model_str)

def delete_all(request, model_str):
    model, form = get_model(model_str)
    user, company = get_user(request)
    items = model.objects.filter(company=company)
    items.delete()
    if model_str == "logic":
        return redirect("logic")
    return redirect("home")

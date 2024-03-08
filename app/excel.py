import io
import pandas as pd
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files import file

import base64
import io
import urllib.request
from openpyxl import load_workbook

from .models import *

def create_onedrive_directdownload(onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/', '_').replace('+', '-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

def dfs_from_link(url):
    onedrive_direct_link = create_onedrive_directdownload(url)
    file = urllib.request.urlopen(onedrive_direct_link).read()

    df_people = pd.read_excel(io.BytesIO(file), sheet_name="People")
    df_questions = pd.read_excel(io.BytesIO(file), sheet_name="Questions")
    df_pings = pd.read_excel(io.BytesIO(file), sheet_name="Pings")

    return df_people, df_questions, df_pings

def df_to_db_employee(df):
    general = General.objects.all().first()
    for index, row in df.iterrows():
        if not Person.objects.filter(company=general.company, email_address=row['email']).exists():
            Person(company=general.company, firstname=row['first_name'], surname=row['surname'], email_address=row['email'], area=row['area']).save()
    existing_records = Person.objects.filter(company=general.company)
    for record in existing_records:
        # print("email in DB:", record.email_address)
        # print(df['email'])
        if not record.email_address in df['email'].values:
            record.delete()
        # else:
            # print("Found in SS:", record.email_address)

def df_to_db_questions(df):
    general = General.objects.all().first()
    for index, row in df.iterrows():
        if not Question.objects.filter(company=general.company, question=row['question']).exists():
            Question(company=general.company, question=row['question'], choices=row['choices']).save()
            print("Question created:", row['question'])
    existing_records = Question.objects.filter(company=general.company)
    for record in existing_records:
        if not record.question in df['question'].values:
            record.delete()

def company_names(id): return Company.objects.get(id=id).name
def ping_names(id): return Ping.objects.get(id=id).name
def people_names(id): return Person.objects.get(id=id).email_address
def question_names(id): return Question.objects.get(id=id).question

def df_to_db_pings(df):
    general = General.objects.all().first()
    for index, row in df.iterrows():
        # print("\nDF to DB:\n", row)
        if not Ping.objects.filter(company=general.company, name=row['ping']).exists():
            Ping(company=general.company, name=row['ping']).save()
            print("Ping created:", row['ping'])
        ping = Ping.objects.filter(company=general.company, name=row['ping']).first()
        person = Person.objects.filter(email_address=row['email']).first()
        question = Question.objects.filter(question=row['question']).first()
        if not ping or not person or not question:
            pass
            # print("DF to DB Pings - error:", row, ping, person, question)
        elif not Person_Question.objects.filter(ping=ping, person=person, question=question):
            # print("Creating Person Question:", ping, person, question)
            Person_Question(company=general.company, ping=ping, person=person, question=question).save()
        # else:
            # print("Not Creating Person Question:", ping, person, question)
    existing_records = Person_Question.objects.filter(company=general.company)
    for record in existing_records:
        found = False
        for index, row in df.iterrows():
            # print(row['email'], record.person.email_address, row['question'], record.question.question)
            if row['email'] == record.person.email_address and row['question'] == record.question.question:
                found = True
        if not found:
            record.delete()


def excel_from_link(url):
    onedrive_direct_link = create_onedrive_directdownload(url)
    file = urllib.request.urlopen(onedrive_direct_link).read()
    wb = load_workbook(filename=io.BytesIO(file))
    return wb


def df_from_link_credentials(url):
# site_url = "https://1drv.ms/x/s!Apw4mhMkELavg-0qvRdYeLFDQnGLpQ?e=iaymIR&nav=MTVfezA5QzBFQkNFLTRBNUYtNDQwMy05MTNFLTkxNEJGM0JBQjY0Rn0"

# Replace with your username and password
# username = "yourusername"
# password = "yourpassword"

# Initialize the client context
# ctx = ClientContext(site_url).with_credentials(UserCredential(username, password=password))

    ctx = ClientContext(url)
    ctx.load(ctx.web)
    ctx.execute_query()

    # Specify the relative URL of the Excel file
    relative_url = "/sites/documentsite/Documents/filename.xlsx"

    # Open the binary content of the file
    response = file.File.open_binary(ctx, relative_url)

    # Save data to a BytesIO stream
    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)

    # Read the file into a pandas dataframe
    df = pd.read_excel(bytes_file_obj)
    print(df)

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

def dfs_from_file(file):
    # wb = excel_from_link(file)
    df_people = pd.read_excel(file, sheet_name="People")
    df_questions = pd.read_excel(file, sheet_name="Questions")
    df_pings = pd.read_excel(file, sheet_name="Pings")

    return df_people, df_questions, df_pings


def df_to_db_people(df, company):
    general = General.objects.all().first()
    for index, row in df.iterrows():
        if not Person.objects.filter(company=company, email_address=row['email']).exists():
            Person(company=company, email_address=row['email'], area=row['area']).save()
    existing_records = Person.objects.filter(company=company)
    for record in existing_records:
        if not record.email_address in df['email'].values:
            record.delete()

def df_to_db_questions(df, company):
    for index, row in df.iterrows():
        ref = index
        if 'ref' in row:
            ref = row['ref']
        existing_record = Question.objects.filter(company=company, question=row['question']).first()
        if existing_record:
            existing_record.ref = ref
            existing_record.choices = row['choices']
            existing_record.save()
        else:
            Question(company=company, ref=ref, question=row['question'], choices=row['choices']).save()

    # Delete existing records that aren't in the spreadsheet
    existing_records = Question.objects.filter(company=company)
    for record in existing_records:
        if not record.question in df['question'].values:
            record.delete()

def df_to_db_pings(df, company):
    general = General.objects.all().first()
    for index, row in df.iterrows():
        if not Ping.objects.filter(company=company, name=row['ping']).exists():
            Ping(company=company, name=row['ping']).save()
            # print("Ping created:", row['ping'])
        ping = Ping.objects.filter(company=company, name=row['ping']).first()
        person = Person.objects.filter(company=company, email_address=row['email']).first()
        question = Question.objects.filter(company=company, question=row['question']).first()
        if not ping or not person or not question:
            pass
        elif not Person_Question.objects.filter(company=company, ping=ping, person=person, question=question):
            Person_Question(company=company, ping=ping, person=person, question=question).save()

def df_to_db_logic(df, company):
    for index, row in df.iterrows():
        last_question = Question.objects.filter(company=company, question=row['last_question']).first()
        next_question = Question.objects.filter(company=company, question=row['next_question']).first()
        existing = Logic.objects.filter(company=company, last_question=last_question, last_answer=row['last_answer']).first()
        if not existing:
            Logic(company=company, last_question=last_question, last_answer=row['last_answer'], next_question=next_question).save()
        else:
            if existing.next_question != next_question:
                # print("Existing next answer:", existing.next_question, next_question)
                existing.next_question = next_question
                existing.save()

def company_names(id): return Company.objects.get(id=id).name
def ping_names(id): return Ping.objects.get(id=id).name
def people_names(id): return Person.objects.get(id=id).email_address
def question_names(id):
    try:
        return Question.objects.get(id=id).question
    except:
        return ""

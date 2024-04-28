from django.db.models import *
from datetime import datetime, date, timedelta, time
from collections import Counter
import pandas as pd
from .df_formats import *
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models

class Company(Model):
    model_name = "company"
    name = CharField(max_length=255, null=True, blank=True)
    icon = ImageField(null=True, blank=True, upload_to="images/")
    colour = CharField(max_length=10, null=True, blank=True, default="#A6C9EC")
    colour_text = CharField(max_length=10, null=True, blank=True, default="#ffffff")

    def __str__(self): return self.name
    def question_sets(self): return QuestionSet.objects.filter(company=self)
    def files(self): return File.objects.filter(company=self).order_by("name").order_by("-time_stamp")
    def people(self): return Person.objects.filter(company=self).order_by("firstname")
    def pings(self): return Ping.objects.filter(company=self).order_by("name")
    def logic(self): return Logic.objects.filter(company=self).order_by("last_question")

# class UserM(AbstractUser):
#     company = ForeignKey(Company, null=True, blank=True, on_delete=SET_NULL)
#     def __str__(self):
#         return self.username

class CustomUser(Model):
    model_name = "custom_user"
    user = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL)
    company = ForeignKey(Company, null=True, blank=True, on_delete=SET_NULL)
    def __str__(self):
        return self.user.username

class General(Model):
    model_name = "general"
    name = TextField(null=True, blank=True)
    company = ForeignKey(Company, null=True, blank=True, on_delete=SET_NULL)
    def __str__(self): return self.name

class Person(Model):
    model_name = "person"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    firstname = TextField(null=True, blank=True)
    surname = TextField(null=True, blank=True)
    email_address = EmailField(null=True, blank=True)
    area = TextField(null=True, blank=True)
    def __str__(self): return f"{self.firstname} ({self.company})"
    def name(self): return f"{self.firstname}"
    def last_question(self):
        result = Person_Question.objects.filter(person=self).order_by('-answer_date').first()
        return result
    def next_question_logic(self):
        last_person_question = Person_Question.objects.filter(person=self).order_by('-answer_date').first()
        last_question = last_person_question.question
        last_answer = last_person_question.answer
        if last_answer:
            last_answer = last_answer.strip()
        else:
            last_answer = "nan"
        logic = Logic.objects.filter(company=self.company, last_question=last_question, last_answer=last_answer).first()
        # print(f"Next question:, '{self.firstname}' '{last_question.question}' '{last_answer}' '{logic}'")
        return logic

class QuestionSet(Model):
    model_name = "question_set"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    name = TextField(null=True, blank=True)
    date = DateField(auto_now=False, null=True)
    class Meta:
        verbose_name = "Question Set"
        verbose_name_plural = "Question Sets"
    def __str__(self): return "[" + str(self.date) + "] " + self.name[0:50]
    def questions(self): return Question.objects.filter(question_set=self).order_by("schedule_date")

class Question(Model):
    model_name = "question"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    question = TextField(null=True, blank=True)
    choices = CharField(max_length=255, blank=True)
    def __str__(self): return f"{self.company}: {self.question}"
    def choices_split(self):
        return self.choices.split(',')
    def response_rate(self):
        emails_sent = len(Email.objects.filter(question=self))
        responses_received = len(Email.objects.filter(question=self, answer__isnull=False))
        if emails_sent == 0: return "No emails sent"
        return f"Response Rate: {int(responses_received / emails_sent * 100)}% ({responses_received} of {emails_sent})"
    def response_distribution(self):
        responses = len(Email.objects.filter(question=self, answer__isnull=False))
        answers = Email.objects.filter(question=self, answer__isnull=False).values('answer').annotate(count=Count('answer'))
        print(answers)
        answer_array = []
        for answer in answers:
            percentage = int(answer['count'] / responses * 100)
            answer_array.append((answer['answer'], answer['count'], percentage))
        answer_array = sorted(answer_array, key=lambda x: (x[1] is None, x[1]), reverse=True)[0: 10]
        return answer_array
    def responses(self):
        return Email.objects.filter(question=self).order_by('id')

class Answer(Model):
    model_name = "answer"
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    answer = TextField(null=True, blank=True)
    response_date = DateTimeField(auto_now_add=True)
    def __str__(self): return f"Answer: {self.person} {self.question} => {self.answer}"

class Ping(Model):
    model_name = "ping"
    name = TextField(null=True, blank=True)
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    def person_questions(self):
        return Person_Question.objects.filter(ping=self).filter(company=self.company)
    def questions(self):
        questions = set()
        for person_question in self.person_questions():
            print("Ping questions:", person_question, person_question.company, self.company)
            if person_question.company == self.company:
                print("Adding", person_question.question)
                questions.add(person_question.question)
        return questions
    def grouped_person_questions_answers(self):
        person_questions = self.person_questions()
        result = []
        for question in self.questions():
            result.append((question, [], [], []))
            # question, person_question, answers, answer counts
        for question in result:
            for person_question in person_questions:
                if question[0] == person_question.question:
                    question[1].append(person_question)
                    question[2].append(person_question.answer)
            counter = Counter(question[2])
            for item, count in counter.items():
                question[3].append((item, count))
        print("Grouped person questions:", result)
        return result

    def response_distribution(self):
        responses = len(Email.objects.filter(question=self, answer__isnull=False))
        answers = Email.objects.filter(question=self, answer__isnull=False).values('answer').annotate(count=Count('answer'))
        print(answers)
        answer_array = []
        for answer in answers:
            percentage = int(answer['count'] / responses * 100)
            answer_array.append((answer['answer'], answer['count'], percentage))
        answer_array = sorted(answer_array, key=lambda x: (x[1] is None, x[1]), reverse=True)[0: 10]
        return answer_array

    def emails(self):
        return Email.objects.filter(ping=self)
    def question_answer_no_response(self):
        return Person_Question.objects.filter(ping=self, answer__isnull=True)
    def response_rate(self):
        person_questions = self.person_questions()
        demoninator = len(person_questions)
        numerator = len(self.person_questions().filter(answer__isnull=False))
        if demoninator == 0: return "No questions asked"
        return f"Response Rate: {int(numerator / demoninator * 100)}% ({numerator} of {demoninator})"

class Logic(Model):
    model_name = "logic"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    last_question = ForeignKey(Question, null=True, blank=True, related_name="last_question", on_delete=CASCADE)
    last_answer = TextField(null=True, blank=True)
    next_question = ForeignKey(Question, null=True, blank=True, related_name="next_question", on_delete=CASCADE)
    def __str__(self): return f"{self.last_question.question} + {self.last_answer} => {self.next_question.question}"

class Person_Question(Model):
    model_name = "person_question"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    ping = ForeignKey(Ping, null=True, blank=True, on_delete=CASCADE)
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    answer = TextField(null=True, blank=True)
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.person.email_address} => {self.question.question}"
    def emails(self): return Email.objects.filter(person_question=self)

class Send(Model):
    model_name = "send"
    ping = ForeignKey(Ping, null=True, blank=True, on_delete=CASCADE)
    number = IntegerField(null=True, blank=True)
    person_question = ForeignKey(Person_Question, null=True, blank=True, on_delete=CASCADE)

class Email(Model):
    model_name = "email"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    ping = ForeignKey(Ping, null=True, blank=True, on_delete=CASCADE)
    person_question = ForeignKey(Person_Question, null=True, blank=True, on_delete=CASCADE)
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    # send = ForeignKey(Send, null=True, blank=True, on_delete=CASCADE)
    email_result = CharField(max_length=3, null=True, blank=True)
    email_date = DateTimeField(auto_now_add=True)
    answer = TextField(null=True, blank=True)
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self): return f"Email to {self.person} {self.email_date}"


# class Response(Model):
#     time = DateTimeField(auto_now_add=True)
#     def __str__(self): return f"Response [{self.time.date()}]"
#     def response_inds(self): return ResponseInd.objects.filter(response=self)

# class ResponseInd(Model):
#     person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
#     question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
#     answer_text = TextField(null=True, blank=True)
#     answer = ForeignKey(Answer, null=True, blank=True, on_delete=CASCADE)
#     response_date = DateTimeField(auto_now_add=True)

class To_do(Model):
    model_name = "to_do"
    name = CharField(max_length=512)
    priority = IntegerField(default=1)
    open = BooleanField(default=True)
    def __str__(self): return f"{self.name}"

class File(Model):
    TYPE_CHOICES = [
        ("People, Questions, Pings", "People, Questions, Pings"),
        ("People", "People"),
        ("Questions", "Questions"),
        ("Pings", "Pings"),
        ("Logic", "Logic"),
    ]
    model_name = "file"

    name = CharField(max_length=512)
    time_stamp = DateTimeField(auto_now_add=True, null=True,blank=True)
    last_update = DateTimeField(null=True,blank=True)
    document = FileField(upload_to="files/", blank=True, null=True)
    url = URLField(blank=True, null=True)
    type = CharField(max_length=100, blank=True, null=True, choices=TYPE_CHOICES)
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)

    def __str__(self):
        return f"{self.name} ({self.company})"

    def html_people(self): return self.html("People")
    def html_questions(self): return self.html("Questions")
    def html_pings(self): return self.html("Pings")
    def html_logic(self): return self.html("Logic")

    def html(self, file_type):
        if not file_type in self.type: return ""
        df = pd.read_excel(self.document, sheet_name=file_type)
        df_html = df.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        df_html = f"<b>{file_type}</b><br>" + df_html
        return df_html


    def delete(self, *args, **kwargs):
        self.document.delete()
        super().delete(*args, **kwargs)

all_models = [General, Company, Person, Question, Ping, Person_Question, Email, File, CustomUser, To_do]

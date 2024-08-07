from django.db.models import *
from datetime import datetime, date, timedelta, time
from collections import Counter
import pandas as pd
from .df_formats import *
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
import openpyxl as xl

standard_email_text = 'Your views can help protect our customers. <br><a style = "color:black;" href="http://riscourage.com/survey/{{ email.id }}"><u>Click here to answer the question for {{ ping.name }}</u></a><br><br><a style = "color:black;" href="http://127.0.0.1:8000/survey/{{ email.id }}"><u>Click here to answer the question for {{ ping.name }} [Local]</u></a><br><br><span style="font-size: 8px">This email and your response are confidential. Please do not forward to anyone else. Your response is anonymous and cannot be viewed by your organisation.<span>"'
standard_survey_pre = "<div style='text-align: center;'><h4>Please answer the following question with regards to your role and experience in your organisation:</h4><br>"
standard_survey_post = "<br><br><h4>Your response is kept confidential. Only the aggregated data is analysed and shared with your organisation.</h4></div>"
standard_thankyou_text = "<h1>Thank you for providing your view.</h1>"

standard_email_text_r = 'Your views can help protect our customers. <br><a style = "color:black;" href="http://riscourage.com/final_email_3_survey/{{ email.id }}"><u>Click here to review your experience</u></a><br><br><a style = "color:black;" href="http://127.0.0.1:8000/final_email_3_survey/{{ email.id }}"><u>Click here to review your experience [Local]</u></a><br><br><span style="font-size: 8px">This email and your response are confidential. Please do not forward to anyone else. Your response is anonymous and cannot be viewed by your organisation.<span>"'

class Company(Model):
    model_name = "company"
    name = CharField(max_length=255, null=True, blank=True)
    icon = ImageField(null=True, blank=True, upload_to="images/")
    colour = CharField(max_length=10, null=True, blank=True, default="#A6C9EC")
    colour_text = CharField(max_length=10, null=True, blank=True, default="#000000")
    email_subject = TextField(null=True, blank=True, default="We want your view")
    email_text = TextField(null=True, blank=True, default=standard_email_text)
    survey_text_pre = TextField(null=True, blank=True, default=standard_survey_pre)
    survey_text_post = TextField(null=True, blank=True, default=standard_survey_post)
    thankyou_text = TextField(null=True, blank=True, default=standard_thankyou_text)
    active = BooleanField(default=True)

    # Fields for the final review
    email_subject_r = TextField(null=True, blank=True, default="We want your view")
    email_text_r = TextField(null=True, blank=True, default=standard_email_text_r)
    survey_text_pre_r = TextField(null=True, blank=True, default=standard_survey_pre)
    survey_text_post_r = TextField(null=True, blank=True, default=standard_survey_post)
    thankyou_text_r = TextField(null=True, blank=True, default=standard_thankyou_text)

    def __str__(self): return self.name
    # def question_sets(self): return QuestionSet.objects.filter(company=self)
    def files(self): return File.objects.filter(company=self).order_by("name").order_by("-time_stamp")
    def people(self): return Person.objects.filter(company=self).order_by("email_address")
    def pings(self): return Ping.objects.filter(company=self).order_by("number")
    def logic(self): return Logic.objects.filter(company=self).order_by("last_question")
    def questions(self): return Question.objects.filter(company=self).order_by("ref")
    def last_ping(self): return self.pings().last()

    def email_html_web(self):
        return self.email_html(web_site=True)

    def email_html(self, web_site=False):
        div_1 = "<div style='text-align: center;'>"

        if web_site:
            image = ""
        else:
            image = "<img src='cid:image' width='600'><br>"

        if self.email_text:
            main = self.email_text
        else:
            main = "<b>No company specific text provided</b>"
        end = "</div>"
        result = div_1 + image + main + end
        return result

    def email_html_web_r(self):
        return self.email_html_r(web_site=True)

    def email_html_r(self, web_site=False):
        div_1 = "<div style='text-align: center;'>"

        if web_site:
            image = ""
        else:
            image = "<img src='cid:image' width='600'><br>"

        if self.email_text_r:
            main = self.email_text_r
        else:
            main = "<b>No company specific text provided</b>"
        end = "</div>"
        result = div_1 + image + main + end
        return result


    def lighter_colour(self):
        amount = 0.3
        hex_color = self.colour.lstrip('#')  # Remove the '#' if present
        try:
            red, green, blue = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        except:
            red, green, blue = int(hex_color[0:1], 16), int(hex_color[1:2], 16), int(hex_color[2:3], 16)

        # Calculate the new RGB values
        new_red = min(255, int(red + 255 * amount))
        new_green = min(255, int(green + 255 * amount))
        new_blue = min(255, int(blue + 255 * amount))

        # Convert back to hex format
        new_hex_color = f"#{new_red:02X}{new_green:02X}{new_blue:02X}"
        return new_hex_color

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
    def __str__(self): return f"{self.email_address} ({self.company})"
    def name(self): return f"{self.email_address}"
    def last_question(self):
        result = Person_Question.objects.filter(person=self).order_by('-answer_date').first()
        return result
    def review_emails(self):
        result = Email_r.objects.filter(person=self)
        return result
    def questions_r(self):
        questions_r = Person_Question_R.objects.filter(company=self.company, person=self, answer__isnull=False)
        return questions_r
    def next_question_r(self):
        remaining_questions = Person_Question_R.objects.filter(company=self.company, person=self)
        next_question_r = None
        for question in remaining_questions:
            if question.answer == "None" or question.answer == "" or question.answer is None:
                next_question_r = question
                break

        # next_question_r = Person_Question_R.objects.filter(company=self.company, person=self, answer="None").first()
        return next_question_r
    def has_answered_r(self):
        all_questions_r = Person_Question_R.objects.filter(company=self.company, person=self)
        not_answered_questions_r = Person_Question_R.objects.filter(company=self.company, person=self, answer="None")
        none_answered_questions_r = Person_Question_R.objects.filter(company=self.company, person=self, answer="None")
        return len(all_questions_r) > len(not_answered_questions_r)
# class QuestionSet(Model):
#     model_name = "question_set"
#     company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
#     name = TextField(null=True, blank=True)
#     date = DateField(auto_now=False, null=True)
#     class Meta:
#         verbose_name = "Question Set"
#         verbose_name_plural = "Question Sets"
#     def __str__(self): return "[" + str(self.date) + "] " + self.name[0:50]
#     def questions(self): return Question.objects.filter(question_set=self).order_by("schedule_date")
#
# def add_lines(text, gap=40):
#     l = len(text)
#     r = range(gap, l, gap)
#     for x in r:
#         position, found = x, False
#         while not found and position < l:
#             if text[position] == " ":
#                 text = text[:position] + "X" + text[position + 1:]
#                 found = True
#             position += 1
#     # print("Add lines:", text)
#     return text

class Question(Model):
    model_name = "question"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    ref = CharField(max_length=20, blank=True, default="")
    question = TextField(null=True, blank=True)
    choices = CharField(max_length=255, blank=True)

    def __str__(self): return f"{self.ref}. {self.question}"
    def choices_split(self):
        return self.choices.split(',')
    def choices_and_next_question(self):
        choices = self.choices.split(',')
        choices.append('Viewed')
        choices.append('None')
        result = []
        for choice in choices:
            choice = choice.strip()
            # print(f"Logic Search: LQ:'{self}' LA:'{choice}'")

            logic = Logic.objects.filter(company=self.company, last_question=self, last_answer=choice).first()
            if not logic:
                logic = Logic(company=self.company, last_question=self, last_answer=choice)
                logic.save()
            next_question = logic.next_question
            # print(f"Choices: '{self.question}' '{choice}' '{next_question}'")
            result.append((choice, next_question, logic.id))

        return result

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
    def question_viz(self):
        return add_lines(self.question)

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
    sent = BooleanField(default=False)
    number = IntegerField(default=1)

    def __str__(self): return f"{self.name} ({self.company})"

    def person_questions(self):
        return Person_Question.objects.filter(ping=self).filter(company=self.company).order_by('person')
    def questions(self):
        questions = set()
        for person_question in self.person_questions():
            # print("Ping questions:", person_question, person_question.company, self.company)
            if person_question.company == self.company:
                # print("Adding", person_question.question)
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
        # print("Grouped person questions:", result)
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
    def __str__(self):
        return f"{self.last_question} + {self.last_answer} => {self.next_question}"

class Person_Question(Model):
    model_name = "person_question"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    ping = ForeignKey(Ping, null=True, blank=True, on_delete=CASCADE)
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    viewed = BooleanField(default=False)
    answer = TextField(null=True, blank=True, default="None")
    send_date = DateTimeField(null=True, blank=True)
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self):
        if self.answer:
            return f"{self.person.email_address} => {self.question.question} => {self.answer}"
        else:
            return f"{self.person.email_address} => {self.question.question} => No response"

    def details(self):
        if self.question is None:
            return self.person.email_address, "No question", ""
        if self.answer is None:
            return self.person.email_address, self.question.question, "No answer"
        return self.person.email_address, self.question.question, self.answer

    def emails(self): return Email.objects.filter(person_question=self)
    def next_question_logic(self):
        # last_person_question = Person_Question.objects.filter(person=self).order_by('-answer_date').first()
        last_question = self.question
        last_answer = self.answer
        if last_answer:
            last_answer = last_answer.strip()
        else:
            last_answer = "None"
        logic = Logic.objects.filter(company=self.company, last_question=last_question, last_answer=last_answer).first()
        return logic

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
    email_date = DateTimeField()
    answer = TextField(null=True, blank=True)
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self): return f"Email to {self.person} ({self.email_date})"

class Email_r(Model):
    model_name = "email"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    email_result = CharField(max_length=3, null=True, blank=True)
    email_date = DateTimeField()
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self): return f"Email (review) to {self.person} ({self.email_date})"

class Person_Question_R(Model):
    model_name = "person_question_r"
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    email = ForeignKey(Email_r, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    viewed = BooleanField(default=False)
    free_text = BooleanField(default=False)
    answer = TextField(null=True, blank=True, default="None")
    send_date = DateTimeField(null=True, blank=True)
    answer_date = DateTimeField(null=True, blank=True)
    def __str__(self):
        try:
            if not self.person:
                return f"{self.question.question} => {self.answer}"
            if self.answer:
                return f"{self.person.email_address} => {self.question.question} => {self.answer}"
            else:
                return f"{self.person.email_address} => {self.question.question} => No response"
        except:
            return "CONFUSED"

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
    owner = CharField(max_length=512, blank=True, null=True)
    priority = IntegerField(default=1)
    open = BooleanField(default=True)
    def __str__(self): return f"{self.name}"

required_fields_dict = {
    'People': ["email", "area"],
    'Questions': ["question", "choices"],
    'Pings': ['ping', 'email', 'question',],
    'Logic': ["last_question", "next_question", "last_answer"],
}

def df_to_db_logic_errors(df, company):
    errors = []
    for index, row in df.iterrows():
        last_question = Question.objects.filter(company=company, question=row['last_question'])
        next_question = Question.objects.filter(company=company, question=row['next_question'])
        if len(last_question) == 0: errors.append(f"<b>No last question:</b> LQ: {row['last_question']} LA: {row['last_answer']} NQ: {row['next_question']}")
        if len(next_question) == 0: errors.append(f"<b>No next question:</b> LQ: {row['last_question']} LA: {row['last_answer']} NQ: {row['next_question']}")
    return errors


class File(Model):
    TYPE_CHOICES = [
        # ("People, Questions, Pings", "People, Questions, Pings"),
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
        return f"{self.name}"

    def message(self):
        text = ""
        file_type = str(self.type)
        try:
            df = pd.read_excel(self.document, sheet_name=file_type)
        except:
            # sheets = pd.ExcelFile(self.document).sheet_names
            return f"<li>There is no sheet named <b>'{file_type}'</b> in this workbook.</li>"
        required_fields = required_fields_dict[file_type]
        for field in required_fields:
            if field not in df.columns:
                error = f"<li>Missing field: '{field}'.</li>"
                text += error
        if self.type == "Logic":
            errors = df_to_db_logic_errors(df, self.company)
            for error in errors:
                text += f"<li>{error}</li>"


        return text

    def sheets(self):
        return pd.ExcelFile(self.document).sheet_names

    # def rename_sheet(self, current_sheet_name):
    #     # ss = pd.read_excel(self.document.path)
    #
    #     # file_path = self.document.path
    #     workbook = xl.load_workbook(self.document)
    #     sheet = workbook[current_sheet_name]
    #     sheet.title = self.type
    #     workbook.save(self.document)

        # ss = xl.load_workbook(self.document, read_only=False)
        # ss_sheet = ss[current_sheet_name]
        # ss_sheet.title = self.type
        # ss.save(self.document)

    def html_people(self): return self.html("People")
    def html_questions(self): return self.html("Questions")
    def html_pings(self): return self.html("Pings")
    def html_logic(self): return self.html("Logic")

    def html(self, file_type):
        if not file_type in self.type: return ""
        try:
            df = pd.read_excel(self.document, sheet_name=file_type)
        except:
            return ""
        df_html = df.to_html(classes=['table', 'table-striped', 'table-center'], index=True, justify='left', formatters=formatters)
        df_html = f"<b>{file_type}</b><br>" + df_html
        return df_html


    def delete(self, *args, **kwargs):
        self.document.delete()
        super().delete(*args, **kwargs)

all_models = [General, Company, Person, Question, Ping, Person_Question, Person_Question_R, Email, Email_r, File, CustomUser, To_do, Logic]

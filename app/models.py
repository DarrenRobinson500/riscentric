from django.db.models import *
from datetime import datetime, date, timedelta, time

class Company(Model):
    name = TextField(null=True, blank=True)
    def __str__(self): return self.name
    def question_sets(self): return QuestionSet.objects.filter(company=self)
    def files(self): return File.objects.filter(company=self).order_by("name").order_by("-time_stamp")
    def people(self): return Person.objects.filter(company=self).order_by("surname")

class General(Model):
    name = TextField(null=True, blank=True)
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    def __str__(self): return self.name

class Person(Model):
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    firstname = TextField(null=True, blank=True)
    surname = TextField(null=True, blank=True)
    email_address = EmailField(null=True, blank=True)
    area = TextField(null=True, blank=True)
    def __str__(self): return f"{self.firstname} {self.surname} ({self.company})"

class QuestionSet(Model):
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)
    name = TextField(null=True, blank=True)
    date = DateField(auto_now=False, null=True)
    class Meta:
        verbose_name = "Question Set"
        verbose_name_plural = "Question Sets"
    def __str__(self): return "[" + str(self.date) + "] " + self.name[0:50]
    def questions(self): return Question.objects.filter(question_set=self).order_by("schedule_date")

class Question(Model):
    question_set = ForeignKey(QuestionSet, null=True, blank=True, on_delete=CASCADE)
    question = TextField(null=True, blank=True)
    choices = CharField(max_length=255, blank=True)
    schedule_date = DateField(auto_now=False, null=True)
    sent_date = DateField(auto_now=False, null=True)
    def __str__(self): return f"{self.question} [{self.question_set.name}]"
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
        return Email.objects.filter(question=self)

class Email(Model):
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    email_result = CharField(max_length=3, null=True, blank=True)
    email_date = DateTimeField(auto_now_add=True)
    answer = TextField(null=True, blank=True)
    def __str__(self): return f"Email to {self.person} {self.email_date}"

class Answer(Model):
    person = ForeignKey(Person, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    answer = TextField(null=True, blank=True)
    response_date = DateTimeField(auto_now_add=True)
    def __str__(self): return f"Answer: {self.person} {self.question} => {self.answer}"

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

class File(Model):
    TYPE_CHOICES = [
        ("Questions", "Questions"),
        ("Employees", "Employees"),
    ]

    name = CharField(max_length=512)
    time_stamp = DateTimeField(auto_now_add=True, null=True,blank=True)
    last_update = DateTimeField(null=True,blank=True)
    document = FileField(upload_to="files/", blank=True, null=True)
    type = CharField(max_length=100, blank=True, null=True, choices=TYPE_CHOICES)
    company = ForeignKey(Company, null=True, blank=True, on_delete=CASCADE)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.document.delete()
        super().delete(*args, **kwargs)

all_models = [QuestionSet, Question, Answer, File, Company, General, Person, Email]

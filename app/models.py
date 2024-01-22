from django.db.models import *
from datetime import datetime, date, timedelta, time

class QuestionSet(Model):
    description = TextField(null=True, blank=True)
    date = DateField(auto_now=False, null=True)
    class Meta:
        verbose_name = "Question Set"
        verbose_name_plural = "Question Sets"
    def __str__(self): return "[" + str(self.date) + "] " + self.description[0:50]
    def questions(self): return Question.objects.filter(question_set=self)

class Question(Model):
    question_set = ForeignKey(QuestionSet, null=True, blank=True, on_delete=CASCADE)
    question = TextField(null=True, blank=True)
    choices = CharField(max_length=255, blank=True)
    def __str__(self): return f"{self.question} [{self.question_set.description}]"
    def choices_split(self):
        return self.choices.split(',')
    def prop_yes(self):
        responses = ResponseInd.objects.filter(question=self)
        responses_yes = responses.filter(answer_text="yes")
        if len(responses) > 0:
            return int(round(len(responses_yes) / len(responses), 2) * 100)
        else:
            return 0

class Answer(Model):
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    answer = TextField(null=True, blank=True)
    def __str__(self): return "[" + str(self.date) + "] " + self.description[0:50]

class Response(Model):
    time = DateTimeField(auto_now_add=True)
    def __str__(self): return f"Response [{self.time.date()}]"
    def response_inds(self): return ResponseInd.objects.filter(response=self)

class ResponseInd(Model):
    response = ForeignKey(Response, null=True, blank=True, on_delete=CASCADE)
    question = ForeignKey(Question, null=True, blank=True, on_delete=CASCADE)
    answer_text = TextField(null=True, blank=True)
    answer = ForeignKey(Answer, null=True, blank=True, on_delete=CASCADE)

class File(Model):
    TYPE_CHOICES = [
        ("questions", "Risk Questions"),
    ]

    name = CharField(max_length=512)
    time_stamp = DateTimeField(auto_now_add=True, null=True,blank=True)
    last_update = DateTimeField(null=True,blank=True)
    document = FileField(upload_to="files/", blank=True, null=True)
    type = CharField(max_length=100, blank=True, null=True, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.document.delete()
        super().delete(*args, **kwargs)

all_models = [QuestionSet, Question, Answer, Response, File]

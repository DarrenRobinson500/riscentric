from django.db.models import *

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
    def __str__(self): return self.question

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

all_models = [QuestionSet, Question, Answer, Response]

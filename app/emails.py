from .models import *
from .email_microsoft_test import *

def send_email_logic(ping):
    ping.sent = True
    ping.save()

    # print("Email person questions:", ping.person_questions())
    for person_question in ping.person_questions():
        print("Email: ", person_question.answer)
        if person_question.answer != "None" and person_question.answer != "Viewed": continue
        person = person_question.person
        question = person_question.question
        to = person_question.person.email_address

        email = Email(company=ping.company, ping=ping, person=person, question=question, person_question=person_question)
        email.save()
        print("Created email:", email)
        send_microsoft_email(email, [to], send=True)



from .models import *
from .email_microsoft_test import *

def email_send_logic(ping):
    ping.sent = True
    ping.save()

    for person_question in ping.person_questions():
        # print("Email: ", person_question.answer)
        if person_question.answer in ["None", "Viewed", "Failed to send"]:
            person_question.send_date = datetime.now()
            person_question.save()
            person = person_question.person
            question = person_question.question
            to = person_question.person.email_address
            email = Email(company=ping.company, ping=ping, person=person, question=question, person_question=person_question, email_date=datetime.now())
            email.save()
            # print("Created email:", email)
            send_microsoft_email(email, [to], send=True)
        else:
            print("Send did not send:", person_question.answer)

def email_send_ind_logic(person_question):
    if person_question.answer in ["None", "Viewed", "Failed to send"]:
        person_question.send_date = datetime.now()
        person_question.save()
        person = person_question.person
        question = person_question.question
        to = person_question.person.email_address
        email = Email(company=person_question.company, ping=person_question.ping, person=person, question=question, person_question=person_question, email_date=datetime.now())
        email.save()
        # print("Created email:", email)
        send_microsoft_email(email, [to], send=True)
    else:
        print("Send did not send:", person_question.answer)


def email_resend_logic(email):
    email.answer = "None"
    email.email_date = datetime.now()
    email.save()
    person_question = email.person_question
    print("Email:", person_question.answer)
    to = person_question.person.email_address
    if person_question.answer in ["None", "Viewed", "Failed to send"]:
        send_microsoft_email(email, [to], send=True)
    else:
        print("Resend did not send:", person_question.answer)



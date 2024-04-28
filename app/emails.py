from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import *
from .models import *
from .email_microsoft_test import *

def send_email_logic(ping):
    subject = 'Subject'
    from_email = 'riscentric.com'

    for person_question in ping.person_questions():
        if person_question.answer: continue
        person = person_question.person
        question = person_question.question
        to = person_question.person.email_address

        # render the HTML content using a template
        email = Email(company=ping.company, ping=ping, person=person, question=question, person_question=person_question)
        email.save()
        context = {"email": email}
        print("Email:", email)
        # html_content = render_to_string('email_template.html', context)

        # create a plain text version of the email
        # text_content = strip_tags(html_content)

        # create the email message
        send_microsoft_email(email, [to])

        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # result = msg.send()
        # email.email_result = result
        # email.save()


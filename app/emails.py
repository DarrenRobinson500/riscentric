from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import *

def send_email_logic(question, people):
    subject = 'Subject'
    from_email = 'riscentric.com'

    for person in people:
        to = person.email

        # render the HTML content using a template
        context = {"question": question, "person": person}
        html_content = render_to_string('email_template.html',context)

        # create a plain text version of the email
        text_content = strip_tags(html_content)

        # create the email message
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        question.sent_date = datetime.today()
        question.save()


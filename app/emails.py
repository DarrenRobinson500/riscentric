from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email_logic(context):
    subject = 'Subject'
    from_email = 'riscentric.com'
    to = 'darrenjamesspare@gmail.com'
    # to = "simone@riscentric.com"

    # render the HTML content using a template
    html_content = render_to_string('email_template.html',context)

    # create a plain text version of the email
    text_content = strip_tags(html_content)

    # create the email message
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
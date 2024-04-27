from exchangelib import Account, Configuration, Identity, OAUTH2, OAuth2Credentials
from exchangelib import Configuration, Account, DELEGATE
from exchangelib import Message, Mailbox, FileAttachment, HTMLBody
from django.template.loader import render_to_string
from datetime import datetime
import os

email_address = os.environ.get("email_address")
email_password = os.environ.get("email_password")

secret_value = os.environ.get("secret_value")
secret = os.environ.get("secret")
client = os.environ.get("client")
object = os.environ.get("object")
tenant = os.environ.get("tenant")

os.environ.get("")

creds = OAuth2Credentials(
    client_id=client,
    client_secret=secret_value,
    tenant_id=tenant,
    identity=Identity(primary_smtp_address=email_address)
)

config = Configuration(server='outlook.office365.com', credentials=creds, auth_type=OAUTH2)

account = Account(
    primary_smtp_address=email_address,
    autodiscover=False,
    config=config
)


def send_microsoft_email(email, recipients):

    # text = f"Hello World {datetime.now()}"
    # html_template = "<html><body>Hello, here's your image: <img src=\"cid:image\"></body></html>"

    div_1 = "<div style='text-align: center;'>"
    image = "<img src=\"cid:image\"></body></html>"
    # line1 = "<p style='margin: 0;'>Less than 30 seconds of your time to get your view on a single question about risk.</p>"
    # line2 = "<p style='margin: 0;'>Thank you for you participation.</p><br>"
    # line3 = "<p style='margin: 0;'>Click here to answer the question.</p>"
    # div_2 = "<div style='text-align: center'>"
    # html_template = div_1 + image + line1 + line2 + line3 + div_2

    context = {"email": email}
    print("Email:", email)
    html_template = div_1 + image + render_to_string('email_template.html', context)

    # email_body = HTMLBody(html_content)
    body=HTMLBody(html_template)
    subject = "We want your view"

    # body = "Text content"
    from_email = email_address
    # recipients = ["darrenandamanda.robinson@gmail.com", ]

    to_recipients = []
    for recipient in recipients:
        to_recipients.append(Mailbox(email_address=recipient))

    message = Message(account=account,
                folder=account.sent,
                subject=subject,
                body=body,
                to_recipients=to_recipients)

    with open("images/image.png", "rb") as f:
        image_attachment = FileAttachment(
            name="image.png",
            content=f.read(),
            is_inline=True,  # Mark as an inline attachment
            content_id="image",  # Use a unique content ID
        )
        message.attach(image_attachment)

    message.send_and_save()



    # account.send_message(
    #     subject=subject,
    #     body=body,
    #     to_recipients=recipients
    # )


    # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    # msg.attach_alternative(html_content, "text/html")
    # result = msg.send()

    account.protocol.close()


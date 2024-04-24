from exchangelib import Account, Configuration, Identity, OAUTH2, OAuth2Credentials
from exchangelib import Configuration, Account, DELEGATE
from exchangelib import Message, Mailbox, FileAttachment, HTMLBody
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


def send_microsoft_email(subject, text_content, html_content, recipients):

    text = f"Hello World {datetime.now()}"
    html_template = f"<h1>{text}</h1>"
    email_body = HTMLBody(html_content)

    body = "Text content"
    from_email = email_address
    # recipients = ["darrenandamanda.robinson@gmail.com", ]

    to_recipients = []
    for recipient in recipients:
        to_recipients.append(Mailbox(email_address=recipient))

    m = Message(account=account,
                folder=account.sent,
                subject=subject,
                body=email_body,
                to_recipients=to_recipients)

    # attach files
    # for attachment_name, attachment_content in attachments or []:
    #     file = FileAttachment(name=attachment_name, content=attachment_content)
    #     m.attach(file)
    m.send_and_save()



    # account.send_message(
    #     subject=subject,
    #     body=body,
    #     to_recipients=recipients
    # )


    # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    # msg.attach_alternative(html_content, "text/html")
    # result = msg.send()

    account.protocol.close()


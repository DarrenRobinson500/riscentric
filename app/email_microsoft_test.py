from exchangelib import Account, Configuration, Identity, OAUTH2, OAuth2Credentials
from exchangelib import Configuration, Account, DELEGATE
from exchangelib import Message, Mailbox, FileAttachment, HTMLBody
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

def send_microsoft_email(email, recipients, send=True):
    html_template = email.company.email_html()
    # print(html_template)
    html_template = html_template.replace("{{ email.id }}", str(email.id))
    html_template = html_template.replace("{{ ping.name }}", email.ping.name)

    body=HTMLBody(html_template)
    subject = email.company.email_subject

    to_recipients = []
    for recipient in recipients:
        to_recipients.append(Mailbox(email_address=recipient))

    try:
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
        if send:
            message.send_and_save()
        print("Email Sent:", email)
    except:
        email.answer = "Failed to send"
        email.save()

    account.protocol.close()

def send_microsoft_email_r(email, send=True):
    html_template = email.company.email_html_r()
    print(html_template)
    html_template = html_template.replace("{{ email.id }}", str(email.id))

    body=HTMLBody(html_template)
    subject = email.company.email_subject_r

    to_recipients = [Mailbox(email_address=email.person.email_address)]

    # try:
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
    if send:
        message.send_and_save()
    print("Email Sent:", email)
    # except:
    #     email.answer = "Failed to send"
    #     email.save()

    account.protocol.close()

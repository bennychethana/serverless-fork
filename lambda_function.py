import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import boto3


load_dotenv()

# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# DOMAIN = os.getenv('WEBAPP_DOMAIN', 'https://yourdomain.com')

def get_secret(secret_name):
    try:
        client = boto3.client('secretsmanager', region_name='us-east-1')
        response = client.get_secret_value(SecretId=secret_name)
        
        secret_dict = json.loads(response['SecretString'])
        
        return secret_dict
    
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise

def send_email(to_email, verification_link, first_name, SENDGRID_API_KEY):
    subject = "Verify Your Email Address"
    body = f"""
    Hi {first_name},

    Please verify your email address by clicking the link below:

    {verification_link}

    This link will expire in 2 minutes.

    Regards,
    webappbybenny team.
    """
    message = Mail(
        from_email="noreply@webappbybenny.me",
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f">>>>>>>>>>>>> Email sent: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

def lambda_handler(event, context):
    for record in event['Records']:
        print(f">>>>>> inside lambda_handler")
        message = json.loads(record['Sns']['Message'])
        print(">>>>>>>>> message received:", message)
        email = message.get("email")
        first_name = message.get("first_name")
        token = message.get("token")

        if not email:
            return {"status": "error", "message": "Invalid payload"}
        
        # retrieve credentials from Secrets Manager
        email_creds = get_secret('email-service-credentials-fixed')
        SENDGRID_API_KEY = email_creds['SENDGRID_API_KEY']
        DOMAIN = email_creds['WEBAPP_DOMAIN']

        # Send email
        verification_link = f"https://{DOMAIN}/verify/?user={email}&token={token}"
        print(">>>>>>>>> verification_link:",verification_link)
        try:
            print(">>>>>>>>> trying to send email")
            send_email(email, verification_link, first_name, SENDGRID_API_KEY)
        except Exception as e:
            return {"status": "error", "message": f"Failed to send email: {str(e)}"}

    return {"status": "success", "message": "Email sent and token logged successfully"}

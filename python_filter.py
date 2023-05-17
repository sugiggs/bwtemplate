#!/usr/bin/env python3

import sys
import os
import email
import smtplib
import logging
from email.mime.text import MIMEText
from email.message import Message
import re

logging.basicConfig(filename='/etc/bitwarden/logs/python_filter.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


smtp_server = None
smtp_port = None
smtp_user = None
smtp_password = None
mail_subject  = {}
mail_mode = ''

config_file = '/etc/bitwarden/bwtemplate.override.env'
with open(config_file, 'r') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    if line.startswith('bwtemplate__mail__smtp__host='):
        smtp_server = line.split('=')[1]
    elif line.startswith('bwtemplate__mail__smtp__port='):
        smtp_port = line.split('=')[1]
    elif line.startswith('bwtemplate__mail__smtp__username='):
        smtp_user = line.split('=')[1]
    elif line.startswith('bwtemplate__mail__smtp__password='):
        smtp_password = line.split('=')[1]
    elif line.startswith('bwtemplate__from='):
        mail_from = line.split('=')[1]
    elif line.startswith('bwtemplate__subject_invitation='):
        mail_subject['invitation'] = line.split('=')[1]
    elif line.startswith('bwtemplate__subject_welcome='):
        mail_subject['welcome'] = line.split('=')[1]

#new_subject = '[BMW IT Dept] New Tool: Bitwarden Password Manager'
#new_from = 'BMW IT Dept <bmw@securityforte.com>'

# Configure logging


# Get the sender and recipient from command-line arguments
sender = sys.argv[1]
recipient = sys.argv[2]


# Read the raw email from standard input
raw_email = sys.stdin.read()

# Parse the raw email into an email object
msg = email.message_from_string(raw_email)

email_subject = msg['Subject']

# Modify the email body

if email_subject.startswith(("Join", "Welcome")):
    if email_subject.startswith(("Join")):
        mail_mode = "invitation"
    elif email_subject.startswith(("Welcome")):
        mail_mode = "welcome"
    
    msg.replace_header('Subject', mail_subject[mail_mode])
    
    
    filename = mail_mode + ".html"

    try:
        # open the file for reading
        with open("/etc/bitwarden/"+filename, "r") as file:
            # read the file contents into a variable
            html_contents = file.read()

    except FileNotFoundError:
        print("Template not found. Please check the file path and try again.")
    except IOError:
        print("Error reading file. Please check the file permissions and try again.")

    if msg.is_multipart():
        for part in msg.walk():
            text = part.get_payload(decode=True)
            charset = part.get_content_charset() if part.get_content_charset() else 'utf-8'

            if part.get_content_type() == 'text/plain':
                modified_text = text.decode(charset) 
                part.set_payload(modified_text, charset=charset)
            elif part.get_content_type() == 'text/html':
                org_name = '';
                expiry_date = ''
                join_url = ''
                email_body = text.decode('latin-1')
                
                result = re.search(r'<b.*?>(.*?)<\/b>', email_body)
                if result:
                    org_name = result.group(1)

                pattern = r'expires on <b>(.*?)</b>'
                result = re.search(pattern, email_body)
                if result:
                    expiry_date = result.group(1)

                url_pattern = r'href="(\S+accept-organization[^"]+)"'
                result = re.search(url_pattern, email_body)
                if result:
                    join_url = result.group(1)

                html_contents = html_contents.replace("{ORG_NAME}",org_name)
                html_contents = html_contents.replace("{EXPIRY_DATE}",expiry_date)
                html_contents = html_contents.replace("{JOIN_LINK}",join_url)


                modified_text = html_contents
                part.set_payload(modified_text, charset=charset)
                #part.set_payload(modified_text, charset='latin-1')
                #part.set_payload(modified_text)


    msg.attach(MIMEText(html_contents, 'html'))

fmt = '{}'

msg.replace_header('From', mail_from)

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        if smtp_user:
            server.starttls()
            server.login(smtp_user, smtp_password)
        else:
            server.ehlo()
        server.sendmail(sender, recipient, fmt.format(msg).encode('utf-8') )
        #server.sendmail(sender, recipient, msg.as_string() )
        server.quit()

    logging.info(f'Successfully sent email from {sender} to {recipient}')
except smtplib.SMTPHeloError as e:
    logging.error(f'SMTP Helo error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPRecipientsRefused as e:
    logging.error(f'SMTP recipients refused error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPSenderRefused as e:
    logging.error(f'SMTP sender refused error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPDataError as e:
    logging.error(f'SMTP data error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPNotSupportedError as e:
    logging.error(f'SMTP not supported error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPAuthenticationError as e:
    logging.error(f'SMTP authentication error while sending email from {sender} to {recipient}: {e}')
except smtplib.SMTPException as e:
    logging.error(f'Failed to send email from {sender} to {recipient}: {e}')

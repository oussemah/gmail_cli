import httplib2
import os
import subprocess

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


import base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mimetypes

from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'GmailCLI'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmailcli.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = "EmailCommand"
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials
    
def SenMessage(service, user_id, message_raw):
	"""Send an email message.
	
	Args:
	  service: Authorized Gmail API service instance.
	  user_id: User's email address. The special value me
	           can be user to indicate the authenticated user.
	  message: Message to be sent.
	  
	Returns:
	  Sent Message.
	"""
	try:
		message = (service.users().messages().send(userId=user_id, body=message_raw).execute())
		print 'Message Id: %s' % message['id']
		return message
	except errors.HttpError, error:
		print 'An error occured: %s' % error

def CreateMessage(sender, to, subject, message_text, file_dir, filename):
	"""Create a message for an email.
	
	Args:
	  sender: Email address of the sender.
	  to: Email address of the receiver.
	  subject: The subject of the email message.
	  message_text: The text of the email message.
	  
	Returns:
	  An object containing a base64 encoded email object.
	"""
	message = MIMEMultipart()
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	
	msg = MIMEText(message_text)
	message.attach(msg)
	
	path = os.path.join(file_dir, filename)
	content_type, encoding = mimetypes.guess_type(path)
	
	if content_type is None or encoding is not None:
		content_type= 'application/octet-stream'
	main_type, sub_type = content_type.split('/', 1)
	if main_type == 'text':
		fp = open(path, 'rb')
		msg = MIMEText(fp.read(), _subtype=sub_type)
		fp.close()
	elif main_type =='image':
		fp = open(path, 'rb')
		msg = MIMEImage(fp.read(), _subtype=sub_type)
		fp.close()
	else:
		fp = open(path, 'rb')
		msg = MIMEBase(main_type, sub_type)
		msg.set_payload(fp.read())
		fp.close()
	
	msg.add_header('Content-Disposition', 'attachment', filename=filename)
	message.attach(msg)
	
	return {'raw': base64.b64encode(message.as_string())}


	
def main():
	"""Checks gmail for executions requests,
	   executes them and returns status in a screenshot.
	"""
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)

	results = service.users().messages().list(userId='me', q="from:oussema.elharbi@gmail.com is:unread subject:execute").execute()
	messages = results.get('messages', [])
	for message in messages:
		#Get the message
		message = service.users().messages().get(userId='me', id=message['id']).execute()
		print 'Message snippet: %s' % message['snippet']
		#Execute Requested command
		subprocess.call(message['snippet'], shell=True)
		os.system('date')
		os.system('import -window root -delay 200 /tmp/screenshot.jpg')
		#Send feedback
		message_raw = CreateMessage('oussema.elharbi@gmail.com', 'oussema.elharbi@gmail.com', 'Execution feedback', 'result for :'+message['snippet'], '/tmp/', 'screenshot.jpg')
		os.system('rm /tmp/screenshot.jpg')
		SenMessage(service, 'me', message_raw)
		#Trash the message
		service.users().messages().trash(userId='me', id=message['id']).execute()

if __name__ == '__main__':
    main()

import imaplib
import email
import pandas as pd
import numpy as np
import datetime
from email.message import EmailMessage
import smtplib
import imghdr

pd.set_option('display.max_columns',500)
pd.set_option('display.max_rows',500)

def read_email_from_gmail():
  mail = imaplib.IMAP4_SSL('imap.gmail.com')

  # intantiate the username and the passwprd
  user ="username@gmail.com" 
  password = "password"
  mail.login(user,password)

  # print(mail.list()) - get list of all possible mailboxes we can access
  mail.select('"[Gmail]/All Mail"')

  result, data = mail.search(None, 'ALL')
  mail_ids = data[0]

  id_list = mail_ids.split()   
  first_email_id = int(id_list[0])
  latest_email_id = int(id_list[-1])

  emails_received = []
  emails_sent = []

  for i in range(latest_email_id,first_email_id, -1):
      result, data = mail.fetch(str(i), '(RFC822)' )

      for response_part in data:
          if isinstance(response_part, tuple):
              msg = email.message_from_bytes(response_part[1])
              email_subject = msg['subject']
              email_to = msg['to']
              email_from = msg['from']
              emails_sent.append(email_to)
              emails_received.append(email_from)
  
  # Formatting Emails Received - needs to be formatted for the < and > as it's picked up when scraping
  emails_received_formatted = []
  for i in emails_received:
    emails_received_formatted.append(i[i.find("<")+1:i.find(">")])
  
  received_email_df = pd.DataFrame(emails_received_formatted,columns=['Email']).reset_index()

  # Getting received email counts
  email_received_counts = received_email_df.groupby('Email').size().reset_index()
  email_received_counts.rename(columns={0: 'Emails Received Count'},inplace=True)

  # No formatting here, will truncate values - no < or > when scraping
  emails_sent_formatted = []
  for i in emails_sent:
    emails_sent_formatted.append(i)
  
  sent_email_df = pd.DataFrame(emails_sent_formatted,columns=['Email']).reset_index()

  # Getting email counts and users with exactly 2 emails sent and NO response
  email_sent_counts = sent_email_df.groupby('Email').size().reset_index()
  email_sent_counts.rename(columns={0: 'Emails Sent Count'},inplace=True)

  # Merging Lists and grabbing users that are NOT in emails received
  email_merge = pd.concat([email_sent_counts,email_received_counts],axis=1)

  # Getting all users where we've sent them emails, but we haven't received an email from them
  users_to_send_second_follow_up = email_sent_counts[~email_sent_counts['Email'].isin(email_received_counts['Email'])]
  
  # Making sure we've sent the user 2 emails
  users_to_send_second_follow_up = users_to_send_second_follow_up[users_to_send_second_follow_up['Emails Sent Count'] == 2]

  # First Email Follow Up
  #######################################################################################################################
  # sheet_url = 'https://docs.google.com/spreadsheets/d/137nXK4BEfJOGU9uvubyi4dAijtexsJpWemJKcfzsxEM/edit#gid=1251324109'
  # url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')

  # sheet_df = pd.read_csv(url,error_bad_lines=False, usecols = ['Name', 'Address', 'Email'])

  # sheet_df['First Name'] = sheet_df['Name'].apply(lambda x: x.split(' ')[0])

  # users_to_send_first_follow_up = sheet_df[~sheet_df['Email'].isin(received_email_df['Email'])]

  # users_to_send_first_follow_up.to_csv('users_to_send_first_follow_up_email.csv')
  df_leads = pd.read_csv('test_leads_three_emails.csv')
  df_leads['First Name'] = df_leads['Name'].apply(lambda x: x.split(' ')[0])
  def GenerateFirstEmail(name, address, email_address):

    content_str = '''Hi {},

Just following up to see if you have had the chance to review the pricing sheet I sent over.
    
As a heads up, our routes are filling up quickly and we'd love to get you onboard before we're completely full this season.
    
Please let me know if you'd like to sign up or if have any questions—looking forward to hearing from you!

I look forward to hearing from you!

Best,
John Doe
(123) 456-7890
www.google.com.com'''

    day = datetime.datetime.now().strftime("%A")

    msg = EmailMessage()
    msg['Subject'] = address
    msg['From'] = 'username@gmail.com'
    msg['To'] = email_address
    msg.set_content(content_str.format(name, day))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('username@gmail.com', 'password')
        smtp.send_message(msg)

    print(name_first_follow_up, email_address_first_follow_up + ' Emailed Successfully! (First Follow Up)')

  for name_first_follow_up, address, email_address_first_follow_up in zip(df_leads['First Name'], df_leads['Address'], df_leads['Email']):
    GenerateFirstEmail(name_first_follow_up, address, email_address_first_follow_up)
#   #######################################################################################################################

#   # Second Email Follow Up
#   #######################################################################################################################
  def GenerateSecondEmail(name, address, email_address):

    content_str = '''Hi {},

I am following up again to see if you have had the chance to review the pricing I sent over. As a heads up, our routes are almost sold out for this season!

As a courtesy, we are holding a spot on our route for you pending your decision. Please let me know if you'd like to sign up, or if you have any questions.

Best,
John Doe
(123) 456-7890
www.google.com.com'''

    day = datetime.datetime.now().strftime("%A")

    msg = EmailMessage()
    msg['Subject'] = address
    msg['From'] = 'username@gmail.com'
    msg['To'] = email_address
    msg.set_content(content_str.format(name, day))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('username@gmail.com', 'password')
        smtp.send_message(msg)

    print(name, email_address + ' Emailed Successfully! (Second Follow Up)')

  for name_second_follow_up, address, email_address_second_follow_up in zip(df_leads['First Name'], df_leads['Address'], df_leads['Email']):
    GenerateSecondEmail(name_second_follow_up, address, email_address_second_follow_up)

read_email_from_gmail()




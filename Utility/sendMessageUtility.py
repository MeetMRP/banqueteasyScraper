from fastapi import HTTPException
from datetime import date, timedelta, datetime
from dbModel import Enquiry
from sqlalchemy import update
import requests
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()


async def send_email_notification(exception, number):
    # Compose the email content
    subject = "Exception Report"
    body = f"An exception occurred while sending a WhatsApp message to {number}:\n\n{str(exception)}"
    sender_email = os.getenv('Mail_USERNAME')
    receiver_email = "malharlakdawala@gmail.com"
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Connect to the SMTP server and send the email
    smtp_server = os.getenv('Mail_HOST')
    smtp_port = os.getenv('Mail_PORT')
    smtp_username = os.getenv('Mail_USERNAME')
    smtp_password = os.getenv('Mail_PASSWORD')

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


async def pushMessage(number, message):

    url = "https://whatsapp.leadzen.ai/api/send.php/"
    params = {
        "number": f'91{number}',
        "type": 'text',
        "message": message,
        "instance_id": os.getenv('INSTANCE_ID'),
        "access_token": os.getenv('ACCESS_TOKEN')
    }
    
    try:
        response = await requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        await send_email_notification(e, number)
        raise HTTPException(
            detail=f'Failed to send WhatsApp message to {number}'
        ) from e


async def sendFollowup(number, session, followUp):
    if followUp == 1:
        message = 'Thank you for visiting Club Millennium, do let me know in case you need any more information'
    elif followUp == 2:
        message = 'Hey Hi, just wanted to check an update on the inquiry you did at Millennium Club'
    elif followUp == 3:
        message = 'Hey Hi, we have received an inquiry for similar date at Millennium Club as yours, so wanted to check with you on this'
    print(f'{number}, {followUp}')

    await pushMessage(number, message)
    updateStatement = (
        update(Enquiry)
        .where(Enquiry.Contact == number)
        .values(Followup = f'{followUp}')  
    )
    session.execute(updateStatement)
    session.commit()


async def sendWaMessage(results, session):
    currentDate = date.today().strftime('%d-%b-%Y')
    print(currentDate)

    for result in results:
        number = result[0]
        currentFollowUp = int(result[2])
        enquiryDate = datetime.strptime(result[1], "%d-%b-%Y %I:%M %p").strftime("%d-%b-%Y")

        dayOne = [datetime.strptime(enquiryDate, "%d-%b-%Y"), 1]
        dayThree = [(dayOne[0] + timedelta(days=3)).strftime("%d-%b-%Y"), 2]
        daySeven = [(dayOne[0] + timedelta(days=7)).strftime("%d-%b-%Y"), 3]

        for Date in [dayOne, dayThree, daySeven]:
            if currentDate == Date[0] and currentFollowUp < Date[1]:
                await sendFollowup(number, session, Date[1])
from fastapi import HTTPException
from datetime import date, timedelta
from dbModel import Enquiry
from sqlalchemy import update
import requests
import os
from dotenv import load_dotenv
load_dotenv()


async def getMessageNewDate(followUp):
    if followUp == '0':
        message = 'Thank you for visiting Club Millennium, do let me know in case you need any more information'
        newDate = (date.today() + timedelta(days=3)).strftime('%d-%b-%Y')
        newFollowUp = '1'

    elif followUp == '1':
        message = 'Hey Hi, just wanted to check an update on the inquiry you did at Millennium Club'
        newDate = (date.today() + timedelta(days=7)).strftime('%d-%b-%Y')
        newFollowUp = '2'

    elif followUp == '2':
        message = 'Hey Hi, we have received an inquiry for similar date at Millennium Club as yours, so wanted to check with you on this'
        newDate = '-'
        newFollowUp = '3'

    return message, newDate, newFollowUp


async def pushMessage(number, followUp, session):
    message, newDate, newFollowUp = await getMessageNewDate(followUp)

    url = "https://whatsapp.leadzen.ai/api/send.php/"
    params = {
        "number": f'91{number}',
        "type": 'text',
        "message": message,
        "instance_id": os.getenv('INSTANCE_ID'),
        "access_token": os.getenv('ACCESS_TOKEN')
    }

    response = await requests.get(url, params=params)

    if response.status != 'success':
        raise HTTPException(detail=f'Failed to send whatsapp message to {number}')
    updateStatement = (
        update(Enquiry)
        .where(Enquiry.Contact == number)
        .values(Followup = newFollowUp, Next_Call = newDate)  
    )
    session.execute(updateStatement)
    session.commit()
        


async def checkFollowUpAndSend(number, session):
    followUp = session.query(Enquiry.Followup).filter(Enquiry.Contact == number).first()[0]
    await pushMessage(number, followUp, session)


async def sendWaMessage(results, session):
    currentDate = date.today().strftime('%d-%b-%Y')
    for result in results:
        lastCall = result[1] 
        nextDate = result[2]
        if nextDate == currentDate or (lastCall == '-' and nextDate == '-'):
            number = result[0]
            await checkFollowUpAndSend(number, session)
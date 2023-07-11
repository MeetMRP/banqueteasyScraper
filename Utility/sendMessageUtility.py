from fastapi import HTTPException
from datetime import date, timedelta, datetime
from dbModel import Enquiry
from sqlalchemy import update
import requests
import os
from dotenv import load_dotenv
load_dotenv()


async def pushMessage(number, message):

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


async def sendFollowup(number, session, followUp):
    if followUp == 1:
        message = 'Thank you for visiting Club Millennium, do let me know in case you need any more information'
    elif followUp == 2:
        message = 'Hey Hi, just wanted to check an update on the inquiry you did at Millennium Club'
    elif followUp == 3:
        message = 'Hey Hi, we have received an inquiry for similar date at Millennium Club as yours, so wanted to check with you on this'
    print(f'{number}, {followUp}')

    pushMessage(number, message)
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
        enquiryDate = datetime.strptime(result[1], "%d-%b-%Y %I:%M %p").strftime("%d-%b-%Y")

        dayOne = [datetime.strptime(enquiryDate, "%d-%b-%Y"), 1]
        dayThree = [(dayOne[0] + timedelta(days=3)).strftime("%d-%b-%Y"), 2]
        daySeven = [(dayOne[0] + timedelta(days=7)).strftime("%d-%b-%Y"), 3]

        for Date in [dayOne, dayThree, daySeven]:
            if currentDate == Date[0]:
                await sendFollowup(number, session, Date[1])
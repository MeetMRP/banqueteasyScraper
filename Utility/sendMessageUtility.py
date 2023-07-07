from datetime import date, timedelta
from dbModel import Enquiry
from sqlalchemy import update

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
    print(f'message: {message}\nnewDate:{newDate}\nnewFollowUp:{newFollowUp}\n')

    #sent message
    
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
    print("currentDate: ", currentDate)
    for result in results:
        nextDate = result[1] 
        if nextDate == currentDate:
            number = result[0]
            print(number)
            await checkFollowUpAndSend(number, session)
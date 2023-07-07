from fastapi import FastAPI
import httpx
import time
import asyncio
from Utility.loadDbUtility import loadData, totalPageCount
from Utility.sendMessageUtility import sendWaMessage
from dbModel import Session, Enquiry
import os
from dotenv import load_dotenv
load_dotenv()


logInUrl = 'https://www.banqueteasy.com/access'
logInPayload = {
    'username': os.getenv('USERNAME_BANQUETE'),
    'pwd': os.getenv('PASSWORD_BANQUETE')
}

enquiriesUrl = 'https://www.banqueteasy.com/erp/main.php?Pg=enquiries'


app = FastAPI()


@app.get("/")
async def root():
    return {
        'Load DB': '/addData',
        'Sent message': '/sendMessage'
    }


@app.get("/addData")
async def addData():
    start_time = time.time()
    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:

        await client.post(logInUrl, data=logInPayload) #login request
        response = await client.get(enquiriesUrl, params={'pgn': 1}) #request for pg count

        totalPages = await totalPageCount(response)

        reqs = [client.get(enquiriesUrl, params={'pgn': page}) for page in totalPages]
        responses = await asyncio.gather(*reqs)

        for response in responses:
            await loadData(response)

    return {
        "Message": "Success", 
        "Response time": f"{time.time() - start_time}", 
    }


@app.get("/sendMessage")
async def sendMessage():
    session = Session()
    results = session.query(Enquiry.Contact, Enquiry.Next_Call).filter(Enquiry.Status != 'Not Interested', Enquiry.Status != 'Converted', Enquiry.Followup != '3').all()

    await sendWaMessage(results, session)

    return {
        "Message": "Success"
    }
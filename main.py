from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
import httpx
import time
import asyncio
from Utility.loadDbUtility import loadData, totalPageCount
from Utility.sendMessageUtility import sendWaMessage
from dbModel import Session, Enquiry
from sqlalchemy import func
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
        'Sent message': '/sendMessage',
        'Get data': '/getData',
    }


@app.get("/addData")
async def addData():
    start_time = time.time()
    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        
        loginResponse = await client.post(logInUrl, data=logInPayload) #login to site

        if loginResponse.headers.get("location") is None:
            raise HTTPException(status_code=401, detail="Incorrect Username, Password")
        
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
    results = session.query(Enquiry.Contact, Enquiry.Enquiry_Date, Enquiry.Followup).filter(    
        Enquiry.Status.notin_(['Not Interested', 'Converted']),
        Enquiry.Followup.in_(['0', '1', '2'])
    ).all()

    await sendWaMessage(results, session)

    return {
        "Message": "Success"
    }


@app.get("/getData")
async def getData():
    session = Session()
    results = session.query(Enquiry.Fullname, Enquiry.Contact, Enquiry.Enquiry_Date, Enquiry.Status, Enquiry.Followup).all()

    json_results = [
        {
            "Fullname": fullname,
            "Contact": contact,
            "Enquiry Date": enquiry_date,
            "Status": status,
            "Followup": followup,
        }
        for fullname, contact, enquiry_date, status, followup in results
    ]
    count = session.query(func.count()).select_from(Enquiry).scalar()
    return jsonable_encoder({
        "Count": count,
        "Results": json_results,
    })
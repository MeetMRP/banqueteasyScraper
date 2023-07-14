from fastapi import FastAPI, HTTPException
import httpx
import time
import asyncio
from Utility.loadDbUtility import collectData, totalPageCount, bulkLoad
from Utility.sendMessageUtility import sendWaMessage
import motor.motor_asyncio
import os
from dotenv import load_dotenv
load_dotenv()


logInUrl = 'https://www.banqueteasy.com/access'
logInPayload = {
    'username': os.getenv('USERNAME_BANQUETE'),
    'pwd': os.getenv('PASSWORD_BANQUETE')
}

enquiriesUrl = 'https://www.banqueteasy.com/erp/main.php?Pg=enquiries'

API_CONFIG_MONGODB_URL = os.getenv(
    "API_CONFIG_MONGODB_URL"
)

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

        insertList = []
        for response in responses:
            insertList.extend(await collectData(response))
        
        testSet = {i['Contact'] for i in insertList}
        print("testSet: ", len(testSet))

        await bulkLoad(insertList)

    return {
        "Message": "Success", 
        "Response time": f"{time.time() - start_time}", 
    }


@app.get("/sendMessage")
async def sendMessage():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        API_CONFIG_MONGODB_URL,
        maxPoolSize=10
    )
    db = client['leadzen_banqueteasy']
    collection = db['enquiries']

    results = await collection.find(
        {
            'Status': {'$nin': ['Not Interested', 'Converted']},
            'Followup': {'$in': ['0', '1', '2']}
        },
        {
            'Contact': 1,
            'Enquiry_Date': 1,
            'Followup': 1
        }
    ).to_list(None)

    await sendWaMessage(results, collection)

    return {
        "Message": "Success"
    }


@app.get("/getData")
async def getData():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        API_CONFIG_MONGODB_URL,
        maxPoolSize=10
    )
    db = client['leadzen_banqueteasy']
    collection = db['enquiries']

    results = await collection.find({}, {'Fullname': 1, 'Contact': 1, 'Enquiry_Date': 1, 'Status': 1, 'Followup': 1}).to_list(None)
    json_results = [
        {
            "Fullname": result['Fullname'],
            "Contact": result['Contact'],
            "Enquiry Date": result['Enquiry_Date'],
            "Status": result['Status'],
            "Followup": result['Followup']
        }
        for result in results
    ]
    count = await collection.count_documents({})
    return {
        "Count": count,
        "Results": json_results
    }
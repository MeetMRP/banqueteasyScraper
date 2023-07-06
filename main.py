from fastapi import FastAPI
import httpx
import time
import asyncio
from Utility.loadDbUtility import loadData, totalPageCount, dataAdded
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
    }


@app.get("/addData")
async def root():
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
    return {"message": "Success", "Response time": f"{time.time() - start_time}", "Number of New data added": dataAdded}
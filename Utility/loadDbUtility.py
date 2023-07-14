from bs4 import BeautifulSoup
import motor.motor_asyncio
from pymongo import errors
import os
from dotenv import load_dotenv
load_dotenv()

API_CONFIG_MONGODB_URL = os.getenv(
    "API_CONFIG_MONGODB_URL"
)
async def chechNumber(number):
    number = number.replace(' ', '').replace('+91', '')
    return number if len(number) == 10 else False


async def collectData(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find('tbody').findChildren('tr')

    insertList = []
    for row in rows:
        columns = row.find_all('td')
        selectedColumns = columns[1:2] +columns[3:11] + columns[14:17]
        data = [column.text.strip() for column in selectedColumns]
        data[1] = await chechNumber(data[1])
        if not data[1]:
            continue
        enquiryData = {
            'Fullname': data[0],
            'Contact': data[1],
            'Pax': data[2],
            'Banquets': data[3],
            'Event': data[4],
            'Enquiry_Date': data[5],
            'Event_Date': data[6],
            'User': data[7],
            'Owners': data[8],
            'Lead_Source': data[9],
            'Status': data[10],
            'Followup': data[11]
        }
        insertList.append(enquiryData)

    return insertList


async def bulkLoad(insertList):

    client = motor.motor_asyncio.AsyncIOMotorClient(
        API_CONFIG_MONGODB_URL,
        maxPoolSize=10
    )
    db = client['leadzen_banqueteasy']
    collection = db['enquiries']

    await collection.create_index('Contact', unique=True)
    for insert in insertList:
        contact = insert['Contact']
        if await collection.find_one({'Contact': contact}) is None:
            try:
                await collection.insert_one(insert)
            except errors.BulkWriteError as e:
                for error in e.details['writeErrors']:
                    print(f"Error: {error}")


async def totalPageCount(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    li = soup.find('ul', {'class': 'pagination default'}).findChildren('li')
    return range(1, int(li[-2].text.strip()) + 1)
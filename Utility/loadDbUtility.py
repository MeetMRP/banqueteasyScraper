from dbModel import Session, Enquiry
from sqlalchemy import exists
from bs4 import BeautifulSoup
from datetime import timedelta, datetime


async def chechNumber(number):
    number = number.replace(' ', '').replace('+91', '')
    return number if len(number) == 10 else False


async def setData(data):
    last_call = data[9]

    if last_call != '-':
        next_call = data[10]
        follow_up = data[13]
        dateFormat = '%d-%b-%Y'
        if follow_up == '1':
            next_call = (datetime.strptime(last_call, dateFormat) + timedelta(days=3)).strftime(dateFormat)
            data[10] = next_call
        elif follow_up == '2':
            next_call = (datetime.strptime(last_call, dateFormat) + timedelta(days=7)).strftime(dateFormat)
            data[10] = next_call

    return data
    



async def loadData(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find('tbody').findChildren('tr')
    
    session = Session()
    for row in rows:
        columns = row.find_all('td')
        selectedColumns = columns[1:2] +columns[3:11] + columns[12:17]
        data = [column.text.strip() for column in selectedColumns]
        data[1] = await chechNumber(data[1])
        if not data[1]:
            continue

        next_call = data[10]
        follow_up = data[13]
        if next_call == '-' and follow_up != '3':
            data = await setData(data)

        q = session.query(exists().where(Enquiry.Contact == data[1])).subquery()
        if not session.query(q).scalar():
            session.add(Enquiry(*data))
            session.commit()


async def totalPageCount(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    li = soup.find('ul', {'class': 'pagination default'}).findChildren('li')
    return range(1, int(li[-2].text.strip()) + 1)
from dbModel import Session, Enquiry
from sqlalchemy import exists
from bs4 import BeautifulSoup
dataAdded=0


async def loadData(response):
    global dataAdded 
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find('tbody').findChildren('tr')
    
    session = Session()
    for row in rows:
        columns = row.find_all('td')
        selectedColumns = columns[1:2] + columns[3:11] + columns[12:17]
        data = [column.text.strip() for column in selectedColumns]
        print(data)
        q = session.query(exists().where(Enquiry.Contact == data[1])).subquery()
        if not session.query(q).scalar():
            session.add(Enquiry(*data))
            session.commit()
            dataAdded+=1


async def totalPageCount(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    li = soup.find('ul', {'class': 'pagination default'}).findChildren('li')
    return range(1, int(li[-2].text.strip()) + 1)
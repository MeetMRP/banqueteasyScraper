from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Enquiry(Base):
    __tablename__ = 'enquiries'

    Fullname = Column('Fullname', String, nullable=True)
    Contact = Column('Contact', String, primary_key=True)
    Pax = Column('Pax', String, nullable=True)
    Banquets = Column('Banquets', String, nullable=True)
    Event = Column('Event', String, nullable=True)
    Enquiry_Date = Column('Enquiry Date', String, nullable=True)
    Event_Date = Column('Event Date', String, nullable=True)
    User = Column('User', String, nullable=True)
    Owners = Column('Owners', String, nullable=True)
    Lead_Source = Column('Lead Source', String, nullable=True)
    Status = Column('Status', String, nullable=True)
    Followup = Column('Followup', String, nullable=True)

    def __init__(self, Fullname, Contact, Pax, Banquets, Event, Enquiry_Date, Event_Date, User, Owners, Lead_Source, Status, Followup):
        self.Fullname = Fullname
        self.Contact = Contact
        self.Pax = Pax
        self.Banquets = Banquets
        self.Event = Event
        self.Enquiry_Date = Enquiry_Date
        self.Event_Date = Event_Date
        self.User = User
        self.Owners = Owners
        self.Lead_Source = Lead_Source 
        self.Status = Status
        self.Followup =  Followup

engine = create_engine('sqlite:///enquiries.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
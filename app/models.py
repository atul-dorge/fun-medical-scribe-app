from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Visit(Base):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    transcript = Column(Text)
    soap_note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

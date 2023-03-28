from sqlalchemy import Column, Integer, String, Float
from database import Base


class Address(Base):
    __tablename__ = "address"

    user_id = Column(Integer, primary_key=True, index=True)
    street = Column(String)
    city = Column(String)
    lat = Column(Float)
    lon = Column(Float)

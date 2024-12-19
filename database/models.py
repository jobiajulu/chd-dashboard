from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Hospital(Base):
    __tablename__ = 'hospitals'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url_id = Column(String)  # The 50XYZ identifier from the URL
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mortality_data = relationship("MortalityData", back_populates="hospital")

class MortalityData(Base):
    __tablename__ = 'mortality_data'

    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey('hospitals.id'))
    category = Column(String)  # e.g., 'Overall', 'STAT 1', etc.
    time_period = Column(String)  # e.g., 'January 2020 - December 2023'
    
    # Statistics
    total_cases = Column(Integer)
    mortalities = Column(Integer)
    observed_mortality_rate = Column(Float)
    expected_mortality_rate = Column(Float)
    oe_ratio = Column(Float)
    oe_ratio_lower = Column(Float)
    oe_ratio_upper = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="mortality_data")

def init_db(db_url='sqlite:///hospitals.db'):
    """Initialize the database"""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

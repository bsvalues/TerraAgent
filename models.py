import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app import db

class Property(db.Model):
    """
    Model representing property data in the CAMA system.
    Contains basic property identification and characteristics.
    """
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    parcel_id = Column(String(20), unique=True, nullable=False, index=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    neighborhood_code = Column(String(10), index=True)
    land_area = Column(Float)  # in square feet
    property_class = Column(String(50))  # residential, commercial, etc.
    year_built = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    total_area = Column(Float)  # total built area in square feet
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="property")
    sales = relationship("Sale", back_populates="property")
    
    def __repr__(self):
        return f"<Property {self.parcel_id}: {self.address}>"


class Assessment(db.Model):
    """
    Model representing property assessment data.
    Contains valuation data and assessment details.
    """
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    assessment_year = Column(Integer, nullable=False)
    land_value = Column(Float, nullable=False)
    improvement_value = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessor_id = Column(Integer)
    exemptions = Column(Text)  # JSON string of applicable exemptions
    tax_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment {self.id}: {self.assessment_year} - ${self.total_value}>"


class Sale(db.Model):
    """
    Model representing property sales data.
    Contains transaction details and sale information.
    """
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    sale_price = Column(Float, nullable=False)
    buyer_name = Column(String(255))
    seller_name = Column(String(255))
    transaction_type = Column(String(50))  # arm's length, foreclosure, etc.
    deed_type = Column(String(50))
    validation_flag = Column(Boolean, default=True)  # indicates if sale is valid for comp analysis
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    property = relationship("Property", back_populates="sales")
    
    def __repr__(self):
        return f"<Sale {self.id}: {self.sale_date.strftime('%Y-%m-%d')} - ${self.sale_price}>"


class Neighborhood(db.Model):
    """
    Model representing neighborhood data.
    Contains neighborhood characteristics and analysis.
    """
    __tablename__ = 'neighborhoods'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    average_value = Column(Float)
    median_value = Column(Float)
    value_trend = Column(Float)  # percentage change YoY
    total_properties = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Neighborhood {self.code}: {self.name}>"


class Document(db.Model):
    """
    Model representing document metadata for retrieval.
    Used for RAG functionality.
    """
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    document_type = Column(String(50))  # report, regulation, memo, etc.
    source_url = Column(String(255))
    published_date = Column(DateTime)
    vector_id = Column(String(100))  # ID in the vector store
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Document {self.id}: {self.title}>"


class QueryLog(db.Model):
    """
    Model for logging user queries and system responses.
    Used for monitoring and analytics.
    """
    __tablename__ = 'query_logs'
    
    id = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # SQL, RAG, levy, trends, dbatools
    response_text = Column(Text)
    response_time = Column(Float)  # in seconds
    status = Column(String(50))  # success, error
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<QueryLog {self.id}: {self.query_type} - {self.status}>"
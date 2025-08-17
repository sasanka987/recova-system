from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ClientType(enum.Enum):
    BANK = "BANK"
    NBFI = "NBFI"
    #LEASING = "LEASING"
    #FINANCE = "FINANCE"
    OTHER = "OTHER"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    client_code = Column(String(10), unique=True, nullable=False, index=True)
    client_name = Column(String(255), nullable=False, index=True)
    client_type = Column(Enum(ClientType), nullable=False, index=True)

    # Contact Information
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    address = Column(Text)

    # Business Information
    registration_number = Column(String(50))
    tax_id = Column(String(50))
    website = Column(String(255))

    # System Information
    is_active = Column(Boolean, default=True, index=True)
    logo_path = Column(String(500))

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)

    # Relationships
    customers = relationship("Customer", back_populates="client")
    import_batches = relationship("ImportBatch", back_populates="client")

    def __repr__(self):
        return f"<Client(code={self.client_code}, name={self.client_name})>"
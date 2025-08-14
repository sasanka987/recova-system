from sqlalchemy import Column, Integer, String, Text, Date, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Import tracking
    import_batch_id = Column(Integer, nullable=True)  # Made nullable

    # Personal Information
    client_name = Column(String(255), nullable=False)
    nic = Column(String(20), unique=True, nullable=False, index=True)
    home_address = Column(Text, nullable=True)  # Made nullable

    # Contact Details
    customer_contact_number_1 = Column(String(20), nullable=True)
    customer_contact_number_2 = Column(String(20), nullable=True)
    customer_contact_number_3 = Column(String(20), nullable=True)

    # Contract Information
    contract_number = Column(String(100), nullable=False, index=True)
    granted_amount = Column(DECIMAL(15, 2), nullable=True)  # Made nullable
    facility_granted_date = Column(Date, nullable=True)
    facility_end_date = Column(Date, nullable=True)

    # Employment
    designation = Column(String(100), nullable=True)
    work_place_name = Column(String(255), nullable=True)
    work_place_address = Column(Text, nullable=True)
    work_place_contact_number_1 = Column(String(20), nullable=True)
    work_place_contact_number_2 = Column(String(20), nullable=True)
    work_place_contact_number_3 = Column(String(20), nullable=True)

    # Financial
    monthly_rental_payment_with_vat = Column(DECIMAL(12, 2), nullable=True)
    last_payment_date = Column(Date, nullable=True)
    last_payment_amount = Column(DECIMAL(12, 2), nullable=True)
    due_date = Column(Date, index=True, nullable=True)

    # Guarantor Information (Two guarantors)
    guarantor_1_name = Column(String(255), nullable=True)
    guarantor_1_address = Column(Text, nullable=True)
    guarantor_1_nic = Column(String(20), nullable=True)
    guarantor_1_contact_number_1 = Column(String(20), nullable=True)
    guarantor_1_contact_number_2 = Column(String(20), nullable=True)
    guarantor_2_name = Column(String(255), nullable=True)
    guarantor_2_address = Column(Text, nullable=True)
    guarantor_2_nic = Column(String(20), nullable=True)
    guarantor_2_contact_number_1 = Column(String(20), nullable=True)
    guarantor_2_contact_number_2 = Column(String(20), nullable=True)

    # Location
    zone = Column(String(100), index=True, nullable=True)
    region = Column(String(100), index=True, nullable=True)
    branch_name = Column(String(100), nullable=True)
    district_name = Column(String(100), nullable=True)
    postal_town = Column(String(100), nullable=True)

    # Status
    days_in_arrears = Column(Integer, default=0)
    details = Column(Text, nullable=True)
    payment_assumption = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
# app/models/customer.py - CORRECTED VERSION
from sqlalchemy import Column, Integer, String, Text, Date, DECIMAL, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Client and Contract Information (THE KEY CHANGE!)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True, comment='Reference to clients table')
    contract_number = Column(String(100), nullable=False, index=True, comment='Contract number unique per client')

    # Personal Information
    client_name = Column(String(255), nullable=False, index=True, comment='Customer full name')
    nic = Column(String(20), nullable=False, index=True, comment='National Identity Card number')
    home_address = Column(Text, comment='Residential address')

    # Contact Details
    customer_contact_number_1 = Column(String(20), comment='Primary contact number')
    customer_contact_number_2 = Column(String(20), comment='Secondary contact number')
    customer_contact_number_3 = Column(String(20), comment='Tertiary contact number')

    # Financial Information
    granted_amount = Column(DECIMAL(15, 2), comment='Original granted amount')
    facility_granted_date = Column(Date, comment='Facility grant date')
    facility_end_date = Column(Date, comment='Facility end date')
    monthly_rental_payment_with_vat = Column(DECIMAL(12, 2), comment='Monthly payment amount')
    last_payment_date = Column(Date, comment='Last payment received date')
    last_payment_amount = Column(DECIMAL(12, 2), comment='Last payment amount')
    due_date = Column(Date, index=True, comment='Next payment due date')

    # Employment Information
    designation = Column(String(100), comment='Job title')
    work_place_name = Column(String(255), comment='Employer name')
    work_place_address = Column(Text, comment='Work address')
    work_place_contact_number_1 = Column(String(20), comment='Work contact number')
    work_place_contact_number_2 = Column(String(20), comment='Work contact number 2')
    work_place_contact_number_3 = Column(String(20), comment='Work contact number 3')

    # Guarantor 1 Information
    guarantor_1_name = Column(String(255), comment='First guarantor name')
    guarantor_1_address = Column(Text, comment='First guarantor address')
    guarantor_1_nic = Column(String(20), comment='First guarantor NIC')
    guarantor_1_contact_number_1 = Column(String(20), comment='First guarantor contact')
    guarantor_1_contact_number_2 = Column(String(20), comment='First guarantor contact 2')

    # Guarantor 2 Information
    guarantor_2_name = Column(String(255), comment='Second guarantor name')
    guarantor_2_address = Column(Text, comment='Second guarantor address')
    guarantor_2_nic = Column(String(20), comment='Second guarantor NIC')
    guarantor_2_contact_number_1 = Column(String(20), comment='Second guarantor contact')
    guarantor_2_contact_number_2 = Column(String(20), comment='Second guarantor contact 2')

    # Location Information
    zone = Column(String(100), index=True, comment='Geographic zone')
    region = Column(String(100), index=True, comment='Geographic region')
    branch_name = Column(String(100), comment='Bank branch name')
    district_name = Column(String(100), comment='District name')
    postal_town = Column(String(100), comment='Postal town')

    # Status Information
    days_in_arrears = Column(Integer, default=0, index=True, comment='Days overdue')
    details = Column(Text, comment='Additional details')
    payment_assumption = Column(String(255), comment='Payment assumptions')

    # Import and Audit Information
    import_batch_id = Column(Integer, ForeignKey("import_batches.id"), comment='Import batch reference')
    created_at = Column(DateTime, server_default=func.now(), comment='Record creation time')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='Last update time')
    created_by = Column(Integer, ForeignKey("users.id"), comment='Creating user ID')

    # Relationships
    client = relationship("Client", back_populates="customers")
    import_batch = relationship("ImportBatch", back_populates="customers")
    created_by_user = relationship("User")

    # Composite unique constraint and indexes
    __table_args__ = (
        Index('idx_unique_client_contract', 'client_id', 'contract_number', unique=True),
        Index('idx_client_contract', 'client_id', 'contract_number'),
        Index('idx_nic_client', 'nic', 'client_id'),
        Index('idx_zone_region', 'zone', 'region'),
        Index('idx_search_fields', 'client_id', 'client_name', 'contract_number'),
    )

    def __repr__(self):
        return f"<Customer(client_id={self.client_id}, contract={self.contract_number}, name={self.client_name})>"
from sqlalchemy import Column, Integer, String, Date, DECIMAL, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    # Import tracking
    import_batch_id = Column(Integer)  # Will add FK later when ImportBatch exists

    # Payment details
    payment_date = Column(Date, nullable=False, index=True)
    contract_number = Column(String(100), nullable=False, index=True)
    account_number = Column(String(50), index=True)
    customer_nic = Column(String(20), index=True)

    receipt_number = Column(String(100))
    payment_type = Column(String(50))
    payment_amount = Column(DECIMAL(12, 2), nullable=False)
    current_total_arrears = Column(DECIMAL(15, 2))

    # Bank reference information
    bank_reference_number = Column(String(100))
    payment_method = Column(String(50))  # Cash, Cheque, Transfer, etc.
    branch_name = Column(String(100))
    payment_remarks = Column(Text)

    # Matching information
    matched_customer_id = Column(Integer, ForeignKey("customers.id"))
    match_type = Column(String(50))  # CONTRACT_NUMBER_MATCH, ACCOUNT_NUMBER_MATCH, NIC_MATCH, NO_MATCH
    is_matched = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    customer = relationship("Customer")
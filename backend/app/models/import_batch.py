# app/models/import_batch.py - FIXED FILE WITH ImportError CLASS
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class ImportStatus(enum.Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    IMPORTING = "IMPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLBACK = "ROLLBACK"


class OperationType(enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    LOAN = "LOAN"
    LEASING = "LEASING"
    PAYMENT = "PAYMENT"


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String(255), nullable=False)

    # Client Information (UPDATED!)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)  # Made nullable for existing data
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(20))

    operation_type = Column(Enum(OperationType), nullable=False)
    import_period = Column(String(20), nullable=False)
    import_month = Column(Integer, nullable=False)
    import_year = Column(Integer, nullable=False)

    # File information
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(500))
    file_checksum = Column(String(64))

    # Import statistics
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    imported_records = Column(Integer, default=0)

    # Status and timing
    status = Column(Enum(ImportStatus), default=ImportStatus.UPLOADED)
    imported_by = Column(Integer, ForeignKey("users.id"))
    import_started_at = Column(DateTime)
    import_completed_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="import_batches")
    import_errors = relationship("ImportError", back_populates="batch")
    customers = relationship("Customer", back_populates="import_batch")
    imported_by_user = relationship("User")

    def __repr__(self):
        return f"<ImportBatch(id={self.id}, client={self.client_id}, type={self.operation_type})>"


class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    column_name = Column(String(100))
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    original_value = Column(Text)
    suggested_value = Column(Text)
    is_critical = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    batch = relationship("ImportBatch", back_populates="import_errors")

    def __repr__(self):
        return f"<ImportError(batch_id={self.batch_id}, row={self.row_number}, type={self.error_type})>"


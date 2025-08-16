# app/schemas/import_batch.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ImportStatusEnum(str, Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    IMPORTING = "IMPORTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLBACK = "ROLLBACK"


class OperationTypeEnum(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    LOAN = "LOAN"
    LEASING = "LEASING"
    PAYMENT = "PAYMENT"


class ImportBatchResponse(BaseModel):
    id: int
    batch_name: str
    bank_name: str
    operation_type: OperationTypeEnum  # Fixed: Changed from ImportStatusEnum to OperationTypeEnum
    import_period: str
    file_name: str
    file_size: int
    total_records: int
    valid_records: int
    invalid_records: int
    imported_records: int
    status: ImportStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    message: str
    batch_id: int
    file_name: str
    file_size: int
    next_step: str


class ImportErrorResponse(BaseModel):
    id: int
    batch_id: int
    row_number: int
    column_name: Optional[str] = None
    error_type: str
    error_message: str
    original_value: Optional[str] = None
    suggested_value: Optional[str] = None
    is_critical: bool

    class Config:
        from_attributes = True
# app/models/__init__.py - FIXED IMPORTS
from app.db.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.client import Client, ClientType  # NEW
from app.models.customer import Customer  # UPDATED
from app.models.import_batch import ImportBatch, ImportError, ImportStatus, OperationType  # FIXED
from app.models.payment import Payment

# Export all models
__all__ = [
    "Base",
    "User", 
    "Role",
    "Client",        # NEW
    "ClientType",    # NEW
    "Customer",      # UPDATED
    "ImportBatch", 
    "ImportError",   # THIS WAS MISSING!
    "ImportStatus", 
    "OperationType",
    "Payment"
]


# app/schemas/client.py - NEW SCHEMA FILE
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.client import ClientType


class ClientBase(BaseModel):
    client_code: str
    client_name: str
    client_type: ClientType
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True

    @validator('client_code')
    def validate_client_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Client code cannot be empty')
        return v.upper().strip()

    @validator('client_name')
    def validate_client_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Client name cannot be empty')
        return v.strip()


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    client_code: Optional[str] = None
    client_name: Optional[str] = None
    client_type: Optional[ClientType] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientWithStats(ClientResponse):
    customer_count: int = 0
    active_contracts: int = 0
    total_outstanding: float = 0

    class Config:
        from_attributes = True
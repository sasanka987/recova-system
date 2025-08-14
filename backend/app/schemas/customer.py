from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CustomerResponse(BaseModel):
    id: int
    client_name: str
    nic: str
    home_address: Optional[str] = None
    contract_number: str
    granted_amount: Optional[Decimal] = None
    zone: Optional[str] = None
    region: Optional[str] = None
    branch_name: Optional[str] = None
    days_in_arrears: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True
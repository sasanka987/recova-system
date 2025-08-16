# app/schemas/customer.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CustomerBase(BaseModel):
    client_name: str
    nic: str
    contract_number: str
    home_address: Optional[str] = None

    # Contact Information
    customer_contact_number_1: Optional[str] = None
    customer_contact_number_2: Optional[str] = None
    customer_contact_number_3: Optional[str] = None

    # Financial Information
    granted_amount: Optional[Decimal] = None
    facility_granted_date: Optional[date] = None
    facility_end_date: Optional[date] = None
    monthly_rental_payment_with_vat: Optional[Decimal] = None
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None
    due_date: Optional[date] = None

    # Employment Information
    designation: Optional[str] = None
    work_place_name: Optional[str] = None
    work_place_address: Optional[str] = None
    work_place_contact_number_1: Optional[str] = None
    work_place_contact_number_2: Optional[str] = None
    work_place_contact_number_3: Optional[str] = None

    # Location Information
    zone: Optional[str] = None
    region: Optional[str] = None
    branch_name: Optional[str] = None
    district_name: Optional[str] = None
    postal_town: Optional[str] = None

    # Status Information
    days_in_arrears: Optional[int] = 0
    details: Optional[str] = None
    payment_assumption: Optional[str] = None

    # Guarantor 1 Information
    guarantor_1_name: Optional[str] = None
    guarantor_1_address: Optional[str] = None
    guarantor_1_nic: Optional[str] = None
    guarantor_1_contact_number_1: Optional[str] = None
    guarantor_1_contact_number_2: Optional[str] = None

    # Guarantor 2 Information
    guarantor_2_name: Optional[str] = None
    guarantor_2_address: Optional[str] = None
    guarantor_2_nic: Optional[str] = None
    guarantor_2_contact_number_1: Optional[str] = None
    guarantor_2_contact_number_2: Optional[str] = None

    @validator('nic')
    def validate_nic(cls, v):
        if v:
            # Sri Lankan NIC validation
            v = v.strip().upper()
            # Old format: 9 digits + V/X or New format: 12 digits
            if not ((len(v) == 10 and v[:-1].isdigit() and v[-1] in 'VX') or
                    (len(v) == 12 and v.isdigit())):
                raise ValueError('Invalid NIC format')
        return v


class CustomerCreate(CustomerBase):
    import_batch_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    # All fields optional for updates
    home_address: Optional[str] = None
    customer_contact_number_1: Optional[str] = None
    customer_contact_number_2: Optional[str] = None
    customer_contact_number_3: Optional[str] = None
    work_place_name: Optional[str] = None
    work_place_address: Optional[str] = None
    work_place_contact_number_1: Optional[str] = None
    work_place_contact_number_2: Optional[str] = None
    work_place_contact_number_3: Optional[str] = None
    payment_assumption: Optional[str] = None
    details: Optional[str] = None
    days_in_arrears: Optional[int] = None
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None


class CustomerResponse(BaseModel):
    id: int
    client_name: str
    nic: str
    contract_number: str
    home_address: Optional[str] = None
    customer_contact_number_1: Optional[str] = None
    zone: Optional[str] = None
    region: Optional[str] = None
    branch_name: Optional[str] = None
    days_in_arrears: Optional[int] = 0
    granted_amount: Optional[Decimal] = None
    work_place_name: Optional[str] = None
    last_payment_date: Optional[date] = None
    last_payment_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    import_batch_id: Optional[int] = None

    class Config:
        from_attributes = True


class CustomerStatistics(BaseModel):
    total_customers: int
    arrears_breakdown: dict
    zone_distribution: list
    total_outstanding_amount: float
    average_days_in_arrears: float
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse

router = APIRouter()


@router.get("/test-no-auth")
async def test_without_auth():
    """Test endpoint that doesn't require authentication"""
    return {
        "message": "This endpoint works without authentication!",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/test-auth-simple")
async def test_auth_simple(current_user: User = Depends(get_current_user)):
    """Simple auth test - just return user info"""
    return {
        "message": "Authentication working!",
        "user_email": current_user.email,
        "user_id": current_user.id,
        "user_status": current_user.status,
        "success": True
    }


@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        search: Optional[str] = Query(None, description="Search by name, NIC, or contract number"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get list of customers with filtering and search"""

    query = db.query(Customer)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.client_name.like(search_term)) |
            (Customer.nic.like(search_term)) |
            (Customer.contract_number.like(search_term))
        )

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get specific customer by ID"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.post("/create-test-data")
async def create_test_customers(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create some test customers for testing (temporary endpoint)"""

    test_customers = [
        {
            "client_name": "John Doe",
            "nic": "123456789V",
            "home_address": "123 Main Street, Colombo 03",
            "contract_number": "CC001234567",
            "granted_amount": 500000.00,
            "zone": "Colombo",
            "region": "Western",
            "branch_name": "Colombo Central",
            "days_in_arrears": 15,
            "customer_contact_number_1": "0771234567"
        },
        {
            "client_name": "Jane Smith",
            "nic": "987654321V",
            "home_address": "456 Oak Road, Kandy",
            "contract_number": "LN987654321",
            "granted_amount": 1000000.00,
            "zone": "Kandy",
            "region": "Central",
            "branch_name": "Kandy Main",
            "days_in_arrears": 30,
            "customer_contact_number_1": "0712345678"
        },
        {
            "client_name": "Mike Johnson",
            "nic": "456789123V",
            "home_address": "789 Beach Road, Galle",
            "contract_number": "LS456789123",
            "granted_amount": 750000.00,
            "zone": "Galle",
            "region": "Southern",
            "branch_name": "Galle Fort",
            "days_in_arrears": 5,
            "customer_contact_number_1": "0723456789"
        }
    ]

    created_customers = []
    for customer_data in test_customers:
        try:
            # Check if customer already exists
            existing = db.query(Customer).filter(Customer.nic == customer_data["nic"]).first()
            if not existing:
                customer = Customer(**customer_data)
                db.add(customer)
                created_customers.append(customer_data["client_name"])
        except Exception as e:
            print(f"Error creating customer {customer_data['client_name']}: {e}")
            continue

    db.commit()

    return {
        "message": f"Created {len(created_customers)} test customers",
        "customers": created_customers,
        "total_customers": len(test_customers),
        "note": "You can now test the /customers/ endpoint to see the data",
        "success": True
    }
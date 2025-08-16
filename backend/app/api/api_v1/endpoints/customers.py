# app/api/api_v1/endpoints/customers.py
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, date

from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate, CustomerDetailResponse
from decimal import Decimal

router = APIRouter()


def serialize_customer(customer):
    """Helper function to serialize customer data, handling NaN and None values"""
    data = {}
    for column in customer.__table__.columns:
        value = getattr(customer, column.name)

        # Handle Decimal types
        if isinstance(value, Decimal):
            # Convert Decimal to float, handling None
            data[column.name] = float(value) if value is not None else None
        # Handle float types with NaN check
        elif isinstance(value, float):
            # Check for NaN or Infinity
            if math.isnan(value) or math.isinf(value):
                data[column.name] = None
            else:
                data[column.name] = value
        # Handle datetime
        elif hasattr(value, 'isoformat'):
            data[column.name] = value.isoformat()
        else:
            data[column.name] = value

    return data

@router.get("/")
async def get_customers(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
        search: Optional[str] = Query(None, description="Search by name, NIC, or contract number"),
        zone: Optional[str] = Query(None, description="Filter by zone"),
        region: Optional[str] = Query(None, description="Filter by region"),
        branch: Optional[str] = Query(None, description="Filter by branch"),
        min_arrears: Optional[int] = Query(None, description="Minimum days in arrears"),
        max_arrears: Optional[int] = Query(None, description="Maximum days in arrears"),
        sort_by: Optional[str] = Query("created_at", description="Sort by field"),
        sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get list of customers with advanced filtering and search"""

    query = db.query(Customer)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.client_name.ilike(search_term),
                Customer.nic.ilike(search_term),
                Customer.contract_number.ilike(search_term),
                Customer.work_place_name.ilike(search_term),
                Customer.postal_town.ilike(search_term)
            )
        )

    # Apply location filters
    if zone:
        query = query.filter(Customer.zone == zone)
    if region:
        query = query.filter(Customer.region == region)
    if branch:
        query = query.filter(Customer.branch_name == branch)

    # Apply arrears filters
    if min_arrears is not None:
        query = query.filter(Customer.days_in_arrears >= min_arrears)
    if max_arrears is not None:
        query = query.filter(Customer.days_in_arrears <= max_arrears)

    # Apply sorting
    if hasattr(Customer, sort_by):
        order_column = getattr(Customer, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    customers = query.offset(skip).limit(limit).all()

    # Serialize customers properly
    serialized_customers = []
    for customer in customers:
        serialized_customers.append(serialize_customer(customer))

    return serialized_customers


@router.get("/statistics")
async def get_customer_statistics(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get customer statistics for dashboard"""

    total_customers = db.query(Customer).count()

    # Arrears statistics
    arrears_stats = {
        "current": db.query(Customer).filter(
            or_(Customer.days_in_arrears == 0, Customer.days_in_arrears.is_(None))
        ).count(),
        "1_30_days": db.query(Customer).filter(
            and_(Customer.days_in_arrears > 0, Customer.days_in_arrears <= 30)
        ).count(),
        "31_60_days": db.query(Customer).filter(
            and_(Customer.days_in_arrears > 30, Customer.days_in_arrears <= 60)
        ).count(),
        "61_90_days": db.query(Customer).filter(
            and_(Customer.days_in_arrears > 60, Customer.days_in_arrears <= 90)
        ).count(),
        "over_90_days": db.query(Customer).filter(Customer.days_in_arrears > 90).count()
    }

    # Zone distribution
    zone_distribution = db.query(
        Customer.zone,
        func.count(Customer.id).label('count')
    ).group_by(Customer.zone).all()

    # Total outstanding amount - handle None values
    total_outstanding = db.query(
        func.sum(Customer.granted_amount)
    ).scalar()

    # Average days in arrears - handle None values
    avg_arrears = db.query(
        func.avg(Customer.days_in_arrears)
    ).scalar()

    return {
        "total_customers": total_customers,
        "arrears_breakdown": arrears_stats,
        "zone_distribution": [
            {"zone": zone or "Unknown", "count": count}
            for zone, count in zone_distribution
        ],
        "total_outstanding_amount": float(total_outstanding) if total_outstanding else 0,
        "average_days_in_arrears": float(avg_arrears) if avg_arrears else 0
    }


@router.get("/filters")
async def get_filter_options(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get available filter options for dropdowns"""

    zones = db.query(Customer.zone).distinct().filter(Customer.zone.isnot(None)).all()
    regions = db.query(Customer.region).distinct().filter(Customer.region.isnot(None)).all()
    branches = db.query(Customer.branch_name).distinct().filter(Customer.branch_name.isnot(None)).all()

    return {
        "zones": [z[0] for z in zones if z[0]],
        "regions": [r[0] for r in regions if r[0]],
        "branches": [b[0] for b in branches if b[0]]
    }


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer_detail(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get detailed customer information"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # You can add related data here (payments, remarks, etc.)
    # For now, returning the customer data
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
        customer_id: int,
        customer_update: CustomerUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update customer information"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Update only provided fields
    update_data = customer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    customer.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(customer)

    return customer


@router.post("/", response_model=CustomerResponse)
async def create_customer(
        customer_data: CustomerCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new customer manually"""

    # Check if customer with same NIC already exists
    existing = db.query(Customer).filter(Customer.nic == customer_data.nic).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Customer with NIC {customer_data.nic} already exists"
        )

    # Check if contract number already exists
    existing_contract = db.query(Customer).filter(
        Customer.contract_number == customer_data.contract_number
    ).first()
    if existing_contract:
        raise HTTPException(
            status_code=400,
            detail=f"Contract number {customer_data.contract_number} already exists"
        )

    customer = Customer(**customer_data.dict())
    customer.created_by = current_user.id

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
async def delete_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a customer (soft delete recommended in production)"""

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check user permissions (only directors or managers should delete)
    # For now, we'll allow any authenticated user

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}


@router.get("/export/csv")
async def export_customers_csv(
        search: Optional[str] = None,
        zone: Optional[str] = None,
        region: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Export filtered customers to CSV"""

    import csv
    import io
    from fastapi.responses import StreamingResponse

    query = db.query(Customer)

    # Apply same filters as listing
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.client_name.ilike(search_term),
                Customer.nic.ilike(search_term),
                Customer.contract_number.ilike(search_term)
            )
        )

    if zone:
        query = query.filter(Customer.zone == zone)
    if region:
        query = query.filter(Customer.region == region)

    customers = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow([
        'ID', 'Client Name', 'NIC', 'Contract Number', 'Zone', 'Region',
        'Branch', 'Days in Arrears', 'Granted Amount', 'Contact Number',
        'Work Place', 'Home Address'
    ])

    # Write data
    for customer in customers:
        writer.writerow([
            customer.id,
            customer.client_name,
            customer.nic,
            customer.contract_number,
            customer.zone,
            customer.region,
            customer.branch_name,
            customer.days_in_arrears,
            customer.granted_amount,
            customer.customer_contact_number_1,
            customer.work_place_name,
            customer.home_address
        ])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type='text/csv',
        headers={
            "Content-Disposition": f"attachment; filename=customers_export_{date.today()}.csv"
        }
    )
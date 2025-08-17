import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, date

from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.client import Client
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate, CustomerDetailResponse
from decimal import Decimal

router = APIRouter()


def serialize_customer(customer):
    """Helper function to serialize customer data, handling NaN and None values"""
    data = {}
    for column in customer.__table__.columns:
        value = getattr(customer, column.name)

        if isinstance(value, Decimal):
            data[column.name] = float(value) if value is not None else None
        elif isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                data[column.name] = None
            else:
                data[column.name] = value
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
    client_id: Optional[int] = Query(None, description="Filter by client"),
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

    # Join with client information
    query = db.query(Customer).options(joinedload(Customer.client))

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

    # Apply client filter (THE KEY CHANGE!)
    if client_id:
        query = query.filter(Customer.client_id == client_id)

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

    # Serialize customers with client information
    serialized_customers = []
    for customer in customers:
        customer_data = serialize_customer(customer)
        # Add client information
        if customer.client:
            customer_data['client'] = {
                'id': customer.client.id,
                'client_code': customer.client.client_code,
                'client_name': customer.client.client_name,
                'client_type': customer.client.client_type.value
            }
        serialized_customers.append(customer_data)

    # Make sure you return a consistent format
    return {
        "customers": serialized_customers,  # Array of customers
        "total_count": total_count,
        "skip": skip,
        "limit": limit
    }


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new customer manually"""

    # Verify client exists
    client = db.query(Client).filter(Client.id == customer_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=400,
            detail=f"Client with ID {customer_data.client_id} not found"
        )

    # Check if customer with same contract number exists for this client
    existing = db.query(Customer).filter(
        Customer.client_id == customer_data.client_id,
        Customer.contract_number == customer_data.contract_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Customer with contract number {customer_data.contract_number} already exists for this client"
        )

    # Check if NIC already exists (NICs are globally unique)
    existing_nic = db.query(Customer).filter(Customer.nic == customer_data.nic).first()
    if existing_nic:
        raise HTTPException(
            status_code=400,
            detail=f"Customer with NIC {customer_data.nic} already exists"
        )

    customer = Customer(**customer_data.dict())
    customer.created_by = current_user.id

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed customer information"""

    customer = db.query(Customer).options(
        joinedload(Customer.client)
    ).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.get("/by-contract/{client_id}/{contract_number}")
async def get_customer_by_contract(
    client_id: int,
    contract_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer by client and contract number"""

    customer = db.query(Customer).options(
        joinedload(Customer.client)
    ).filter(
        Customer.client_id == client_id,
        Customer.contract_number == contract_number
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404, 
            detail=f"Customer with contract {contract_number} not found for client {client_id}"
        )

    return customer


@router.get("/statistics")
async def get_customer_statistics(
    client_id: Optional[int] = Query(None, description="Filter statistics by client"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer statistics for dashboard"""

    base_query = db.query(Customer)
    if client_id:
        base_query = base_query.filter(Customer.client_id == client_id)

    total_customers = base_query.count()

    # Arrears statistics
    arrears_stats = {
        "current": base_query.filter(
            or_(Customer.days_in_arrears == 0, Customer.days_in_arrears.is_(None))
        ).count(),
        "1_30_days": base_query.filter(
            and_(Customer.days_in_arrears > 0, Customer.days_in_arrears <= 30)
        ).count(),
        "31_60_days": base_query.filter(
            and_(Customer.days_in_arrears > 30, Customer.days_in_arrears <= 60)
        ).count(),
        "61_90_days": base_query.filter(
            and_(Customer.days_in_arrears > 60, Customer.days_in_arrears <= 90)
        ).count(),
        "over_90_days": base_query.filter(Customer.days_in_arrears > 90).count()
    }

    # Client distribution (if not filtered by client)
    if not client_id:
        client_distribution = db.query(
            Client.client_code,
            Client.client_name,
            func.count(Customer.id).label('count')
        ).join(Customer).group_by(Client.id, Client.client_code, Client.client_name).all()
    else:
        client_distribution = []

    # Zone distribution
    zone_distribution = base_query.filter(Customer.zone.isnot(None)).with_entities(
        Customer.zone,
        func.count(Customer.id).label('count')
    ).group_by(Customer.zone).all()

    # Total outstanding amount
    total_outstanding = base_query.with_entities(
        func.sum(Customer.granted_amount)
    ).scalar()

    # Average days in arrears
    avg_arrears = base_query.with_entities(
        func.avg(Customer.days_in_arrears)
    ).scalar()

    return {
        "total_customers": total_customers,
        "arrears_breakdown": arrears_stats,
        "client_distribution": [
            {"client_code": code, "client_name": name, "count": count}
            for code, name, count in client_distribution
        ],
        "zone_distribution": [
            {"zone": zone or "Unknown", "count": count}
            for zone, count in zone_distribution
        ],
        "total_outstanding_amount": float(total_outstanding) if total_outstanding else 0,
        "average_days_in_arrears": float(avg_arrears) if avg_arrears else 0
    }


@router.get("/filters")
async def get_filter_options(
    client_id: Optional[int] = Query(None, description="Filter options by client"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available filter options for dropdowns"""

    base_query = db.query(Customer)
    if client_id:
        base_query = base_query.filter(Customer.client_id == client_id)

    # Get filter options
    zones = base_query.with_entities(Customer.zone).distinct().filter(Customer.zone.isnot(None)).all()
    regions = base_query.with_entities(Customer.region).distinct().filter(Customer.region.isnot(None)).all()
    branches = base_query.with_entities(Customer.branch_name).distinct().filter(Customer.branch_name.isnot(None)).all()

    # Get clients for client filter
    clients = db.query(Client).filter(Client.is_active == True).all()

    return {
        "clients": [{"id": c.id, "code": c.client_code, "name": c.client_name} for c in clients],
        "zones": [z[0] for z in zones if z[0]],
        "regions": [r[0] for r in regions if r[0]],
        "branches": [b[0] for b in branches if b[0]]
    }
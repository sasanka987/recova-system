# app/api/api_v1/endpoints/clients.py - COMPLETE VERSION WITH FULL CRUD
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from typing import List, Optional

from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.client import Client
from app.models.customer import Customer
from app.schemas.client import ClientResponse, ClientCreate, ClientUpdate, ClientWithStats

router = APIRouter()


def check_director_permission(current_user: User):
    """Check if user has director permissions"""
    if not current_user.role or current_user.role.code != "DIRECTOR":
        raise HTTPException(
            status_code=403,
            detail="Only Directors can perform this operation"
        )


@router.get("/", response_model=List[ClientResponse])
async def get_clients(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        search: Optional[str] = Query(None, description="Search by code or name"),
        client_type: Optional[str] = Query(None, description="Filter by client type"),
        active_only: bool = Query(True, description="Show only active clients"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get list of clients with filtering"""

    query = db.query(Client)

    # Apply filters
    if active_only:
        query = query.filter(Client.is_active == True)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Client.client_code.ilike(search_term),
                Client.client_name.ilike(search_term)
            )
        )

    if client_type:
        query = query.filter(Client.client_type == client_type)

    # Order by name and apply pagination
    clients = query.order_by(Client.client_name).offset(skip).limit(limit).all()

    return clients


@router.get("/with-stats", response_model=List[ClientWithStats])
async def get_clients_with_statistics(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get clients with customer statistics"""

    # Query clients with customer counts and statistics
    results = db.query(
        Client,
        func.count(Customer.id).label('customer_count'),
        func.sum(Customer.granted_amount).label('total_outstanding')
    ).outerjoin(Customer).group_by(Client.id).all()

    clients_with_stats = []
    for client, customer_count, total_outstanding in results:
        client_data = ClientWithStats(
            **client.__dict__,
            customer_count=customer_count or 0,
            active_contracts=customer_count or 0,  # Can be refined later
            total_outstanding=float(total_outstanding or 0)
        )
        clients_with_stats.append(client_data)

    return clients_with_stats


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
        client_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get specific client by ID"""

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.post("/", response_model=ClientResponse)
async def create_client(
        client_data: ClientCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new client (Directors only)"""

    # Check director permission
    check_director_permission(current_user)

    # Check if client code already exists
    existing = db.query(Client).filter(Client.client_code == client_data.client_code).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Client with code '{client_data.client_code}' already exists"
        )

    # Create new client
    client = Client(**client_data.dict())
    client.created_by = current_user.id

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
        client_id: int,
        client_update: ClientUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update client information (Directors only)"""

    # Check director permission
    check_director_permission(current_user)

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if new client code conflicts (if being updated)
    if client_update.client_code and client_update.client_code != client.client_code:
        existing = db.query(Client).filter(
            Client.client_code == client_update.client_code,
            Client.id != client_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Client code '{client_update.client_code}' already exists"
            )

    # Update only provided fields
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client


@router.delete("/{client_id}")
async def delete_client(
        client_id: int,
        force: bool = Query(False, description="Force delete even if client has customers"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete client (Directors only)"""

    # Check director permission
    check_director_permission(current_user)

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if client has customers
    customer_count = db.query(Customer).filter(Customer.client_id == client_id).count()

    if customer_count > 0 and not force:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete client. {customer_count} customers are associated with this client. "
                   f"Use force=true to delete anyway (this will delete all associated data)."
        )

    if force and customer_count > 0:
        # Delete all associated customers first
        db.query(Customer).filter(Customer.client_id == client_id).delete()

    # Delete the client
    db.delete(client)
    db.commit()

    return {
        "message": f"Client '{client.client_name}' deleted successfully",
        "deleted_customers": customer_count if force else 0
    }


@router.get("/{client_id}/customers")
async def get_client_customers(
        client_id: int,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get customers for a specific client"""

    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get customers for this client
    customers = db.query(Customer).filter(
        Customer.client_id == client_id
    ).offset(skip).limit(limit).all()

    total_customers = db.query(Customer).filter(Customer.client_id == client_id).count()

    return {
        "client": {
            "id": client.id,
            "client_code": client.client_code,
            "client_name": client.client_name,
            "client_type": client.client_type.value
        },
        "customers": customers,
        "total_customers": total_customers,
        "showing": len(customers),
        "skip": skip,
        "limit": limit
    }


@router.post("/{client_id}/activate")
async def activate_client(
        client_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Activate client (Directors only)"""

    check_director_permission(current_user)

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.is_active = True
    db.commit()

    return {"message": f"Client '{client.client_name}' activated successfully"}


@router.post("/{client_id}/deactivate")
async def deactivate_client(
        client_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Deactivate client (Directors only)"""

    check_director_permission(current_user)

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.is_active = False
    db.commit()

    return {"message": f"Client '{client.client_name}' deactivated successfully"}


@router.get("/{client_id}/statistics")
async def get_client_detailed_statistics(
        client_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get detailed statistics for a specific client"""

    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get comprehensive statistics
    total_customers = db.query(Customer).filter(Customer.client_id == client_id).count()

    # Arrears statistics
    arrears_stats = {
        "current": db.query(Customer).filter(
            and_(Customer.client_id == client_id, Customer.days_in_arrears == 0)
        ).count(),
        "1_30_days": db.query(Customer).filter(
            and_(Customer.client_id == client_id, Customer.days_in_arrears.between(1, 30))
        ).count(),
        "31_60_days": db.query(Customer).filter(
            and_(Customer.client_id == client_id, Customer.days_in_arrears.between(31, 60))
        ).count(),
        "61_90_days": db.query(Customer).filter(
            and_(Customer.client_id == client_id, Customer.days_in_arrears.between(61, 90))
        ).count(),
        "over_90_days": db.query(Customer).filter(
            and_(Customer.client_id == client_id, Customer.days_in_arrears > 90)
        ).count()
    }

    # Geographic distribution
    zone_distribution = db.query(
        Customer.zone,
        func.count(Customer.id).label('count')
    ).filter(
        and_(Customer.client_id == client_id, Customer.zone.isnot(None))
    ).group_by(Customer.zone).all()

    # Financial statistics
    total_outstanding = db.query(
        func.sum(Customer.granted_amount)
    ).filter(Customer.client_id == client_id).scalar()

    return {
        "client": {
            "id": client.id,
            "client_code": client.client_code,
            "client_name": client.client_name,
            "client_type": client.client_type.value
        },
        "total_customers": total_customers,
        "arrears_breakdown": arrears_stats,
        "zone_distribution": [
            {"zone": zone or "Unknown", "count": count}
            for zone, count in zone_distribution
        ],
        "total_outstanding_amount": float(total_outstanding) if total_outstanding else 0,
        "is_active": client.is_active,
        "created_at": client.created_at
    }
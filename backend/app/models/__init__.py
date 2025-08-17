# app/models/__init__.py - FIXED IMPORTS
from app.db.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.client import Client, ClientType
from app.models.customer import Customer
from app.models.import_batch import ImportBatch, ImportError, ImportStatus, OperationType
from app.models.payment import Payment
from app.models.remark import Remark, RemarkStatus
from app.models.remark_abbreviation import RemarkAbbreviation

# Export all models
__all__ = [
    "Base",
    "User",
    "Role",
    "Client",
    "ClientType",
    "Customer",
    "ImportBatch",
    "ImportError",
    "ImportStatus",
    "OperationType",
    "Payment",
    "Remark",
    "RemarkStatus",
    "RemarkAbbreviation"
]
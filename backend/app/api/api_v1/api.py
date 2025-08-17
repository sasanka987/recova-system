from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, customers, templates, imports, clients, remarks, abbreviations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])  # Add this
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(templates.router, prefix="/templates", tags=["excel-templates"])
api_router.include_router(imports.router, prefix="/imports", tags=["data-imports"])
api_router.include_router(remarks.router, prefix="/remarks", tags=["remarks"])
api_router.include_router(abbreviations.router, prefix="/abbreviations", tags=["remark-abbreviations"])
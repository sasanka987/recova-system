from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, customers, templates, imports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(templates.router, prefix="/templates", tags=["excel-templates"])
api_router.include_router(imports.router, prefix="/imports", tags=["data-imports"])
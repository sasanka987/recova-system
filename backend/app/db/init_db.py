# app/db/init_db.py - FIXED IMPORTS
from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.models import *  # Import all models
from app.models.role import Role
from app.models.user import User
from app.models.remark_abbreviation import RemarkAbbreviation  # FIXED: Import from correct file
from app.core.security import get_password_hash


def init_db() -> None:
    """Initialize database with tables and default data"""

    # Create all tables
    from app.db.database import Base
    Base.metadata.create_all(bind=engine)

    # Create default roles
    db = SessionLocal()
    try:
        # Check if roles exist
        if not db.query(Role).first():
            default_roles = [
                {
                    "name": "Operation Coordinator",
                    "code": "OP_COORD",
                    "description": "Call defaulters and update remarks",
                    "permissions": ["view_assigned_accounts", "create_remarks", "update_remarks",
                                    "view_payment_history"]
                },
                {
                    "name": "Field Recovery Officer",
                    "code": "FIELD_RO",
                    "description": "Visit defaulters and update visit status",
                    "permissions": ["view_assigned_accounts", "create_remarks", "update_visit_status",
                                    "create_payments"]
                },
                {
                    "name": "HR Admin Coordinator",
                    "code": "HR_COORD",
                    "description": "Manage employee activities",
                    "permissions": ["manage_employees", "process_leave_requests", "manage_events", "manage_equipment"]
                },
                {
                    "name": "Operation Team Leader",
                    "code": "OP_LEADER",
                    "description": "Manage operations and teams",
                    "permissions": ["view_team_accounts", "assign_accounts", "approve_remarks", "generate_team_reports"]
                },
                {
                    "name": "IT Coordinator",
                    "code": "IT_COORD",
                    "description": "Network and security management",
                    "permissions": ["manage_users", "system_config", "backup_monitoring", "system_reports"]
                },
                {
                    "name": "IT Manager",
                    "code": "IT_MANAGER",
                    "description": "Oversee IT operations",
                    "permissions": ["all_it_permissions", "system_administration", "security_management"]
                },
                {
                    "name": "Operations Manager",
                    "code": "OP_MANAGER",
                    "description": "Oversee all operations",
                    "permissions": ["view_all_operations", "allocate_resources", "approve_major_updates",
                                    "operational_reports"]
                },
                {
                    "name": "HR Admin Manager",
                    "code": "HR_MANAGER",
                    "description": "Oversee HR activities",
                    "permissions": ["all_hr_permissions", "approve_leave", "hr_analytics", "performance_management"]
                },
                {
                    "name": "General Manager",
                    "code": "GM",
                    "description": "Oversee progress and generate reports",
                    "permissions": ["view_all_data", "generate_all_reports", "approve_decisions", "strategic_planning"]
                },
                {
                    "name": "Director",
                    "code": "DIRECTOR",
                    "description": "Full system oversight",
                    "permissions": ["full_system_access", "approve_users", "manage_roles", "override_permissions"]
                }
            ]

            for role_data in default_roles:
                role = Role(**role_data)
                db.add(role)

            db.commit()

            # Create default director user
            director_role = db.query(Role).filter(Role.code == "DIRECTOR").first()
            if director_role and not db.query(User).filter(User.email == "director@sapl.lk").first():
                director_user = User(
                    email="director@sapl.lk",
                    password_hash=get_password_hash("director123"),
                    first_name="System",
                    last_name="Director",
                    employee_code="DIR001",
                    department="Management",
                    designation="Director",
                    status="ACTIVE",
                    role_id=director_role.id,
                    is_active=True
                )
                db.add(director_user)
                db.commit()

            # Initialize default remark abbreviations
            init_default_remark_abbreviations(db)

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


def init_default_remark_abbreviations(db):
    """Initialize default remark abbreviations"""

    default_abbreviations = [
        {"abbreviation": "LMG", "description": "Left Message",
         "detailed_description": "Left message with family member or colleague"},
        {"abbreviation": "RNR", "description": "Ringing No Response",
         "detailed_description": "Phone ringing but no one answered"},
        {"abbreviation": "PTP", "description": "Promise to Pay",
         "detailed_description": "Customer promised to make payment"},
        {"abbreviation": "SW", "description": "Switched Off", "detailed_description": "Phone is switched off"},
        {"abbreviation": "OOR", "description": "Out of Reach", "detailed_description": "Phone out of network coverage"},
        {"abbreviation": "CBL", "description": "Call Back Later",
         "detailed_description": "Customer requested to call back later"},
        {"abbreviation": "DNC", "description": "Disputed - Not Contacted",
         "detailed_description": "Customer disputes the debt"},
        {"abbreviation": "WN", "description": "Wrong Number", "detailed_description": "Contact number is incorrect"},
        {"abbreviation": "NA", "description": "No Answer", "detailed_description": "No response to calls"},
        {"abbreviation": "NHV", "description": "Not at Home - Visited",
         "detailed_description": "Customer not at home during visit"},
        {"abbreviation": "MET", "description": "Met Customer",
         "detailed_description": "Successfully met with customer"},
        {"abbreviation": "ADD", "description": "Address Not Found",
         "detailed_description": "Could not locate customer address"},
        {"abbreviation": "REF", "description": "Refused to Pay",
         "detailed_description": "Customer refused to make payment"},
        {"abbreviation": "PAR", "description": "Partial Payment",
         "detailed_description": "Customer made partial payment"},
        {"abbreviation": "FUL", "description": "Full Payment", "detailed_description": "Customer made full payment"},
    ]

    # Get director user for created_by
    director_user = db.query(User).filter(User.email == "director@sapl.lk").first()
    if not director_user:
        print("Warning: No director user found for remark abbreviations")
        return

    for abbr_data in default_abbreviations:
        existing = db.query(RemarkAbbreviation).filter(
            RemarkAbbreviation.abbreviation == abbr_data["abbreviation"]
        ).first()

        if not existing:
            abbreviation = RemarkAbbreviation(
                **abbr_data,
                is_system_default=True,
                created_by=director_user.id
            )
            db.add(abbreviation)

    db.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
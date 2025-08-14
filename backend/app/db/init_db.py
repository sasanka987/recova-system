from sqlalchemy import text
from app.db.database import engine, SessionLocal
from app.models import *  # Import all models
from app.models.role import Role
from app.models.user import User
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

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
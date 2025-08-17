# backend/app/api/api_v1/endpoints/imports.py - ULTIMATE COMPLETE VERSION
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import os
import shutil
import pandas as pd
import hashlib

from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.import_batch import ImportBatch, ImportError, OperationType, ImportStatus
from app.models.customer import Customer
from app.models.client import Client
from app.schemas.import_batch import ImportBatchResponse, UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_import_file(
        file: UploadFile = File(...),
        client_id: int = Form(...),  # NEW: Require client selection
        operation_type: str = Form(...),
        import_period: str = Form(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Upload Excel file for import processing with client-based system"""

    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=400,
            detail=f"Client with ID {client_id} not found"
        )

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    # Validate operation type
    valid_operations = ["CREDIT_CARD", "LOAN", "LEASING", "PAYMENT"]
    if operation_type not in valid_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation type. Must be one of: {valid_operations}"
        )

    # Create upload directory
    upload_dir = "uploads/imports"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename with client code
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    safe_client_code = client.client_code.replace(" ", "_").replace("/", "_")
    safe_operation = operation_type.replace("_", "-")
    safe_period = import_period.replace(" ", "_")

    unique_filename = f"{safe_client_code}_{safe_operation}_{safe_period}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    # Save uploaded file
    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Create import batch record
    try:
        # Extract month and year
        try:
            month_name, year_str = import_period.split()
            month_map = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month = month_map.get(month_name, datetime.now().month)
            year = int(year_str)
        except:
            month, year = datetime.now().month, datetime.now().year

        # Generate file hash
        file_hash = hashlib.md5(content).hexdigest()

        batch = ImportBatch(
            batch_name=f"{client.client_code} {operation_type} {import_period}",
            client_id=client_id,  # Store client ID
            bank_name=client.client_name,  # Keep for backward compatibility
            bank_code=client.client_code,
            operation_type=OperationType(operation_type),
            import_period=import_period,
            import_month=month,
            import_year=year,
            file_name=file.filename,
            file_size=len(content),
            file_path=file_path,
            file_checksum=file_hash,
            status=ImportStatus.UPLOADED,
            imported_by=current_user.id
        )

        db.add(batch)
        db.commit()
        db.refresh(batch)

        return UploadResponse(
            message="File uploaded successfully",
            batch_id=batch.id,
            file_name=file.filename,
            file_size=len(content),
            next_step=f"Use /validate/{batch.id} to validate the data, then /process/{batch.id} to import"
        )

    except Exception as e:
        # Clean up file if batch creation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create import batch: {str(e)}"
        )


@router.post("/validate/{batch_id}")
async def validate_import_batch(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Validate uploaded import file with client code validation"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    if batch.status != ImportStatus.UPLOADED:
        raise HTTPException(status_code=400, detail="Batch must be in UPLOADED status to validate")

    # Update status to validating
    batch.status = ImportStatus.VALIDATING
    db.commit()

    try:
        # Read and validate Excel file
        if not os.path.exists(batch.file_path):
            raise FileNotFoundError("Import file not found")

        # Read Excel file
        df = pd.read_excel(batch.file_path, engine='openpyxl')

        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # Basic validation
        errors = []
        total_records = len(df)
        valid_records = 0

        # Required fields based on operation type
        required_fields = {
            "CREDIT_CARD": ["client_code", "client_name", "nic", "contract_number"],
            "LOAN": ["client_code", "client_name", "nic", "contract_number"],
            "LEASING": ["client_code", "client_name", "nic", "contract_number"],
            "PAYMENT": ["client_code", "payment_date", "contract_number", "payment_amount"]
        }

        required = required_fields.get(batch.operation_type.value,
                                       ["client_code", "client_name", "nic", "contract_number"])

        # Check required columns exist
        missing_columns = [col for col in required if col not in df.columns]
        if missing_columns:
            errors.append({
                "row_number": 0,
                "column_name": None,
                "error_type": "MISSING_COLUMNS",
                "error_message": f"Missing required columns: {missing_columns}",
                "is_critical": True
            })

        # Get the client for this batch to validate client codes
        batch_client = db.query(Client).filter(Client.id == batch.client_id).first()

        # Validate each row
        for index, row in df.iterrows():
            row_errors = []

            # Check required fields
            for field in required:
                if field in df.columns and pd.isna(row[field]):
                    row_errors.append({
                        "row_number": index + 2,  # +2 for Excel row (header + 0-index)
                        "column_name": field,
                        "error_type": "REQUIRED_FIELD_MISSING",
                        "error_message": f"Required field '{field}' is missing",
                        "original_value": None,
                        "is_critical": True
                    })

            # Validate client code matches the selected client
            if 'client_code' in df.columns and not pd.isna(row['client_code']):
                client_code = str(row['client_code']).strip()
                if client_code != batch_client.client_code:
                    row_errors.append({
                        "row_number": index + 2,
                        "column_name": "client_code",
                        "error_type": "INVALID_CLIENT_CODE",
                        "error_message": f"Client code '{client_code}' doesn't match selected client '{batch_client.client_code}'",
                        "original_value": client_code,
                        "is_critical": True
                    })

            # Validate NIC format if present
            if 'nic' in df.columns and not pd.isna(row['nic']):
                nic = str(row['nic']).strip()
                if not (len(nic) == 10 and nic[:-1].isdigit() and nic[-1].upper() in 'VX') and not (
                        len(nic) == 12 and nic.isdigit()):
                    row_errors.append({
                        "row_number": index + 2,
                        "column_name": "nic",
                        "error_type": "INVALID_NIC_FORMAT",
                        "error_message": "Invalid NIC format. Use 123456789V or 123456789012",
                        "original_value": nic,
                        "is_critical": False
                    })

            # Check for duplicate contract numbers within this file
            if 'contract_number' in df.columns and not pd.isna(row['contract_number']):
                contract_number = str(row['contract_number']).strip()
                duplicate_count = df[df['contract_number'] == contract_number].shape[0]
                if duplicate_count > 1:
                    row_errors.append({
                        "row_number": index + 2,
                        "column_name": "contract_number",
                        "error_type": "DUPLICATE_CONTRACT_IN_FILE",
                        "error_message": f"Contract number '{contract_number}' appears {duplicate_count} times in this file",
                        "original_value": contract_number,
                        "is_critical": True
                    })

            # If no critical errors, count as valid
            if not any(error["is_critical"] for error in row_errors):
                valid_records += 1

            errors.extend(row_errors)

        # Save errors to database
        for error_data in errors:
            error = ImportError(
                batch_id=batch_id,
                row_number=error_data["row_number"],
                column_name=error_data.get("column_name"),
                error_type=error_data["error_type"],
                error_message=error_data["error_message"],
                original_value=error_data.get("original_value"),
                is_critical=error_data["is_critical"]
            )
            db.add(error)

        # Update batch statistics
        batch.total_records = total_records
        batch.valid_records = valid_records
        batch.invalid_records = len([e for e in errors if e["is_critical"]])

        # Update status
        critical_errors = [e for e in errors if e["is_critical"]]
        if critical_errors:
            batch.status = ImportStatus.FAILED
        else:
            batch.status = ImportStatus.VALIDATED

        db.commit()

        return {
            "batch_id": batch_id,
            "status": batch.status.value,
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": len(critical_errors),
            "errors": len(errors),
            "message": "Validation completed" if not critical_errors else "Validation failed - critical errors found",
            "next_step": "Use /process/{batch_id} to import data" if not critical_errors else "Fix errors and re-upload file"
        }

    except Exception as e:
        batch.status = ImportStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/process/{batch_id}")
async def process_import_batch(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Process validated import batch with client-based customer management"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    if batch.status != ImportStatus.VALIDATED:
        raise HTTPException(status_code=400, detail="Batch must be validated before processing")

    # Update status to importing
    batch.status = ImportStatus.IMPORTING
    batch.import_started_at = datetime.now()
    db.commit()

    try:
        # Read Excel file
        df = pd.read_excel(batch.file_path, engine='openpyxl')
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        imported_count = 0
        updated_count = 0
        created_count = 0

        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                row_data = {}
                for col, value in row.items():
                    if pd.notna(value):
                        # Handle numeric columns
                        if col in ['granted_amount', 'credit_limit', 'payment_amount',
                                   'monthly_rental_payment_with_vat', 'last_payment_amount',
                                   'capital_balance', 'interest_over_due_balance',
                                   'total_outstanding_amount', 'minimum_due_amount']:
                            row_data[col] = float(value)
                        # Handle integer columns
                        elif col in ['days_in_arrears', 'rentals_in_arrears', 'age_in_arrears']:
                            row_data[col] = int(value)
                        # Handle date columns
                        elif col in ['facility_granted_date', 'facility_end_date',
                                     'last_payment_date', 'due_date']:
                            try:
                                row_data[col] = pd.to_datetime(value).date()
                            except:
                                row_data[col] = None
                        else:
                            row_data[col] = str(value).strip()
                    else:
                        row_data[col] = None

                # Get contract number
                contract_number = row_data.get('contract_number')
                if not contract_number:
                    print(f"Row {index}: No contract number found, skipping")
                    continue

                # Check if customer exists for this client and contract
                existing_customer = db.query(Customer).filter(
                    Customer.client_id == batch.client_id,
                    Customer.contract_number == contract_number
                ).first()

                if existing_customer:
                    # UPDATE existing customer
                    print(f"Updating customer with contract {contract_number} for client {batch.client_id}")

                    # Update all fields from the import
                    for key, value in row_data.items():
                        if hasattr(existing_customer, key) and value is not None and key != 'client_code':
                            setattr(existing_customer, key, value)

                    # Update import batch ID and timestamp
                    existing_customer.import_batch_id = batch_id
                    existing_customer.updated_at = datetime.now()

                    updated_count += 1
                else:
                    # CREATE new customer
                    print(f"Creating new customer with contract {contract_number} for client {batch.client_id}")

                    # Filter only valid Customer model fields
                    customer_fields = [col.name for col in Customer.__table__.columns]
                    customer_data = {k: v for k, v in row_data.items() if k in customer_fields}
                    customer_data['client_id'] = batch.client_id  # Set client ID
                    customer_data['import_batch_id'] = batch_id
                    customer_data['created_by'] = current_user.id

                    customer = Customer(**customer_data)
                    db.add(customer)

                    created_count += 1

                imported_count += 1

                # Commit every 100 records for performance
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"Processed {imported_count} records...")

            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue

        # Final commit
        db.commit()

        # Update batch completion
        batch.status = ImportStatus.COMPLETED
        batch.imported_records = imported_count
        batch.import_completed_at = datetime.now()
        db.commit()

        processing_time = (batch.import_completed_at - batch.import_started_at).total_seconds()

        return {
            "batch_id": batch_id,
            "status": "COMPLETED",
            "total_records": batch.total_records,
            "imported_records": imported_count,
            "created_records": created_count,
            "updated_records": updated_count,
            "processing_time_seconds": processing_time,
            "message": f"Successfully imported {imported_count} records ({created_count} new, {updated_count} updated)",
            "next_step": "Data is now available in the system. Use /customers/ to view imported customers"
        }

    except Exception as e:
        batch.status = ImportStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Import processing failed: {str(e)}")


@router.get("/batches", response_model=List[ImportBatchResponse])
async def get_import_batches(
        skip: int = 0,
        limit: int = 50,
        client_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get list of import batches with optional client filtering"""

    query = db.query(ImportBatch).order_by(ImportBatch.created_at.desc())

    if client_id:
        query = query.filter(ImportBatch.client_id == client_id)

    batches = query.offset(skip).limit(limit).all()
    return batches


@router.get("/batch/{batch_id}", response_model=ImportBatchResponse)
async def get_import_batch(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get specific import batch details"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    return batch


@router.get("/batch/{batch_id}/errors")
async def get_import_errors(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get validation errors for an import batch"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    errors = db.query(ImportError).filter(ImportError.batch_id == batch_id).all()

    return {
        "batch_id": batch_id,
        "batch_name": batch.batch_name,
        "total_errors": len(errors),
        "critical_errors": len([e for e in errors if e.is_critical]),
        "errors": [
            {
                "id": error.id,
                "row_number": error.row_number,
                "column_name": error.column_name,
                "error_type": error.error_type,
                "error_message": error.error_message,
                "original_value": error.original_value,
                "suggested_value": error.suggested_value,
                "is_critical": error.is_critical
            }
            for error in errors
        ]
    }


@router.get("/status/{batch_id}")
async def get_import_status(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get real-time import status"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    # Calculate progress percentage
    progress_percentage = 0
    if batch.total_records > 0:
        if batch.status == ImportStatus.COMPLETED:
            progress_percentage = 100
        elif batch.status == ImportStatus.IMPORTING:
            progress_percentage = (batch.imported_records / batch.total_records) * 100
        elif batch.status == ImportStatus.VALIDATED:
            progress_percentage = 75
        elif batch.status == ImportStatus.VALIDATING:
            progress_percentage = 25

    return {
        "batch_id": batch_id,
        "batch_name": batch.batch_name,
        "status": batch.status.value,
        "progress_percentage": progress_percentage,
        "total_records": batch.total_records,
        "imported_records": batch.imported_records,
        "valid_records": batch.valid_records,
        "invalid_records": batch.invalid_records,
        "started_at": batch.import_started_at,
        "completed_at": batch.import_completed_at,
        "bank_name": batch.bank_name,
        "operation_type": batch.operation_type.value,
        "import_period": batch.import_period,
        "client_id": batch.client_id
    }


@router.get("/check-customers/{batch_id}")
async def check_imported_customers(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Check which customers were imported from a specific batch"""

    # Get batch info
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    # Get customers from this batch
    customers = db.query(Customer).filter(
        Customer.import_batch_id == batch_id
    ).all()

    return {
        "batch_name": batch.batch_name,
        "batch_status": batch.status.value,
        "imported_records": batch.imported_records,
        "customers_found": len(customers),
        "client_id": batch.client_id,
        "customer_list": [
            {
                "id": c.id,
                "client_name": c.client_name,
                "nic": c.nic,
                "contract_number": c.contract_number,
                "client_id": c.client_id,
                "created_at": c.created_at
            }
            for c in customers
        ]
    }


@router.post("/force-reprocess/{batch_id}")
async def force_reprocess_batch(
        batch_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Force reprocess a batch regardless of status"""

    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    # Reset status to VALIDATED to allow reprocessing
    batch.status = ImportStatus.VALIDATED
    batch.imported_records = 0
    db.commit()

    # Now process it
    return await process_import_batch(batch_id, db, current_user)


@router.get("/test-import-status")
async def test_import_status(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Simple test to check import status"""

    # Get last 5 batches
    batches = db.query(ImportBatch).order_by(ImportBatch.id.desc()).limit(5).all()

    result = {
        "total_customers": db.query(Customer).count(),
        "recent_batches": []
    }

    for batch in batches:
        # Count customers from this batch
        customers_count = db.query(Customer).filter(
            Customer.import_batch_id == batch.id
        ).count()

        # Get sample customers
        sample_customers = db.query(Customer).filter(
            Customer.import_batch_id == batch.id
        ).limit(3).all()

        batch_info = {
            "id": batch.id,
            "name": batch.batch_name,
            "status": batch.status.value,
            "total_records": batch.total_records,
            "imported_records": batch.imported_records,
            "customers_in_db": customers_count,
            "client_id": batch.client_id,
            "sample_customers": [
                {
                    "id": c.id,
                    "name": c.client_name,
                    "contract": c.contract_number
                }
                for c in sample_customers
            ]
        }

        result["recent_batches"].append(batch_info)

    return result
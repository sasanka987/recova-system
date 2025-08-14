# File: app/services/__init__.py
# Create this file (empty is fine)

# File: app/services/template_service.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, List
import os
from datetime import date


class TemplateService:
    """Service for generating Excel templates based on our database models"""

    def __init__(self):
        self.templates = {
            "CREDIT_CARD": {
                "headers": [
                    # Bank/Client Information (NEW)
                    "bank_name", "operation_name",

                    # Customer Base Fields
                    "client_name", "nic", "home_address",
                    "customer_contact_number_1", "customer_contact_number_2", "customer_contact_number_3",
                    "contract_number", "granted_amount", "facility_granted_date", "facility_end_date",

                    # Employment
                    "designation", "work_place_name", "work_place_address",
                    "work_place_contact_number_1", "work_place_contact_number_2", "work_place_contact_number_3",

                    # Financial
                    "monthly_rental_payment_with_vat", "last_payment_date", "last_payment_amount", "due_date",

                    # Location
                    "zone", "region", "branch_name", "district_name", "postal_town",

                    # Status
                    "days_in_arrears", "details", "payment_assumption",

                    # Guarantor Information
                    "guarantor_1_name", "guarantor_1_address", "guarantor_1_nic",
                    "guarantor_1_contact_number_1", "guarantor_1_contact_number_2",
                    "guarantor_2_name", "guarantor_2_address", "guarantor_2_nic",
                    "guarantor_2_contact_number_1", "guarantor_2_contact_number_2",

                    # Credit Card Specific Fields
                    "card_product_type", "card_number", "supplementary_card_number", "card_status",
                    "account_number", "account_status", "segment", "bill_cycle_code",
                    "credit_limit", "capital_balance", "interest_over_due_balance",
                    "total_outstanding_amount", "minimum_due_amount",
                    "card_issued_date", "facility_closed_date", "statement_date", "payment_due_date",
                    "relative_name", "relative_address", "relative_relationship",
                    "relative_contact_number_1", "relative_contact_number_2", "relative_contact_number_3"
                ],
                "sample_data": [
                    [
                        # Bank/Client Information (NEW)
                        "Commercial Bank", "Credit Cards",

                        # Customer Base
                        "John Doe", "123456789V", "123 Main Street, Colombo 03",
                        "0771234567", "0112345678", "0779876543",
                        "CC001234567", 500000.00, "2023-01-15", "2028-01-15",

                        # Employment
                        "Manager", "ABC Company", "456 Business Ave, Colombo",
                        "0112334455", "0112334456", "",

                        # Financial
                        25000.00, "2025-07-15", 20000.00, "2025-08-15",

                        # Location
                        "Colombo", "Western", "Colombo Central", "Colombo", "Colombo 03",

                        # Status
                        15, "Regular customer", "Monthly payments",

                        # Guarantors
                        "Jane Doe", "789 Oak Road, Kandy", "987654321V", "0712345678", "0112233445",
                        "Bob Smith", "321 Pine St, Galle", "456789123V", "0723456789", "0912234567",

                        # Credit Card Specific
                        "VISA GOLD", "4532********1234", "4532********5678", "ACTIVE",
                        "ACC123456789", "ACTIVE", "PREMIUM", "15",
                        500000.00, 250000.00, 15000.00, 265000.00, 25000.00,
                        "2023-01-15", "", "2025-08-01", "2025-08-15",
                        "Mary Doe", "Same as home", "Sister", "0771111111", "0112222222", ""
                    ],
                    [
                        # Bank/Client Information - Second row example
                        "Commercial Bank", "Credit Cards",

                        # Customer Base
                        "Alice Wilson", "234567890V", "567 Queen Street, Kandy",
                        "0712345678", "0812345679", "",
                        "CC002345678", 300000.00, "2023-02-10", "2028-02-10",

                        # Employment
                        "Engineer", "Tech Solutions", "789 Tech Park, Kandy",
                        "0812233445", "", "",

                        # Financial
                        15000.00, "2025-07-10", 12000.00, "2025-08-10",

                        # Location
                        "Kandy", "Central", "Kandy Main", "Kandy", "Kandy 20000",

                        # Status
                        25, "Good customer", "Regular payments",

                        # Guarantors
                        "Bob Wilson", "Same address", "345678901V", "0713456789", "",
                        "Carol Smith", "123 Hill Road, Kandy", "567890123V", "0714567890", "",

                        # Credit Card Specific
                        "MASTERCARD PLATINUM", "5432********9876", "", "ACTIVE",
                        "ACC234567890", "ACTIVE", "GOLD", "20",
                        300000.00, 150000.00, 8000.00, 158000.00, 15000.00,
                        "2023-02-10", "", "2025-08-05", "2025-08-20",
                        "", "", "", "", "", ""
                    ]
                ],
                "description": "Credit Card defaulter accounts template with bank information and all customer/card-specific fields"
            },

            "LOAN": {
                "headers": [
                    # Bank/Client Information (NEW)
                    "bank_name", "operation_name",

                    # Customer Base Fields
                    "client_name", "nic", "home_address",
                    "customer_contact_number_1", "customer_contact_number_2", "customer_contact_number_3",
                    "contract_number", "granted_amount", "facility_granted_date", "facility_end_date",

                    # Employment
                    "designation", "work_place_name", "work_place_address",
                    "work_place_contact_number_1", "work_place_contact_number_2", "work_place_contact_number_3",

                    # Financial
                    "monthly_rental_payment_with_vat", "last_payment_date", "last_payment_amount", "due_date",

                    # Location
                    "zone", "region", "branch_name", "district_name", "postal_town",

                    # Status
                    "days_in_arrears", "details", "payment_assumption",

                    # Guarantor Information
                    "guarantor_1_name", "guarantor_1_address", "guarantor_1_nic",
                    "guarantor_1_contact_number_1", "guarantor_1_contact_number_2",
                    "guarantor_2_name", "guarantor_2_address", "guarantor_2_nic",
                    "guarantor_2_contact_number_1", "guarantor_2_contact_number_2",

                    # Loan Specific Fields
                    "segment", "loan_type", "loan_status", "loan_description",
                    "clear_balance", "capital_balance", "interest_over_due_balance",
                    "capital_with_interest_amount", "installment_amount",
                    "arrears_settlement_offer", "full_settlement_offer",
                    "security_description", "security_value", "operative_account_number"
                ],
                "sample_data": [
                    [
                        # Bank/Client Information (NEW)
                        "Sampath Bank", "Loans",

                        # Customer Base
                        "Alice Smith", "234567890V", "789 Oak Road, Kandy",
                        "0712345678", "0812345679", "",
                        "LN987654321", 1000000.00, "2022-05-10", "2027-05-10",

                        # Employment
                        "Engineer", "XYZ Corporation", "123 Tech Park, Kandy",
                        "0812233445", "0812233446", "",

                        # Financial
                        15000.00, "2025-07-10", 12000.00, "2025-08-10",

                        # Location
                        "Kandy", "Central", "Kandy Main", "Kandy", "Kandy 20000",

                        # Status
                        30, "Property loan", "Monthly installments",

                        # Guarantors
                        "Bob Smith", "456 Hill Road, Kandy", "345678901V", "0713456789", "0813456789",
                        "Carol Johnson", "789 Valley Road, Kandy", "567890123V", "0714567890", "0814567890",

                        # Loan Specific
                        "RETAIL", "PERSONAL", "ACTIVE", "Personal loan for house renovation",
                        50000.00, 750000.00, 50000.00, 800000.00, 15000.00,
                        600000.00, 750000.00, "Property at Kandy valued at 1.5M", 1500000.00, "OP123456789"
                    ],
                    [
                        # Bank/Client Information - Second row
                        "Sampath Bank", "Loans",

                        # Customer Base
                        "David Brown", "345678901V", "456 Castle Road, Galle",
                        "0913456789", "0713456780", "",
                        "LN876543210", 1500000.00, "2021-08-15", "2026-08-15",

                        # Employment
                        "Doctor", "Private Practice", "789 Medical Center, Galle",
                        "0913334455", "", "",

                        # Financial
                        25000.00, "2025-07-05", 22000.00, "2025-08-05",

                        # Location
                        "Galle", "Southern", "Galle Main", "Galle", "Galle 80000",

                        # Status
                        10, "Medical equipment loan", "Regular payments",

                        # Guarantors
                        "Sarah Brown", "Same address", "456789012V", "0914567890", "",
                        "Michael Wilson", "321 Beach Road, Galle", "678901234V", "0915678901", "",

                        # Loan Specific
                        "PROFESSIONAL", "COMMERCIAL", "ACTIVE", "Medical equipment financing",
                        100000.00, 1200000.00, 75000.00, 1275000.00, 25000.00,
                        1000000.00, 1200000.00, "Medical equipment valued at 2M", 2000000.00, "OP987654321"
                    ]
                ],
                "description": "Loan defaulter accounts template with bank information and all customer/loan-specific fields"
            },

            "LEASING": {
                "headers": [
                    # Bank/Client Information (NEW)
                    "bank_name", "operation_name",

                    # Customer Base Fields
                    "client_name", "nic", "home_address",
                    "customer_contact_number_1", "customer_contact_number_2", "customer_contact_number_3",
                    "contract_number", "granted_amount", "facility_granted_date", "facility_end_date",

                    # Employment
                    "designation", "work_place_name", "work_place_address",
                    "work_place_contact_number_1", "work_place_contact_number_2", "work_place_contact_number_3",

                    # Financial
                    "monthly_rental_payment_with_vat", "last_payment_date", "last_payment_amount", "due_date",

                    # Location
                    "zone", "region", "branch_name", "district_name", "postal_town",

                    # Status
                    "days_in_arrears", "details", "payment_assumption",

                    # Guarantor Information
                    "guarantor_1_name", "guarantor_1_address", "guarantor_1_nic",
                    "guarantor_1_contact_number_1", "guarantor_1_contact_number_2",
                    "guarantor_2_name", "guarantor_2_address", "guarantor_2_nic",
                    "guarantor_2_contact_number_1", "guarantor_2_contact_number_2",

                    # Leasing Specific Fields
                    "lease_granted_period", "rental_category",
                    "rental_and_vat_arrears", "default_arrears", "other_charges",
                    "insurance_premium_arrears", "total_arrears", "current_arrears",
                    "rentals_in_arrears", "age_in_arrears", "matured_rentals", "paid_rentals", "future_rentals",
                    "vehicle_number", "equipment", "model", "leased_vehicle_status", "asset_description",
                    "other_party_name", "other_party_contact_number", "other_party_address"
                ],
                "sample_data": [
                    [
                        # Bank/Client Information (NEW)
                        "Central Finance", "Leasing",

                        # Customer Base
                        "Mike Johnson", "345678901V", "321 Pine Street, Galle",
                        "0723456789", "0913456789", "",
                        "LS456789012", 750000.00, "2023-03-20", "2028-03-20",

                        # Employment
                        "Sales Manager", "DEF Enterprises", "987 Business Center, Galle",
                        "0913334455", "0913334456", "",

                        # Financial
                        18000.00, "2025-07-20", 15000.00, "2025-08-20",

                        # Location
                        "Galle", "Southern", "Galle Fort", "Galle", "Galle 80000",

                        # Status
                        5, "Vehicle lease", "Monthly rentals",

                        # Guarantors
                        "Sarah Johnson", "654 Beach Road, Galle", "678901234V", "0724567890", "0914567890",
                        "David Wilson", "432 Coastal Ave, Galle", "789012345V", "0725678901", "0915678901",

                        # Leasing Specific
                        60, "Vehicle Leasing",
                        50000.00, 25000.00, 5000.00, 10000.00, 90000.00, 90000.00,
                        3, 5, 24, 21, 36,
                        "CAR-1234", "Toyota Corolla", "Corolla Axio 2023", "WITH CUSTOMER",
                        "Toyota Corolla Axio 2023 - Red Color",
                        "Lisa Johnson", "0726789012", "Same as customer address"
                    ],
                    [
                        # Bank/Client Information - Second row
                        "Central Finance", "Leasing",

                        # Customer Base
                        "Emma Davis", "456789012V", "789 Garden Lane, Kandy",
                        "0814567890", "0714567891", "",
                        "LS567890123", 900000.00, "2023-04-15", "2028-04-15",

                        # Employment
                        "Teacher", "Government School", "456 Education Road, Kandy",
                        "0814445566", "", "",

                        # Financial
                        20000.00, "2025-07-15", 18000.00, "2025-08-15",

                        # Location
                        "Kandy", "Central", "Kandy Central", "Kandy", "Kandy 20000",

                        # Status
                        12, "Motorbike lease", "Regular rentals",

                        # Guarantors
                        "John Davis", "Same address", "567890123V", "0815678901", "",
                        "Maria Silva", "123 School Road, Kandy", "890123456V", "0816789012", "",

                        # Leasing Specific
                        48, "Two Wheeler Leasing",
                        30000.00, 15000.00, 2000.00, 5000.00, 52000.00, 52000.00,
                        2, 12, 18, 16, 30,
                        "BIKE-5678", "Honda CBR", "CBR 150R 2023", "WITH CUSTOMER", "Honda CBR 150R 2023 - Blue Color",
                        "", "", ""
                    ]
                ],
                "description": "Leasing/Vehicle Finance defaulter accounts template with bank information and all customer/leasing-specific fields"
            }
        }

    def generate_template(self, operation_type: str, include_sample: bool = True) -> str:
        """Generate Excel template for given operation type"""

        if operation_type not in self.templates:
            raise ValueError(f"Template not available for operation type: {operation_type}")

        template_data = self.templates[operation_type]

        # Create workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{operation_type}_Import_Template"

        # Define styles
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        data_font = Font(name="Arial", size=10)
        data_alignment = Alignment(horizontal="left", vertical="center")

        border = Border(
            left=Side(border_style="thin"),
            right=Side(border_style="thin"),
            top=Side(border_style="thin"),
            bottom=Side(border_style="thin")
        )

        # Add title and description
        ws.merge_cells('A1:E1')
        title_cell = ws['A1']
        title_cell.value = f"RECOVA - {operation_type.replace('_', ' ').title()} Import Template"
        title_cell.font = Font(name="Arial", size=14, bold=True, color="366092")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.merge_cells('A2:E2')
        desc_cell = ws['A2']
        desc_cell.value = template_data["description"]
        desc_cell.font = Font(name="Arial", size=10, italic=True)
        desc_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Add instructions
        ws.merge_cells('A3:E3')
        inst_cell = ws['A3']
        inst_cell.value = "Instructions: Fill in the data starting from row 6. Do not modify the headers in row 5."
        inst_cell.font = Font(name="Arial", size=10, color="FF0000")
        inst_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Add headers starting from row 5
        header_row = 5
        for col, header in enumerate(template_data["headers"], 1):
            cell = ws.cell(row=header_row, column=col)
            cell.value = header.replace("_", " ").title()
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        # Add sample data if requested
        if include_sample and template_data.get("sample_data"):
            for row_idx, sample_row in enumerate(template_data["sample_data"], header_row + 1):
                for col_idx, value in enumerate(sample_row, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    cell.font = data_font
                    cell.alignment = data_alignment
                    cell.border = border

        # Auto-adjust column widths - Fixed version
        for col_num in range(1, len(template_data["headers"]) + 1):
            column_letter = get_column_letter(col_num)
            max_length = 0

            # Check header length
            header_cell = ws.cell(row=header_row, column=col_num)
            if header_cell.value:
                max_length = max(max_length, len(str(header_cell.value)))

            # Check data length if sample data exists
            if include_sample and template_data.get("sample_data"):
                for row_idx in range(header_row + 1, header_row + len(template_data["sample_data"]) + 1):
                    data_cell = ws.cell(row=row_idx, column=col_num)
                    if data_cell.value:
                        max_length = max(max_length, len(str(data_cell.value)))

            # Set minimum width of 12, maximum of 50
            adjusted_width = min(max(max_length + 2, 12), 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Add data validation for some fields
        self._add_data_validation(ws, operation_type, header_row)

        # Save template
        template_dir = "templates"
        os.makedirs(template_dir, exist_ok=True)
        filename = f"RECOVA_{operation_type}_Import_Template.xlsx"
        filepath = os.path.join(template_dir, filename)
        wb.save(filepath)

        return filepath

    def _add_data_validation(self, ws, operation_type: str, header_row: int):
        """Add data validation rules to specific columns"""
        from openpyxl.worksheet.datavalidation import DataValidation

        # Find column indices for validation
        headers = [cell.value for cell in ws[header_row]]

        # NIC validation (basic format check)
        if "Nic" in headers:
            nic_col = headers.index("Nic") + 1
            nic_validation = DataValidation(
                type="textLength",
                operator="between",
                formula1=10,
                formula2=12,
                error="NIC must be 10-12 characters (e.g., 123456789V or 123456789012)",
                errorTitle="Invalid NIC Format"
            )
            ws.add_data_validation(nic_validation)
            nic_validation.add(f"{get_column_letter(nic_col)}6:{get_column_letter(nic_col)}1000")

        # Loan type validation for loans
        if operation_type == "LOAN" and "Loan Type" in headers:
            loan_type_col = headers.index("Loan Type") + 1
            loan_type_validation = DataValidation(
                type="list",
                formula1='"MORTGAGED,PERSONAL,EDUCATIONAL,VEHICLE,OVERDUE,COMMERCIAL"',
                error="Please select a valid loan type",
                errorTitle="Invalid Loan Type"
            )
            ws.add_data_validation(loan_type_validation)
            loan_type_validation.add(f"{get_column_letter(loan_type_col)}6:{get_column_letter(loan_type_col)}1000")

        # Status validation for credit cards
        if operation_type == "CREDIT_CARD" and "Card Status" in headers:
            status_col = headers.index("Card Status") + 1
            status_validation = DataValidation(
                type="list",
                formula1='"ACTIVE,INACTIVE,CLOSED,BLOCKED"',
                error="Please select a valid card status",
                errorTitle="Invalid Card Status"
            )
            ws.add_data_validation(status_validation)
            status_validation.add(f"{get_column_letter(status_col)}6:{get_column_letter(status_col)}1000")

    def get_template_info(self) -> Dict:
        """Get information about all available templates"""
        return {
            operation_type: {
                "description": template_data["description"],
                "field_count": len(template_data["headers"]),
                "sample_provided": bool(template_data.get("sample_data"))
            }
            for operation_type, template_data in self.templates.items()
        }
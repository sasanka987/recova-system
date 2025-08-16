# Create this as test_import.py in your backend folder
# Run it with: python test_import.py

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.models.customer import Customer
from app.models.import_batch import ImportBatch
import pandas as pd
from sqlalchemy import text


def test_import():
    db = SessionLocal()

    print("=" * 50)
    print("TESTING IMPORT SYSTEM")
    print("=" * 50)

    # 1. Check if Customer table exists and has correct columns
    print("\n1. Checking Customer table structure:")
    result = db.execute(text("DESCRIBE customers"))
    columns = result.fetchall()
    print(f"Found {len(columns)} columns in customers table")

    # Check for important columns
    important_cols = ['id', 'contract_number', 'nic', 'client_name', 'import_batch_id']
    for col in important_cols:
        found = any(c[0] == col for c in columns)
        print(f"  - {col}: {'✓' if found else '✗ MISSING'}")

    # 2. Check total customers
    print(f"\n2. Total customers in database: {db.query(Customer).count()}")

    # 3. Check recent import batches
    print("\n3. Recent import batches:")
    batches = db.query(ImportBatch).order_by(ImportBatch.id.desc()).limit(5).all()
    for batch in batches:
        print(f"  - Batch {batch.id}: {batch.batch_name}")
        print(f"    Status: {batch.status.value}")
        print(f"    Imported: {batch.imported_records} records")

        # Check customers from this batch
        customers_from_batch = db.query(Customer).filter(
            Customer.import_batch_id == batch.id
        ).count()
        print(f"    Customers found: {customers_from_batch}")

    # 4. Check the latest batch file
    if batches:
        latest_batch = batches[0]
        print(f"\n4. Checking latest batch file: {latest_batch.file_name}")

        if os.path.exists(latest_batch.file_path):
            print(f"   File exists at: {latest_batch.file_path}")

            # Try to read it
            try:
                df = pd.read_excel(latest_batch.file_path, engine='openpyxl')
                print(f"   File has {len(df)} rows")
                print(f"   Columns: {list(df.columns)[:5]}...")  # Show first 5 columns

                # Clean columns and check data
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

                if 'contract_number' in df.columns:
                    print(f"   Contract numbers found: {df['contract_number'].head().tolist()}")
                else:
                    print("   WARNING: No 'contract_number' column found!")

            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"   File NOT FOUND at: {latest_batch.file_path}")

    # 5. Try a test insert
    print("\n5. Testing direct insert:")
    try:
        test_customer = Customer(
            client_name="TEST CUSTOMER",
            nic="123456789V",
            contract_number="TEST-CONTRACT-001",
            import_batch_id=1
        )
        db.add(test_customer)
        db.commit()
        print("   ✓ Test customer inserted successfully")

        # Now delete it
        db.delete(test_customer)
        db.commit()
        print("   ✓ Test customer deleted")

    except Exception as e:
        print(f"   ✗ Error inserting test customer: {e}")
        db.rollback()

    db.close()
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    test_import()
import os
import datetime

MIGRATIONS_DIR = "/db/migrations"

def create_migration_file():
    # Ensure the migrations directory exists
    if not os.path.exists(MIGRATIONS_DIR):
        os.makedirs(MIGRATIONS_DIR)

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Prompt the user for the migration name
    migration_name = input("Enter the name of the migration (e.g., create_users_table): ")

    # Create the full filename
    filename = f"{timestamp}_{migration_name}.sql"
    full_path = os.path.join(MIGRATIONS_DIR, filename)

    # Create an empty SQL file
    with open(full_path, 'w') as f:
        f.write("-- Migration: " + migration_name + "\n\n")

    print(f"Created new migration file: {full_path}")

if __name__ == "__main__":
    create_migration_file()

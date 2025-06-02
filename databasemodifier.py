import os

# Name of your database file
db_filename = "face_db.sqlite"

# Check if the file exists
if os.path.exists(db_filename):
    os.remove(db_filename)
    print(f"✅ Database '{db_filename}' deleted successfully.")
else:
    print(f"⚠️ Database file '{db_filename}' does not exist.")


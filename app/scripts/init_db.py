# In this script, we initialize the database by creating all necessary tables for the job scheduler application.


from app.db.session import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully")

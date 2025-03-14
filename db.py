from sqlmodel import Field, SQLModel, create_engine, Session, select
from models import metadata, Instructor, Group, Activity, Venue
import pandas as pd 
from sqlalchemy import event


sqlite_file_name = "/tmp/db.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})


# Ensure foreign key enforcement
@event.listens_for(engine, "connect")
def enforce_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


def create_db():
    SQLModel.metadata.create_all(engine)
    # Check and insert default records if tables are empty
    with Session(engine) as session:
        # Check if 'Instructor' table is empty
        if not session.execute(select(Instructor)).scalars().first():
            # Insert default instructor
            default_instructor = Instructor(name="Default Instructor")
            session.add(default_instructor)
            session.commit()

        # Check if 'Venue' table is empty
        if not session.execute(select(Venue)).scalars().first():
            # Insert default venue
            default_venue = Venue(name="Default Venue", floor_type="real")
            session.add(default_venue)
            session.commit()

        # Check if 'Group' table is empty
        if not session.execute(select(Group)).scalars().first():
            # Insert default group (instructor_id set to 1 as Default Instructor)
            default_group = Group(name="Default Group", gender="M", age_group=18, instructor_id=1)
            session.add(default_group)
            session.commit()

# 🚀 Get Database Session
def get_session():
    return Session(engine)

# 🚀 Helper Function: Get DataFrame from SQLModel
def fetch_data(model):
    with get_session() as session:
        results = session.exec(select(model)).all()
        return pd.DataFrame([row.dict() for row in results])

# Initialize database
if __name__ == "__main__":
    create_db_and_tables()
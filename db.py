from sqlmodel import Field, SQLModel, create_engine, Session, select
from models import metadata, Coach, Team, Facility
import pandas as pd 

sqlite_file_name = "/tmp/db.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db():
    SQLModel.metadata.create_all(engine)
    # Check and insert default records if tables are empty
    with Session(engine) as session:
        # Check if 'Coach' table is empty
        if not session.execute(select(Coach)).scalars().first():
            # Insert default coach
            default_coach = Coach(name="Default Coach")
            session.add(default_coach)
            session.commit()

        # Check if 'Facility' table is empty
        if not session.execute(select(Facility)).scalars().first():
            # Insert default facility
            default_facility = Facility(name="Default Facility", floor_type="real")
            session.add(default_facility)
            session.commit()

        # Check if 'Team' table is empty
        if not session.execute(select(Team)).scalars().first():
            # Insert default team (coach_id set to 1 as Default Coach)
            default_team = Team(name="Default Team", gender="M", age_group=18, coach_id=1)
            session.add(default_team)
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
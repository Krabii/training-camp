from enum import Enum
from sqlmodel import Field, Session, SQLModel, Relationship, MetaData

metadata = MetaData()  # Define a single metadata instance


class Coach(SQLModel, table=True):
    __tablename__ = "coach"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # teams: list["Team"] = Relationship(back_populates="coach")


class Team(SQLModel, table=True):
    __tablename__ = "team"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    gender: str = Field(default="M")
    age_group: int

    coach_id: int | None = Field(default=None, foreign_key="coach.id")
    # coach: Coach | None = Relationship(back_populates="teams")


class Facility(SQLModel, table=True):
    __tablename__ = "facility"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    floor_type: str = Field(default="real")


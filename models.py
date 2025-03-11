from enum import Enum
from sqlmodel import Field, Session, SQLModel, Relationship


class Gender(Enum):
    M = "M"
    F = "F"
    MIXED = "MIXED"
 

class Coach(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    teams: list["Team"] = Relationship(back_populates="coach")


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    gender: Gender = Field(default=Gender.M)
    age_group: int

    coach_id: int | None = Field(default=None, foreign_key="coach.id")
    coach: Coach | None = Relationship(back_populates="teams")


class Facility(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


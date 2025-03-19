from enum import Enum
from sqlmodel import Field, Session, SQLModel, Relationship, MetaData, Column
from datetime import time, datetime, date
from sqlalchemy import JSON
from typing import List, Optional


metadata = MetaData()  # Define a single metadata instance


class Priority(str, Enum):
    MANDATORY = 'mandatory'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class Day(str, Enum):
    MON = "mon"
    TUE = "tue"
    WED = "wed"
    THU = "thu"
    FRI = "fri"
    SAT = "sat"
    SUN = "sun"
    WEEKDAY = "weekday"
    WEEKEND = "weekend"
    ALL = "all"


class Instructor(SQLModel, table=True):
    __tablename__ = "instructor"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    groups: list["Group"] = Relationship(back_populates="instructor")


class Group(SQLModel, table=True):
    __tablename__ = "group"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    gender: str = Field(default="M")
    age_group: int

    instructor_id: int | None = Field(default=None, foreign_key="instructor.id", nullable=False)
    instructor: Instructor | None = Relationship(back_populates="groups")


class VenueTagLink(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    venue_id: int | None = Field(default=None, foreign_key="venue.id", primary_key=True, nullable=False)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True, nullable=False)


class Venue(SQLModel, table=True):
    __tablename__ = "venue"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    
    tags: list["Tag"] = Relationship(back_populates="facilities", link_model=VenueTagLink)


class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(...)

    facilities: list[Venue] = Relationship(back_populates="tags", link_model=VenueTagLink)


class Activity(SQLModel, table=True):
    __tablename__ = "activity"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    
    description: str = Field(...)
    duration_minutes: int = Field(...)


class ActivityInstructor(SQLModel, table=True):
    __tablename__ = "activity_instructor"
    __table_args__ = {"extend_existing": True}

    activity_id: int | None = Field(default=None, foreign_key="activity.id", primary_key=True, nullable=False)
    instructor_id: int | None = Field(default=None, foreign_key="instructor.id", primary_key=True, nullable=False)
    priority: Priority = Field(default=Priority.HIGH)


class ActivityRestriction(SQLModel):
    """
    Only onee can be set.
    """

    earliest_start: time = None  # Activity earliest starting time
    latest_start: time = None  # Activity latest starting time
    earliest_end: time = None  # Activity earliest end time
    latest_end: time = None  # Activity latest end time
    on_day: Day = None  # Activity will be programed on this day according to the priority provided
    not_on_day: Day = None  # Avoid programming on this day according to the priority provided
    tag_id: int = None  # The Venue assigned should have this Tag. Use Priority accordingly
    instructor_id: int = None  # The Instructor assigned should be this one. Use Priority accordingly
    venue_id: int = None  # Activity Should be assigned on this venue. Use Priority accordingly


class Restriction(SQLModel, table=True):
    __tablename__ = "restriction"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    restriction: str = Field(sa_column=Column(JSON))  # Store ActivityRestriction as JSON
    priority: Priority = Field(default=Priority.HIGH)

    def set_restriction(self, restriction: ActivityRestriction):
        """Store ActivityRestriction as a JSON string."""
        self.restriction = json.dumps(restriction.model_dump())

    def get_restriction(self) -> ActivityRestriction:
        """Retrieve ActivityRestriction from JSON."""
        return ActivityRestriction(**json.loads(self.restriction))


from enum import Enum
from sqlmodel import Field, Session, SQLModel, Relationship, MetaData, Column, ForeignKey
from datetime import time, datetime, date
from sqlalchemy import JSON
from typing import List, Optional, Dict


metadata = MetaData()  # Define a single metadata instance


# Sets and Enums, non DB
# --------------

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


class DayPlanningTimePeriod(SQLModel, table=True):
    __tablename__ = "day_planning_time_period"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    day: Day = Field(..., unique=True)
    opening_time: time
    closing_time: time
 

# Tagging system: Polymorphic Tag any of the main entities
# --------------------------------------------------------

class TagLink(SQLModel, table=True):
    __tablename__ = "tag_link"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    tag_id: int = Field(ForeignKey("tag.id"), primary_key=True)
    entity_id: int | None = Field(default=None, primary_key=True)  # ID of Venue, Group, or Instructor
    entity_type: str = Field(default=None, primary_key=True)  # e.g., "venue", "group", "instructor"


class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(...)


# Base Entities, Group, Instructor, Venue, Activity
# -------------------------------------------------

class Instructor(SQLModel, table=True):
    __tablename__ = "instructor"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Group(SQLModel, table=True):
    __tablename__ = "group"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    gender: str = Field(default="M")
    age_group: int

    # Relationship to Activities
    activities: List["Activity"] = Relationship(back_populates="group")


class Venue(SQLModel, table=True):
    __tablename__ = "venue"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Activity(SQLModel, table=True):
    __tablename__ = "activity"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    
    description: str = Field(...)
    duration_minutes: int = Field(...)

    group_id: int = Field(foreign_key="group.id")  # Foreign Key Reference
    
    # Relationship to Group
    group: Optional[Group] = Relationship(back_populates="activities")


# RESTRICTION & RULES
# -------------------

class ActivityRestriction(SQLModel):
    """
    Only one can be set.
    """

    earliest_start: Dict[Day, time] = None  # Activity earliest starting time
    latest_start: Dict[Day, time] = None  # Activity latest starting time
    earliest_end: Dict[Day, time] = None  # Activity earliest end time
    latest_end: Dict[Day, time] = None  # Activity latest end time
    on_day: List[Day] = None  # Activity can be programed on this day according to the priority provided
    not_on_day: List[Day] = None  # Avoid programming on this day according to the priority provided
    tag: Dict[str, int] = None  # The Entity assigned should have this Tag. Use Priority accordingly
    instructor_id: int = None  # The Instructor assigned should be this one. Use Priority accordingly
    venue_id: int = None  # Activity Should be assigned on this venue. Use Priority accordingly
    group_id: int = None  # Group Should be assigned this activity. Use Priority accordingly


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


from dataclasses import dataclass
from enum import Enum
import json
from sqlmodel import Field, Session, SQLModel, Relationship, MetaData, Column, ForeignKey
from datetime import time, datetime, date, timedelta
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
 

class HashMixin:
    """Generates a hash based on all fields of the model."""
    def __hash__(self):
        """Generates a hash based on the primary key (id)."""
        return hash(self.id) if self.id is not None else super().__hash__()

    def __eq__(self, other):
        """Ensures that equality is based on id comparison."""
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False


# Tagging system: Polymorphic Tag any of the main entities
# --------------------------------------------------------

class TagLink(SQLModel, table=True):
    __tablename__ = "tag_link"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    tag_id: int = Field(ForeignKey("tag.id"), primary_key=True)
    entity_id: int | None = Field(default=None, primary_key=True)  # ID of Venue, Group, or Instructor
    entity_type: str = Field(default=None, primary_key=True)  # e.g., "venue", "group", "instructor"


class Tag(SQLModel, HashMixin, table=True):
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(...)


# Base Entities, Group, Instructor, Venue, Activity
# -------------------------------------------------

class Instructor(SQLModel, HashMixin, table=True):
    __tablename__ = "instructor"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Group(SQLModel, HashMixin, table=True):
    __tablename__ = "group"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    gender: str = Field(default="M")
    age_group: int

    # Relationship to Activities
    activities: List["Activity"] = Relationship(back_populates="group")


class Venue(SQLModel, HashMixin, table=True):
    __tablename__ = "venue"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class Activity(SQLModel, HashMixin, table=True):
    __tablename__ = "activity"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table errors

    id: int | None = Field(default=None, primary_key=True)
    
    description: str = Field(...)
    duration_minutes: int = Field(...)
    num_sessions: int = Field(..., description="How many sessions should be planned.")
    step_minutes: int = Field(..., ge=5, le=60)

    group_id: int = Field(foreign_key="group.id")  # Foreign Key Reference
    
    # Relationship to Group
    group: Optional[Group] = Relationship(back_populates="activities")

    # @root_validator(pre=True)
    # def check_multiple_of_5(cls, values):
    #     step_minutes = values.get("step_minutes")
        
    #     if step_minutes % 5 != 0:
    #         raise ValueError("step_minutes must be a multiple of 5.")
        
    #     return values


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

@dataclass
class ScheduledEvent():
    title: str
    days_of_week: int
    start_time: time
    end_time: time
    activity_id: int
    group_id: int
    instructor_id: int
    venue_id: int

    def to_dict(self):
        return {
            "title": self.title,
            "days_of_week": self.days_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "activity_id": self.activity_id,
            "group_id": self.group_id,
            "instructor_id": self.instructor_id,
            "venue_id": self.venue_id,
        }


class Schedule(SQLModel, table=True):
    __tablename__ = "schedule"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    proto: Optional[bytes] = Field(default=None, description="Serialized proto or metadata identifier")
    result: str = Field(default=None, description="Optimization result as JSON")
    created: datetime = Field(default_factory=datetime.utcnow)


def minutes_to_day_time(total_minutes):
    days_passed = total_minutes // 1440  # 1440 minutes in a day
    day_index = (days_passed % 7) + 1
    
    minutes_remaining = total_minutes % 1440
    hours = minutes_remaining // 60
    minutes = minutes_remaining % 60
    
    return day_index, f"{hours:02d}:{minutes:02d}"

def day_time_to_minutes(day_str, time_str):
    # Map Spanish day abbreviations to indices (Mon = 0)
    day_map = {
        "mon": 0,  # Monday
        "tue": 1,  # Tuesday
        "wed": 2,  # Wednesday
        "thu": 3,  # Thursday
        "fri": 4,  # Friday
        "sat": 5,  # Saturday
        "sun": 6   # Sunday
    }

    day_index = day_map.get(day_str)
    if day_index is None:
        raise ValueError("Invalid day string")

    # Clean and split time string
    parts = time_str.strip().split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid time format: {time_str}")
    
    hours = int(parts[0])
    minutes = int(parts[1])

    total_minutes = day_index * 1440 + hours * 60 + minutes
    return total_minutes

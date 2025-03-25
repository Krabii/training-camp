from ortools.sat.python import cp_model
from models import Group, Instructor, Venue, Activity, DayPlanningTimePeriod, Day
from typing import List
from dataclasses import dataclass

@dataclass
class Instance:
    groups: List[Group]
    instructors: List[Instructor]
    venues: List[Venue]
    activities: List[Activity]
    opening_times: List[DayPlanningTimePeriod]


class TimetableSolver:
    
    def __init__(self, instance: Instance):

        self.groups = instance.groups
        self.instructors = instance.instructors
        self.venues = instance.venues
        self.activities = instance.activities
        self.opening_times = instance.opening_times

        self.horizon = 1000  # TODO: calculate from opening times in minutes
        self.step = 15  # In minutes the steping of intervals

        self.model = cp_model.CpModel()

        self.venue_vars = {
            a: {venue: model.new_bool_var(f"{a}_in_{venue}") for venue in self.venues}
            for a in self.activities
        }

        self.instructor_vars = {
            a: {i: model.new_bool_var(f"{a}_in_{i}") for i in self.instructors}
            for a in self.activities
        }

        self.starts = {
            a: self.model.new_int_var(0, self.horizon, f"{a}")
            for a in self.activities
        }

        self.ends = {
            a: self.model.new_int_var(0, self.horizon, f"{a}")
            for a in self.activities
        }

        self.venue_intervals = {
            a: {
                # We need a separate interval for each venue
                v: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.venue_vars[a][v]
                    )
                    for v in self.venues
            }
            for a in self.activities
        }

        self.instructor_intervals = {
            a: {
                # We need a separate intervals for each venue
                i: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.instructor_intervals[a][i]
                    )
                    for i in self.instructors
            }
            for a in self.activities
        }

        self.group_intervals = {
            a: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.assigned[a]
                    )
                }

        # Restrictions
        # HARD Constraints

        # Ensure each activity is assigned to exactly one venue
        for a in self.activities:
            self.model.add_at_most_one([self.venue_vars[a][v] for v in self.venues])
            self.model.add_at_most_one([self.instructor_vars[a][i] for i in self.instructors])

        # No overlap
        for g in self.groups:
            self.model.add_no_overlap(self.group_intervals[a] for a in self.activities if self.activities[a].group_id == g.id)

        for v in self.venues:
            self.model.add_no_overlap(self.venue_intervals[a][v] for a in self.activities)

        for v in self.instructors:
            self.model.add_no_overlap(self.instructor_intervals[a][i] for a in self.activities)


        # Solve model
        self.solver = cp_model.CpSolver()
        self.solver.parameters.log_search_progress = True

        self.solver.solve(self.model)
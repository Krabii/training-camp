from ortools.sat.python import cp_model
from models import Group, Instructor, Venue, Activity, DayPlanningTimePeriod, Day, ScheduledEvent, minutes_to_day_time, day_time_to_minutes
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

        self.groups = {i.id: i for i in instance.groups}
        self.instructors = {i.id: i for i in instance.instructors}
        self.venues = {i.id: i for i in instance.venues}
        self.activities = {str(i.id) + '_' + str(x): i for i in instance.activities for x in range(1, i.num_sessions + 1)}
        self.opening_times = {i.id: i for i in instance.opening_times}

        self.valid_intervals = []
        for o in self.opening_times:
            window = self.opening_times[o]
            from_minute = day_time_to_minutes(window.day.value, str(window.opening_time))
            to_minute = day_time_to_minutes(window.day.value, str(window.closing_time))
            self.valid_intervals.append((from_minute, to_minute))

        # Sets
        self.G = [g.id for g in instance.groups]
        self.I = [i.id for i in instance.instructors]
        self.V = [v.id for v in instance.venues]
        self.A = list(self.activities.keys())

        self.horizon = 10080  # minutes in a full week

    def build(self):

        self.model = cp_model.CpModel()

        self.assigned = {
            a: self.model.new_bool_var(f"{a}_assigned") for a in self.A
        }

        self.venue_vars = {
            a: {v: self.model.new_bool_var(f"{a}_in_{v}") for v in self.V}
            for a in self.A
        }

        self.instructor_vars = {
            a: {i: self.model.new_bool_var(f"{a}_in_{i}") for i in self.I}
            for a in self.A
        }

        self.starts = {
            a: self.model.new_int_var_from_domain(cp_model.Domain.FromIntervals(self.valid_intervals),f"{a}")
            for a in self.A
        }

        self.ends = {
            a: self.model.new_int_var_from_domain(cp_model.Domain.FromIntervals(self.valid_intervals),f"{a}")
            for a in self.A
        }

        for a in self.A:
            self.model.add(self.ends[a] == self.starts[a] + self.activities[a].duration_minutes)

        self.venue_intervals = {
            a: {
                # We need a separate interval for each venue
                v: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.venue_vars[a][v],
                    f"{a}_in_{v}"
                    )
                    for v in self.V
            }
            for a in self.A
        }

        self.instructor_intervals = {
            a: {
                # We need a separate intervals for each instructor
                i: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.instructor_vars[a][i],
                    f"{a}_from_{i}"
                    )
                    for i in self.I
            }
            for a in self.A
        }

        self.group_intervals = {
            # We need a separate intervals for each group
            a: self.model.new_optional_fixed_size_interval_var(
                    self.starts[a],
                    self.activities[a].duration_minutes,
                    self.assigned[a],
                    f"{a}"
                    )
                    for a in self.A
                }

        # Restrictions
        # HARD Constraints

        # Ensure each activity is assigned to exactly one venue and one instructor
        # TODO: Adjust for capacity. A venue can host an joint activity for two or more groups or two activities at the same time.
        # TODO: A Activity can be given be more than one instructor
        for a in self.A:
            self.model.add_at_most_one([self.venue_vars[a][v] for v in self.V])
            self.model.add_at_most_one([self.instructor_vars[a][i] for i in self.I])

        # No overlap
        for g in self.G:
            self.model.add_no_overlap(self.group_intervals[a] for a in self.A if self.activities[a].group_id == g)

        for v in self.V:
            self.model.add_no_overlap(self.venue_intervals[a][v] for a in self.A)

        for i in self.I:
            self.model.add_no_overlap(self.instructor_intervals[a][i] for a in self.A)

        # TODO: DO NOT USE non scheduling windows, prohibided times
        
        # OBJECTIVES
        self.model.maximize(sum(self.assigned[a] for a in self.A))
        
        # Solve model
        self.solver = cp_model.CpSolver()
        self.solver.parameters.log_search_progress = True
        self.solver.solve(self.model)

        # Results
        scheduled_events = []
        for a in self.A:
            # instructor_id = self.instructor_vars[a][i]
            # venue_id = self.venue_vars[a][i]
            # Calculate Start, End
            start_day, start_time = minutes_to_day_time(self.solver.value(self.starts[a]))
            end_day, end_time = minutes_to_day_time(self.solver.value(self.starts[a]) + self.activities[a].duration_minutes)
            scheduled_events.append(ScheduledEvent(
                title=self.activities[a].description,
                days_of_week=start_day,
                start_time=start_time,
                end_time=end_time,
                activity_id=self.activities[a].id,
                group_id=self.activities[a].group_id,
                instructor_id=None,
                venue_id=None
                ))
        return scheduled_events, self.model.Proto().SerializeToString()
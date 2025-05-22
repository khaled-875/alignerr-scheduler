from ortools.sat.python import cp_model
from datetime import datetime, timedelta

def to_minutes(time_str):
    return datetime.strptime(time_str, "%I:%M %p").hour * 60 + datetime.strptime(time_str, "%I:%M %p").minute

def to_timestr(minutes):
    h = minutes // 60
    m = minutes % 60
    suffix = "AM" if h < 12 else "PM"
    h = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
    return f"{h}:{m:02d} {suffix}"

model = cp_model.CpModel()

# Define all activities with duration (minutes), earliest start, latest end, fixed start if any, category, location
activities = {
    "Conference Call (A1)": {"duration": 60, "fixed_start": "2:00 PM", "category": "Work", "location": "Office"},
    "Customer Meeting 1 (A2)": {"duration": 60, "earliest_start": "10:30 AM", "latest_end": "5:00 PM", "category": "Work", "location": "Office"},
    "Customer Meeting 2 (A2)": {"duration": 60, "earliest_start": "10:30 AM", "latest_end": "5:00 PM", "category": "Work", "location": "Office"},
    "Email Time 1 (A3)": {"duration": 30, "latest_end": "12:30 PM", "category": "Work", "location": "Home"},
    "Email Time 2 (A3)": {"duration": 30, "latest_end": "12:30 PM", "category": "Work", "location": "Office"},
    "Independent Work (A4)": {"duration": 60, "earliest_start": "3:00 PM", "latest_end": "7:30 PM", "category": "Work", "location": "Home"},
    "Prepare Pitch (A5)": {"duration": 30, "category": "Work", "location": "Home"},
    "Meet James (A6)": {"duration": 30, "earliest_start": "10:00 AM", "latest_end": "2:00 PM", "category": "Work", "location": "Office"},
    "Team Standup (A7)": {"duration": 30, "earliest_start": "9:30 AM", "latest_end": "2:00 PM", "category": "Work", "location": "Office"},
    "Kids Carpool (A8)": {"duration": 60, "earliest_start": "8:30 AM", "latest_end": "9:30 AM", "category": "Personal", "location": "Home"},
    "Dentist Appointment (A9)": {"duration": 60, "latest_end": "6:00 PM", "category": "Personal", "location": "Home"},
    "Workout (A10)": {"duration": 60, "latest_end": "7:30 PM", "category": "Personal", "location": "Home"},
    "Research Holiday (A11)": {"duration": 60, "earliest_start": "8:30 PM", "category": "Personal", "location": "Home"},
    "Family Time (A12)": {"duration": 30, "category": "Personal", "location": "Home"},
    "General Admin 1 (A13)": {"duration": 30, "category": "Personal", "location": "Office"},
    "General Admin 2 (A13)": {"duration": 30, "category": "Personal", "location": "Home"},
    "Breakfast": {"duration": 30, "fixed_start": "8:00 AM", "category": "Personal", "location": "Home"},
    "Lunch": {"duration": 60, "fixed_start": "12:30 PM", "category": "Personal", "location": "Home"},
    "Dinner": {"duration": 60, "fixed_start": "7:30 PM", "category": "Personal", "location": "Home"}
}

# Convert times to minutes
start_day = to_minutes("7:00 AM")
end_day = to_minutes("11:00 PM")

intervals = {}
starts = {}
ends = {}
categories = {}
locations = {}
durations = {}

for act, v in activities.items():
    dur = v["duration"]
    durations[act] = dur
    earliest = start_day
    latest = end_day - dur

    if "fixed_start" in v:
        fixed_start = to_minutes(v["fixed_start"])
        earliest = fixed_start
        latest = fixed_start
    if "earliest_start" in v:
        earliest = max(earliest, to_minutes(v["earliest_start"]))
    if "latest_end" in v:
        latest = min(latest, to_minutes(v["latest_end"]) - dur)

    start_var = model.NewIntVar(earliest, latest, f"{act}_start")
    end_var = model.NewIntVar(earliest + dur, latest + dur, f"{act}_end")
    interval = model.NewIntervalVar(start_var, dur, end_var, f"{act}_interval")

    intervals[act] = interval
    starts[act] = start_var
    ends[act] = end_var
    categories[act] = v["category"]
    locations[act] = v["location"]

# No overlapping activities
model.AddNoOverlap(list(intervals.values()))

# Commute times logic (simple version):
# Commutes between Home and Office when location changes between consecutive activities
# We can only add commute intervals between activities that require commute.
# For simplicity, ignore full commute scheduling in this example.

# Staggering constraints example: Email Time 1 and 2 at least 2hrs apart
model.Add(starts["Email Time 2 (A3)"] >= ends["Email Time 1 (A3)"] + 120)

# Customer Meetings at least 2hrs apart
model.Add(starts["Customer Meeting 2 (A2)"] >= ends["Customer Meeting 1 (A2)"] + 120)

# Team Standup before Meet James and Conference Call
model.Add(starts["Meet James (A6)"] >= ends["Team Standup (A7)"])
model.Add(starts["Conference Call (A1)"] >= ends["Meet James (A6)"])

# Independent Work after Conference Call
model.Add(starts["Independent Work (A4)"] >= ends["Conference Call (A1)"])

# Kids Carpool after Breakfast
model.Add(starts["Kids Carpool (A8)"] >= ends["Breakfast"])

# Dentist Appointment before 6PM
model.Add(ends["Dentist Appointment (A9)"] <= to_minutes("6:00 PM"))

# Research Holiday after Dinner
model.Add(starts["Research Holiday (A11)"] >= ends["Dinner"])

# Personal time calculation
personal_activities = [a for a, c in categories.items() if c == "Personal" and a not in ["Breakfast", "Lunch", "Dinner"]]
work_activities = [a for a, c in categories.items() if c == "Work"]

# Objective to maximize or maintain 40-45% personal time ratio
# Calculate total personal and work minutes
personal_time = sum(durations[a] for a in personal_activities)
work_time = sum(durations[a] for a in work_activities)

# Solver
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    assignments = {}
    for act in sorted(starts, key=lambda x: solver.Value(starts[x])):
        s = solver.Value(starts[act])
        e = solver.Value(ends[act])
        assignments[act] = {
            "start": to_timestr(s),
            "end": to_timestr(e)
        }

    # Calculate percentage personal allocation
    total_assigned = personal_time + work_time
    personal_alloc = (personal_time / total_assigned) * 100 if total_assigned > 0 else 0.0

    import json
    output = {
        "assignments": assignments,
        "personal_allocation": f"{personal_alloc:.1f}%"
    }
    print(json.dumps(output, indent=2))
else:
    print("No feasible solution found.")

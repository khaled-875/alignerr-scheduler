# alignerr-scheduler
Constraint programming schedule example using OR-Tools

This project uses Google OR-Tools CP-SAT solver to create a daily activity schedule respecting time constraints, categories, and locations.

Key features:

Activities: Defined with durations, earliest start times, latest end times, fixed start times (if any), categories (Work or Personal), and locations (Home or Office).

Time conversion: Converts times between "HH:MM AM/PM" format and total minutes from midnight for easier constraint handling.

Interval variables: Each activity is represented as an interval variable with a start time, end time, and fixed duration.

Constraints:

No overlapping activities.

Staggering gaps between specific activities (e.g., at least 2 hours between two email sessions and between customer meetings).

Ordering constraints enforcing a logical flow (e.g., Team Standup before Meet James, which is before Conference Call).

Fixed start times for some activities (e.g., Breakfast, Lunch, Dinner).

Time windows limiting earliest start and latest end times.

Simplified commute logic: The model considers activity locations but does not explicitly schedule commute intervals in this version.

Objective and output:

Computes total personal and work time based on scheduled durations.

Calculates the percentage of personal time relative to total scheduled time.

Outputs the schedule with assigned start and end times formatted as "HH:MM AM/PM" along with the personal time percentage.

This model helps balance work and personal tasks while respecting detailed timing constraints, making it suitable for realistic daily planning scenarios.

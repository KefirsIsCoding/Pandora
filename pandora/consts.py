from enum import Enum

class Status(Enum):
    BACKLOG = 1
    WIP = 2
    DONE = 3

class DateChoices(Enum):
    ANY = "Any"
    WEEKENDS = "Weekends"
    WEEKDAYS = "Weekdays"
    MONTHLY = "Monthly"
    SPECIFIC_DATE = "Specific Date"

class WeekDays(Enum):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"



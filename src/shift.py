from datetime import datetime
import pytz


class Shift:
    def __init__(self, date_string, start_time, end_time) -> None:
        self.start_time = Shift.parse_time(date_string, start_time)
        self.end_time = Shift.parse_time(date_string, end_time)

    @staticmethod
    def parse_time(date_string: str, time_string: str) -> str:
        today = datetime.now()
        date: datetime = datetime.strptime(date_string, "%a, %b %d")
        time: datetime = datetime.strptime(time_string, "%I:%M %p")
        time = time.time()
        date_time = datetime.combine(date, time).replace(
            year=today.year if today.month != 1 else today.year + 1
        )
        return pytz.timezone("US/Pacific").localize(date_time).isoformat()

    def __repr__(self) -> str:
        return f"{self.start_time} to {self.end_time}"


def parse_times(time_str: str) -> list[str]:
    times = time_str.split(" ")
    start_time = f"{times[0]} {times[1]}"
    end_time = f"{times[2]} {times[3]}"
    return [start_time, end_time]

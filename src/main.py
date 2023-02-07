import os
from datetime import datetime

from dotenv import load_dotenv
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.shift import Shift, parse_times

# Load env vars
load_dotenv()
EMAIL = os.environ["USER"]
PASS = os.environ["PASS"]

# Init driver and waiter
driver = webdriver.Chrome()
waiter = WebDriverWait(driver, 10)


# Helper functions
def get_after_visible(locator) -> WebElement:
    return waiter.until(EC.element_to_be_clickable(locator))


def element_is_present(locator) -> bool:
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
        return True
    except:
        return False


# Begin scraping
# Login
driver.get("https://innerview.wholefoods.com/")
get_after_visible((By.CSS_SELECTOR, "input[type='email']")).send_keys(EMAIL)
get_after_visible((By.CSS_SELECTOR, "input[type='submit']")).click()
get_after_visible((By.CSS_SELECTOR, "input[type='password']")).send_keys(PASS)
get_after_visible((By.CSS_SELECTOR, "input[type='submit']")).click()

# Navigate to shift lists
waiter.until(lambda driver: driver.title == "Innerview | Home")
driver.get("https://innerview.wholefoods.com/schedule")
try:
    get_after_visible((By.CLASS_NAME, "ant-modal-close-x")).click()
except:
    pass

# Listing shifts
shifts: list[Shift] = []
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    days = get_after_visible((By.CLASS_NAME, "index_dayList_2U9G8")).find_elements(
        By.CLASS_NAME, "ant-row"
    )
    for day_div in days:
        date = day_div.find_element(By.CLASS_NAME, "ant-col-8").text
        today = datetime.now()
        if today >= datetime.strptime(date, "%a, %b %d").replace(year=today.year):
            continue
        try:
            day_div.find_element(By.CLASS_NAME, "overview-widget-row_muted_i-EPU")
        except:
            times = (
                day_div.find_element(By.CLASS_NAME, "ant-col-14")
                .find_element(By.CSS_SELECTOR, "*")
                .find_element(By.CSS_SELECTOR, "*")
                .text
            )
            [start_time, end_time] = parse_times(times)
            shifts.append(Shift(date, start_time, end_time))
    if element_is_present((By.CLASS_NAME, "index_disabled_27N4l")):
        break
    driver.find_elements(By.CLASS_NAME, "index_caret_E-6uh")[1].click()
driver.quit()

# Init Google Calendar
calendar = (
    GoogleCalendar()
)  # Somewhere under the hood it already connected to my gmail.
i = 0

# Ensure everything matches for now
for event in calendar.get_events(time_min=datetime.now(), query="Whole Foods"):
    assert event.start.isoformat() == shifts[i].start_time, "Lists are not equal"
    i += 1

# Creating events
events_created = 0
while i < len(shifts):
    event = Event("Whole Foods", shifts[i].start_time, shifts[i].end_time)
    calendar.add_event(event)
    print(f"Event created: {event}")
    events_created += 1

print(f"Total events created: {events_created}")

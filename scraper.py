import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime

from shift import Shift, parse_times

EMAIL=os.environ['USER']
PASS=os.environ['PASS']

driver = webdriver.Chrome()
waiter = WebDriverWait(driver, 10)

def get_after_visible(locator) -> WebElement:
  return waiter.until(EC.element_to_be_clickable(locator))

def element_is_present(locator) -> bool:
  try:
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    return True
  except:
    return False
driver.get("https://innerview.wholefoods.com/")
get_after_visible((By.CSS_SELECTOR, "input[type='email']")).send_keys(EMAIL)
get_after_visible((By.CSS_SELECTOR, "input[type='submit']")).click()
get_after_visible((By.CSS_SELECTOR, "input[type='password']")).send_keys(PASS)
get_after_visible((By.CSS_SELECTOR, "input[type='submit']")).click()
waiter.until(lambda driver: driver.title == 'Innerview | Home')
driver.get('https://innerview.wholefoods.com/schedule')
try: 
  get_after_visible((By.CLASS_NAME, 'ant-modal-close-x')).click()
except:
  pass

shifts: list[Shift] = []
while True:
  days = get_after_visible((By.CLASS_NAME, 'index_dayList_2U9G8')).find_elements(By.CLASS_NAME, 'ant-row')
  for day_div in days:
    date = day_div.find_element(By.CLASS_NAME, 'ant-col-8').text
    today = datetime.now()
    if (today >= datetime.strptime(date, '%a, %b %d').replace(year=today.year)):
      continue
    try:
      day_div.find_element(By.CLASS_NAME, 'overview-widget-row_muted_i-EPU')
    except:
      times = (day_div
            .find_element(By.CLASS_NAME, 'ant-col-14')
            .find_element(By.CSS_SELECTOR, '*')
            .find_element(By.CSS_SELECTOR, '*').text)
      [start_time, end_time] = parse_times(times)
      shifts.append(Shift(date, start_time, end_time))
  if element_is_present((By.CLASS_NAME, 'index_disabled_27N4l')): break
  driver.find_elements(By.CLASS_NAME, 'index_caret_E-6uh')[1].click()
driver.quit()


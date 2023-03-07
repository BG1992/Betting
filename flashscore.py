from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import csv
from datetime import timedelta, date

options = Options()
#options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')
#driver_match = webdriver.Firefox(options=options,
#                                 executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.get('https://www.flashscore.pl/pilka-reczna/hiszpania/liga-asobal/wyniki/')
more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
more_events.click()
sleep(3)
events = driver.find_elements_by_xpath("//div[contains(@class, 'match')]")
for e in events[:1]:
    print(e.text)
    e.click()

driver.switch_to_window(driver.window_handles[1])
sleep(3)
odds = driver.find_element_by_xpath('//*[@id="a-match-odds-comparison"]')
odds.click()
sleep(3)
odds_table = driver.find_element_by_xpath('//*[@id="odds_1x2"]')
rows = odds_table.find_elements_by_class_name('odd') + odds_table.find_elements_by_class_name('even')
for row in rows:
    row_ = row.find_element_by_class_name('detail-blogos')
    row_.get_attribute('title') #buk
    odds_row = row.find_elements_by_xpath(".//span[contains(@class, 'odds-wrap')]")
    for o in odds_row:
        print(o.get_attribute('eu'))


odds = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[4]/div[7]/div[2]/div[2]/ul/li[3]/span/a')
odds.click()
sleep(3)
tables = odds.find_elements_by_xpath("//table[contains(@id, 'odds_ou')]")
for tb in tables:
    print(tb.get_attribute('id'))
    rows = tb.find_elements_by_class_name('odd') + tb.find_elements_by_class_name('even')
    for row in rows:
        row_ = row.find_element_by_class_name('elink')
        row_.get_attribute('title')  # buk
        odds_row = row.find_elements_by_xpath(".//span[contains(@class, 'odds-wrap')]")
        for o in odds_row:
            print(o.get_attribute('eu'))

driver.close()
driver.switch_to_window(driver.window_handles[0])
driver.quit()
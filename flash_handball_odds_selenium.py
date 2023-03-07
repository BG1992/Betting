from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-reczna/dania/bambusa-kvindeligaen-women-2020-2021/wyniki/'
driver.get(web_path)
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

i = input()
events = driver.find_elements_by_xpath("//div[contains(@class, 'match')]")
events_text = list(map(lambda x: x.text.split('\n'), events))
events_ids = list(map(lambda x: x.get_attribute('id').replace('g_1_', ''), events))

ct = 0
print(len(events))
sleep(3)
for i in range(len(events_text)):
    e = events[i]
    #print(i)
    e_text = events_text[i]
    row = [e_text[0], e_text[1], e_text[2], e_text[3], e_text[4]]
    e_id = events_ids[i].replace('g_7_', '')
    driver.get('https://www.flashscore.pl/mecz/' + e_id + '/#zestawienie-kursow/powyzej-ponizej/koniec-meczu')
    sleep(2)
    t = driver.find_elements_by_xpath("//div[contains(@class, 'ui-table__row')]")
    for el in t:
        if '.5|' in el.text.replace('\n', '|'):
            row.append(el.text.replace('\n', '|'))
    print(row)

driver.quit()
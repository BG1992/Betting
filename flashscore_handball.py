from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import csv
from collections import defaultdict

options = Options()
#options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

main_path = 'https://www.flashscore.pl/pilka-reczna/dania/herre-handbold-ligaen-2017-2018/wyniki/'
driver.get(main_path)
input()
more_events = driver.find_elements_by_xpath("//div[contains(@id, 'g_7_')]")
more_events_ids = []
for el in more_events:
    more_events_ids.append((el.get_attribute('id')[4:], el.text.split('\n')))

name = '_'.join(main_path.split('/')[4:6])
with open(r'C:\Users\Marzena\PycharmProjects\DS\flashscore_handball\Kursy_' + name +'.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    for el in more_events_ids:
        #https://www.flashscore.pl/mecz/lpojZ0lo/#zestawienie-kursow/powyzej-ponizej/koniec-meczu
        path = 'https://www.flashscore.pl/mecz/' + el[0] + \
               '/#zestawienie-kursow/powyzej-ponizej/koniec-meczu'
        tx = el[1]
        _row = tx
        driver.get(path)
        sleep(3)
        nums = driver.find_elements_by_xpath("//div[contains(@class, 'ui-table__row')]")
        for num in nums:
            _row.append(num.text.replace('\n', '|'))
        try:
            writer.writerow(_row)
        except: pass
        print(_row)

driver.close()
#driver.switch_to_window(driver.window_handles[0])
driver.quit()
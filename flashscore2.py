from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import csv
from datetime import timedelta, date

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
driver.get('https://www.flashscore.pl/pilka-nozna/dania/superliga-2019-2020/wyniki/')
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

sleep(3)
events = driver.find_elements_by_xpath("//div[contains(@class, 'match')]")
ct = 0
with open('flashscore.csv', 'a', newline='') as csvfile:
    _writer = csv.writer(csvfile, delimiter=';')
    print(len(events))
    sleep(3)
    for e in events[2:]:
        row_csv = []

        #date, teams
        print(ct)
        row_csv.append(e.text)
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
            buk_name = row_.get_attribute('title') #buk
            odds_row = row.find_elements_by_xpath(".//span[contains(@class, 'odds-wrap')]")
            for o in odds_row:
                row_csv.append(buk_name + ' 1x2 ' + str(o.get_attribute('eu')))
                #print(o.get_attribute('eu'))

        odds = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[4]/div[7]/div[2]/div[2]/ul/li[3]/span/a')
        odds.click()
        sleep(3)
        tables = odds.find_elements_by_xpath("//table[contains(@id, 'odds_ou')]")
        for tb in tables:
            att = tb.get_attribute('id')
            rows = tb.find_elements_by_class_name('odd') + tb.find_elements_by_class_name('even')
            for row in rows:
                row_ = row.find_element_by_class_name('elink')
                buk_name = row_.get_attribute('title')  # buk
                odds_row = row.find_elements_by_xpath(".//span[contains(@class, 'odds-wrap')]")
                for o in odds_row:
                    row_csv.append(buk_name + ' ' + att + ' ' + str(o.get_attribute('eu')))
                    #print(o.get_attribute('eu'))

        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        sleep(1)
        driver.execute_script('window.scrollBy(0, 30)')
        sleep(1)
        try:
            _writer.writerow(row_csv)
        except: pass
        ct += 1

driver.quit()
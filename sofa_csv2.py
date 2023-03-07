from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import csv
from datetime import timedelta, date

curr_date = date(2020, 10, 20)
while curr_date != date(2020, 10, 1):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Firefox(options=options,
                               executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')
    driver_match = webdriver.Firefox(options=options,
                                     executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

    if len(str(curr_date.month)) == 1:
        m = '0' + str(curr_date.month)
    else:
        m = str(curr_date.month)
    if len(str(curr_date.day)) == 1:
        d = '0' + str(curr_date.day)
    else:
        d = str(curr_date.day)
    driver.get('https://www.sofascore.com/football/' +
               str(curr_date.year) + '-' + m + '-' + d)
    # driver_match.get('https://www.sofascore.com/football/' +
    #                  str(curr_date.year) + '-' + m + '-' + d)
    with open('sofascore.csv', 'a', newline='') as csvfile:
        _writer = csv.writer(csvfile, delimiter=';')

        matches_checked = set()
        for i in range(50):
            print(i, 'scroll', curr_date)
            driver.execute_script("window.scrollTo(0, " + str(40*(i+1)) +")")
            #sleep(1)
            matches = driver.find_elements_by_xpath("//a[contains(@class, 'dhKVQJ')]")
            for m in matches:
                if m.text not in matches_checked:
                    try:
                        row = []
                        print(m.text)
                        _m = m.text.split('\n')[0].split('/')
                        row.extend([_m[2] + '20-' + _m[1] + '-' + _m[0]])
                        row.extend(m.text.split('\n')[1:])
                        driver_match.get(m.get_attribute('href'))
                        sleep(1)
                        a = driver_match.find_element_by_xpath("//ul[contains(@class, 'ciuw58-0')]")
                        print(a.text.split('\n'), 'hehe')
                        row.extend(a.text.split('\n')[:-1])
                        sleep(1)
                        results = driver_match.find_elements_by_xpath("//span[contains(@class, '1f9zoyc')]")
                        sleep(1)
                        for res in results:
                            print(res.text)
                            row.append(res.text)
                        #print(b.text)
                        asof = driver_match.find_element_by_xpath("//div[contains(@class, 'gYsVZh')]")
                        print(asof.text)
                        row.append(asof.text)
                        print('****************')
                        _writer.writerow(row)
                    except: pass
                    matches_checked.add(m.text)
    curr_date = curr_date + timedelta(days=-1)
    driver.quit()
    driver_match.quit()
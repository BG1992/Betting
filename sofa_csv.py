from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import csv
from datetime import timedelta, date

curr_date = date(2019, 1, 17)
while curr_date != date(2019, 1, 1):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Firefox(options=options,
                               executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')
    options = Options()
    # options.headless = True
    # options.add_argument("--window-size=1920,1200")
    driver.maximize_window()

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
    sleep(3)
    with open('sofascore_test.csv', 'a', newline='') as csvfile:
        _writer = csv.writer(csvfile, delimiter=';')

        ck = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
        ck.click()
        sleep(3)
        matches_checked = set()
        for i in range(50):
            print(i, 'scroll')
            driver.execute_script("window.scrollTo(0, " + str(40*(i+1)) +")")
            sleep(1)
            matches = driver.find_elements_by_xpath("//a[contains(@class, 'dhKVQJ')]")
            for m in matches:
                if m.text not in matches_checked:
                    row = []
                    print(m.text)
                    _m = m.text.split('\n')[0].split('/')
                    row.extend([_m[2] + '20-' + _m[1] + '-' + _m[0]])
                    row.extend(m.text.split('\n')[1:])
                    try:
                        m.click()
                        #driver_match.get(m.get_attribute('href'))
                        sleep(2)
                        a = driver.find_element_by_xpath("//ul[contains(@class, 'ciuw58-0')]")
                        print(a.text.split('\n'), 'hehe')
                        row.extend(a.text.split('\n')[:-1])

                        #m = driver.find_element_by_xpath("//div[contains(@class, 'ps__rail-y')]")
                        a = driver.find_element_by_xpath('/html/body/div[1]/main/div/div[2]/div/div[5]/div/div[3]')

                        a.click()
                        #driver.execute_script("arguments[0].setAttribute('style', 'top: 720px; height: 600px; right: 0px;')", m)
                        sleep(1)

                        results = driver.find_elements_by_xpath("//span[contains(@class, '1f9zoyc')]")
                        sleep(1)
                        for res in results:
                            print(res.text)
                            row.append(res.text)
                        #print(b.text)
                        print('****************')
                        try:
                            _writer.writerow(row)
                        except: pass
                    except: pass
                    matches_checked.add(m.text)
    #ps__thumb-y
    curr_date = curr_date + timedelta(days=-1)
    driver.quit()
    #driver_match.quit()
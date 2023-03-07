from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep

def check(driver):
    try:
        driver.find_element_by_xpath("//ul[contains(@class, 'ciuw58-0')]")
        return True
    except:
        return False

options = Options()
#options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')
driver_match = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.get('https://www.sofascore.com/football/2020-11-23')
matches_checked = set()
#scope = driver.find_element_by_xpath('/html/body/div[1]/main/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div')
#matches = driver.find_elements_by_xpath('/html/body/div[1]/main/div/div[2]/div/div[3]/div[2]/div/div[1]/div/div/*')
for i in range(10):
    driver.execute_script("window.scrollTo(0, " + str(100*(i+1)) +")")
    sleep(1)
    matches = driver.find_elements_by_xpath("//a[contains(@class, 'dhKVQJ')]")
    print(len(matches))
    #scroll do końca strony i z powrotem
    for m in matches:
        if m.text not in matches_checked:
            try:
                print(m.text)
                driver_match.get(m.get_attribute('href'))
                sleep(3)
                # driver.execute_script("window.scrollTo(0, 0)")
                # sleep(1)
                #
                # #print(a.text)
                # b = driver.find_element_by_xpath("//a[contains(@class, 'koniBB')]")
                # right_window = driver.find_element_by_xpath('/html/body/div[1]/main/div/div[2]/div/div[5]/div')
                # right_window_s = driver.find_element_by_class_name('ps__rail-y')
                # right_window_s.click()
                # for _ in range(10):
                #     right_window_s.send_keys(Keys.DOWN)
                a = driver_match.find_element_by_xpath("//ul[contains(@class, 'ciuw58-0')]")
                print(a.text, 'hehe')
                sleep(1)
                results = driver_match.find_elements_by_xpath("//span[contains(@class, '1f9zoyc')]")
                sleep(2)
                for res in results:
                    print(res.text)
                #print(b.text)
                print('****************')
            except: pass
            matches_checked.add(m.text)


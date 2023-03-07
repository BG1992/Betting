from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import csv
import os

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-reczna/rumunia/liga-nationala-2021-2022/wyniki/'
driver.get(web_path)

rows = []
i = input()
ind = 0
events = driver.find_elements_by_xpath("//div[contains(@id, 'g_7_')]")

for e in events:
    t = e.text.split('\n')
    rows.append(t)
    print(ind, len(events))
    ind += 1


filename = web_path.split('/')
foldername = r'C:\Users\Marzena\PycharmProjects\DS\handball_scores'

with open(os.path.join(foldername, filename[5] + '.csv'), 'w', newline = '', encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    for row in rows:
        writer.writerow(row)

driver.quit()
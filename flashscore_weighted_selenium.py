from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-nozna/wlochy/serie-a-2018-2019/wyniki/'
driver.get(web_path)
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

all_columns = ['Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole']

for g in range(7):
    all_columns.extend([str(g+0.5) + ' Under', str(g+0.5) + ' Over'])

df = pd.DataFrame(columns=all_columns[:])
i = input()
events = driver.find_elements_by_xpath("//div[contains(@class, 'match')]")
events_text = list(map(lambda x: x.text.split('\n'), events))
events_ids = list(map(lambda x: x.get_attribute('id').replace('g_1_', ''), events))

ct = 0
print(len(events))
sleep(3)
for i in range(len(events_text)):
    e = events[i]
    print(i)
    e_text = events_text[i]
    row = {'Data': [e_text[0]], 'Gospodarze': [e_text[1]], 'Goście': [e_text[2]], 'Gospodarze Gole': [e_text[3]],
           'Goście Gole': [e_text[5]]}
    e_id = events_ids[i]
    driver.get('https://www.flashscore.pl/mecz/' + e_id + '/#zestawienie-kursow/powyzej-ponizej/koniec-meczu/')
    sleep(2)
    fort_check = False
    for g in ('0.5', '1.5', '2.5', '3.5', '4.5', '5.5', '6.5'):
        odds_list = list(filter(lambda x: x.text.split('\n')[0] == g,
                           driver.find_elements_by_xpath("//div[contains(@class, '1rtP1QI')]")))
        odds_g = {}
        fort_check = False
        for odds in odds_list:
            goals, odds_over, odds_under = odds.text.split('\n')
            if not fort_check:
                if odds_under != '-' and odds_over != '-':
                    odds_g['Under'] = [float(odds_under)]
                    odds_g['Over'] = [float(odds_over)]
                    if odds.find_element_by_xpath(".//a[contains(@class, '2cfGV84')]").get_attribute('title') == 'eFortuna.pl':
                        fort_check = True
            else:
                row[goals + ' Under'] = odds_g['Under']
                row[goals + ' Over'] = odds_g['Over']
                break

    df = df.append(pd.DataFrame(row), ignore_index=True)

df.to_csv('C:/Users/Marzena/PycharmProjects/DS/flashscore_weighted_seasons/'
          + web_path.split('/')[-3] + '.csv', encoding='utf-8')

driver.quit()
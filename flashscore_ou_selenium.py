from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd
from collections import defaultdict

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-nozna/wlochy/serie-a-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/anglia/premier-league-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/francja/ligue-1-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/hiszpania/laliga-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/niemcy/bundesliga-2020-2021/wyniki/'
#'https://www.flashscore.pl/pilka-nozna/wlochy/serie-a-2020-2021/wyniki/'
driver.get(web_path)
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

all_columns = ['Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole']

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
    odds_dict = defaultdict(list)
    for odds in driver.find_elements_by_xpath("//div[contains(@class, 'ui table__row')]"):

        odds_txt = odds.text.split('\n')
        try: odds_dict[odds_txt[0] + 'o'].append(float(odds_txt[1]))
        except ValueError: odds_dict[odds_txt[0] + 'o'].append(1)
        try: odds_dict[odds_txt[0] + 'u'].append(float(odds_txt[2]))
        except ValueError: odds_dict[odds_txt[0] + 'u'].append(1)

        for k in odds_dict:
            row[k + '_min'] = min(odds_dict[k])
            row[k + '_avg'] = sum(odds_dict[k])/len(odds_dict[k])
            row[k + '_max'] = max(odds_dict[k])

    df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)

df.to_csv('C:/Users/Marzena/PycharmProjects/DS/flashscore_ou/'
          + web_path.split('/')[-3] + '.csv', encoding='utf-8')

driver.quit()
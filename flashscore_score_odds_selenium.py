from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa-2019-2020/wyniki/'
driver.get(web_path)
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

all_columns = ['Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole', 'odds_1', 'odds_0', 'odds_2']

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
    driver.get('https://www.flashscore.pl/mecz/' + e_id + '/#szczegoly-meczu/szczegoly-meczu')
    sleep(3)
    t = driver.find_elements_by_xpath("//div[contains(@class, 'odds___2aJyDCz')]")[0]
    row['odds_1'] = t.text.split('\n')[1]
    row['odds_0'] = t.text.split('\n')[3]
    row['odds_2'] = t.text.split('\n')[5]
    df = df.append(pd.DataFrame(row), ignore_index=True)

df.to_csv('C:/Users/Marzena/PycharmProjects/DS/flashscore_score_odds_seasons/'
          + web_path.split('/')[-3] + '.csv', encoding='utf-8')

driver.quit()
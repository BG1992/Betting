from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import pandas as pd

options = Options()
#options.headless = True
driver = webdriver.Firefox(options=options,
                           executable_path=r'C:\Users\Marzena\AppData\Local\Programs\Python\Python38\libs\geckodriver.exe')

driver.maximize_window()
web_path = 'https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa/'
driver.get(web_path)
try:
    more_events = driver.find_element_by_xpath("//a[contains(@class, 'event__more')]")
    more_events.click()
except: pass

all_columns = ['Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole']
stat_columns = ['Posiadanie piłki', 'Sytuacje bramkowe', 'Strzały na bramkę', 'Strzały niecelne',
                           'Strzały zablokowane', 'Rzuty wolne', 'Rzuty rożne', 'Spalone',
                           'Wrzuty z autu', 'Interwencje bramkarzy', 'Faule', 'Żółte kartki',
                           'Podania', 'Bloki', 'Ataki', 'Niebezpieczne ataki']

for s in stat_columns:
    for ha in ['Gospodarze', 'Goście']:
        all_columns.append(ha + ' ' + s)

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
    try:
        row = {'Data': [e_text[0]], 'Gospodarze': [e_text[1]], 'Goście': [e_text[2]], 'Gospodarze Gole': [e_text[3]],
               'Goście Gole': [e_text[4]], 'HT': ['(' + e_text[5][1] + ' - ' + e_text[6][1] + ')']}
        e_id = events_ids[i]
        driver.get('https://www.flashscore.pl/mecz/' + e_id + '/#szczegoly-meczu/statystyki-meczu/')
        sleep(2)
        for e_stat in driver.find_elements_by_xpath("//div[contains(@class, 'statRow')]"):
            stat = e_stat.text.split('\n')
            row['Gospodarze ' + stat[1]] = [stat[0]]
            row['Goście ' + stat[1]] = [stat[2]]
        df = df.append(pd.DataFrame(row), ignore_index=True)
    except: pass

df.to_csv('C:/Users/Marzena/PycharmProjects/DS/flashscore_gap_seasons/'
          + web_path.split('/')[-3] + '_FT.csv', encoding='utf-8')

driver.quit()
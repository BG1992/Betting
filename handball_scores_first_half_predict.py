import csv
import os
import numpy as np
from collections import defaultdict

foldername = r'C:\Users\Marzena\PycharmProjects\DS\handball_scores'
files = ['liga-asobal-2021-2022.csv']

h = 0.5
a = 1-h
std_coef = 0.65

predictions = [('Hamburg', 'Lemgo'), ('Hannover-Burgdorf', 'Flensburg-H.'), ('Stuttgart', 'Fuchse Berlin'),
               ('Göppingen', 'Kiel'), ('Leipzig', 'MT Melsungen'), ('SC Magdeburg', 'N-Lubbecke')]

# predictions = [('Bacau', 'CSM Bucuresti'), ('Dinamo Bucuresti', 'Potaissa Turda'), ('Minaur Baia Mare', 'Buzau'),
#                ('Alexandria', 'Cluj'), ('Vaslui', 'Timisoara')]
#
predictions = [('Brno', 'Hranice'), ('Nove Veseli', 'Lovosice'), ('Jicin', 'Dukla Prague'),
               ('Zubri', 'Koprivnice'), ('Frydek-Mistek', 'Malomerice')]
#
predictions = [('Barcelona', 'Puente Genil'), ('Nava', 'Atl. Valladolid'), ('Antequera', 'Morrazo Cangas'),
               ('CD Bidasoa Irun', 'Torrelavega'), ('La Rioja', 'Huesca')]

probs = {}
for f in files:
    rows = []
    teams = set()
    with open(os.path.join(foldername, f), encoding='utf-8') as g:
        reader = csv.reader(g, delimiter=';')
        for row in reader:
            if row[1] in ('Po karn.', 'Po dogr.'):
                try: rows.append([row[2], row[3], int(row[7]), int(row[8])])
                except: pass
                teams.add(row[2])
                teams.add(row[3])
            elif row[1] not in ('Walkower', 'Anulowane'):
                rows.append([row[1], row[2], int(row[5]), int(row[6])])
                teams.add(row[1])
                teams.add(row[2])
    rows = rows[::-1]
    scores_achieved = defaultdict(list)
    scores_lost = defaultdict(list)
    dists = []
    for k in range(len(rows)):
        row = rows[k]
        scores_achieved[row[0]].append(row[2])
        scores_achieved[row[1]].append(row[3])
        scores_lost[row[0]].append(row[3])
        scores_lost[row[1]].append(row[2])
    for k in range(len(predictions)):
        row = predictions[k]
        if len(scores_achieved[row[0]]) >= 5 and len(scores_achieved[row[1]]) >= 5 \
                and len(scores_lost[row[0]]) >= 5 and len(scores_lost[row[1]]) >= 5:
            match_interval = (h*(np.mean(scores_achieved[row[0]]) - std_coef*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) - std_coef*np.std(scores_lost[row[1]])) +
                             h*(np.mean(scores_achieved[row[1]]) - std_coef*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) - std_coef*np.std(scores_lost[row[0]])),
                             h*(np.mean(scores_achieved[row[0]]) + std_coef*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) + std_coef*np.std(scores_lost[row[1]])) +
                             h*(np.mean(scores_achieved[row[1]]) + std_coef*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) + std_coef*np.std(scores_lost[row[0]])))
            print(row, match_interval)

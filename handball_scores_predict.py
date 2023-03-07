import csv
import os
import numpy as np
from collections import defaultdict

foldername = r'C:\Users\Marzena\PycharmProjects\DS\handball_scores'
files = ['bundesliga-2021-2022.csv']

h = 0.5
a = 1-h
std_coef = 0.9
std_coef2 = 0.8

# predictions = [('Viborg K', 'Copenhagen K'), ('Horsens K', 'Skanderborg K'), ('Randers K', 'Silkeborg-Voel K'),
#                ('Aarhus United K', 'Ringkøbing K'), ('Herning-Ikast K', 'Esbjerg K')]

# predictions = [('Steaua Bucharest', 'Buzau'), ('Alexandria', 'Dobrogea Sud'), ('Minaur Baia Mare', 'Timisoara'),
#                ('Vaslui', 'CSM Focsani')]

predictions = [('MMTS Kwidzyn', 'Wybrzeże Gdańsk'), ('Vive Kielce', 'Stal Mielec'), ('Pogoń Szczecin', 'Azoty-Puławy'),
               ('Chrobry Głogów', 'Unia Tarnow'), ('Górnik Zabrze', 'Piotrkowianin'), ('MKS Kalisz', 'Zagłębie Lubin')]

predictions = [('HSG Graz', 'West Wien'), ('Bregenz', 'Barnbach/K.'), ('Fuchse', 'Alpla HC Hard')]

predictions = [('Minden', 'Göppingen'), ('MT Melsungen', 'Stuttgart'), ('N-Lubbecke', 'Lemgo'),
               ('Flensburg-H.', 'Rhein-Neckar'), ('Fuchse Berlin', 'SC Magdeburg'), ('Kiel', 'Hannover-Burgdorf'),
               ('Erlangen', 'Hamburg'), ('HBW Balingen-Weilstetten', 'Bergischer'), ('Leipzig', 'HSG Wetzlar')]

predictions = [('Madeira', 'Avanca'), ('Aguas Santas', 'ABC Braga'), ('Benfica', 'Sporting'), ('Porto', 'Gaia'),
               ('Sanjoanense', 'Boa Hora'), ('Xico Andebol', 'Vitoria'), ('Povoa', 'Belenenses'), ('SC Horta', 'Maia-Ismai')]

predictions = [('Gyongyosi', 'Balatonfuredi'), ('Komloi', 'Dabas'), ('Veszprem', 'Szeged')]

predictions = [('Plzen', 'Zubri'), ('Koprivnice', 'Jicin')]

predictions = [('Benidorm', 'BM Sinfin'), ('Morrazo Cangas', 'Barcelona'), ('Torrelavega', 'Nava'),
               ('Atl. Valladolid', 'La Rioja'), ('Anaitasuna', 'Antequera'), ('Huesca', 'Ademar'), ('Puente Genil', 'Cuenca')]

predictions = [('CSM Bucuresti', 'Minaur Baia Mare'), ('Timisoara', 'Bacau'), ('Suceava', 'Dobrogea Sud'),
               ('Cluj', 'Vaslui'), ('CSM Focsani', 'Alexandria')]

predictions = [('Hamburg', 'Lemgo'), ('Hannover-Burgdorf', 'Flensburg-H.')]

probs = {}
for f in files:
    rows = []
    teams = set()
    with open(os.path.join(foldername, f), encoding='utf-8') as g:
        reader = csv.reader(g, delimiter=';')
        for row in reader:
            if row[1] in ('Po karn.', 'Po dogr.'):
                try: rows.append([row[2], row[3], int(row[6])+int(row[8]), int(row[7])+int(row[9])])
                except: pass
                teams.add(row[2])
                teams.add(row[3])
            elif row[1] not in ('Walkower', 'Anulowane'):
                rows.append([row[1], row[2], int(row[3]), int(row[4])])
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
            home_interval = (h*(np.mean(scores_achieved[row[0]]) - std_coef*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) - std_coef*np.std(scores_lost[row[1]])),
                             h*(np.mean(scores_achieved[row[0]]) + std_coef*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) + std_coef*np.std(scores_lost[row[1]])))
            away_interval = (h*(np.mean(scores_achieved[row[1]]) - std_coef*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) - std_coef*np.std(scores_lost[row[0]])),
                             h*(np.mean(scores_achieved[row[1]]) + std_coef*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) + std_coef*np.std(scores_lost[row[0]])))
            match_interval = (h*(np.mean(scores_achieved[row[0]]) - std_coef2*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) - std_coef2*np.std(scores_lost[row[1]])) +
                             h*(np.mean(scores_achieved[row[1]]) - std_coef2*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) - std_coef2*np.std(scores_lost[row[0]])),
                             h*(np.mean(scores_achieved[row[0]]) + std_coef2*np.std(scores_achieved[row[0]])) +
                             a*(np.mean(scores_lost[row[1]]) + std_coef2*np.std(scores_lost[row[1]])) +
                             h*(np.mean(scores_achieved[row[1]]) + std_coef2*np.std(scores_achieved[row[1]])) +
                             a*(np.mean(scores_lost[row[0]]) + std_coef2*np.std(scores_lost[row[0]])))
            print(row, home_interval, away_interval, match_interval)

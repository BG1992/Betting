import csv
from numpy import mean, std
from collections import defaultdict
from scipy.stats import norm
import os

input_path = r'C:\Users\Marzena\PycharmProjects\DS\flashscore_handball'
capital = 1000

for file in os.listdir(input_path):

    df = []
    with open(os.path.join(input_path, file)) as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            row_data = {}
            row_data['Date'] = row[0]
            if row[1] == 'Po karn.':
                row_data['HomeTeam'] = row[2]
                row_data['AwayTeam'] = row[3]
                row_data['HomeGoals'] = float(row[4])
                row_data['AwayGoals'] = float(row[5])
            else:
                row_data['HomeTeam'] = row[1]
                row_data['AwayTeam'] = row[2]
                row_data['HomeGoals'] = float(row[3])
                row_data['AwayGoals'] = float(row[4])
            row_data['Lines'] = set()
            for i in range(5, len(row)):
                if '|' in row[i]:
                    cell = row[i].split('|')
                    if '.' in cell[0]:
                        if float(cell[0]):
                            row_data['Lines'].add(float(cell[0]))
                        if (float(cell[0]), 'O') in row_data:
                            row_data[(float(cell[0]), 'O')].append(float(cell[1]))
                        else:
                            row_data[(float(cell[0]), 'O')] = [float(cell[1])]
                        if (float(cell[0]), 'U') in row_data:
                            row_data[(float(cell[0]), 'U')].append(float(cell[2]))
                        else:
                            row_data[(float(cell[0]), 'U')] = [float(cell[2])]
            df.append(row_data.copy())

    df = list(reversed(df))

    ind_start = 60
    step = 7
    pos_ct = 0
    ct = 0

    for j in range(ind_start, len(df)-step, step):

        df_in = df[:j]
        df_out = df[j:j+step]

        goals_ct = defaultdict(list)
        params = defaultdict(tuple)

        for i in range(len(df_in)):
            goals_ct[(df_in[i]['HomeTeam'], 'A')].append(df_in[i]['HomeGoals'])
            goals_ct[(df_in[i]['HomeTeam'], 'D')].append(df_in[i]['AwayGoals'])
            goals_ct[(df_in[i]['AwayTeam'], 'A')].append(df_in[i]['AwayGoals'])
            goals_ct[(df_in[i]['AwayTeam'], 'D')].append(df_in[i]['HomeGoals'])

        for el in goals_ct:
            params[el] = (mean(goals_ct[el]), std(goals_ct[el]))

        for i in range(len(df_out)):
            curr_capital = capital
            lines = list(sorted(df_out[i]['Lines']))

            for line in lines:
                prob = norm.cdf(line, 0.5*params[(df_out[i]['HomeTeam'], 'A')][0] + 0.5*params[(df_out[i]['AwayTeam'], 'D')][0]+
                    0.5*params[(df_out[i]['AwayTeam'], 'A')][0] + 0.5*params[(df_out[i]['HomeTeam'], 'D')][0],
                    pow(0.5*params[(df_out[i]['AwayTeam'], 'A')][1]**2 + 0.5*params[(df_out[i]['HomeTeam'], 'D')][1]**2
                    + 0.5*params[(df_out[i]['AwayTeam'], 'A')][1]**2 + 0.5*params[(df_out[i]['HomeTeam'], 'D')][1]**2, 0.5))

                if prob*mean(df_out[i][(line, 'U')]) > 1.2:
                    prob = 1.05 /mean(df_out[i][(line, 'U')])
                    f = prob - (1 - prob) / (mean(df_out[i][(line, 'U')]) - 1)
                    f = 0.01
                    bet = f*curr_capital*1
                    if df_out[i]['HomeGoals'] + df_out[i]['AwayGoals'] < line:
                        capital += bet * (mean(df_out[i][(line, 'U')]) - 1)
                        win = True
                        pos_ct += 1
                    else:
                        capital -= bet
                        win = False
                    ct += 1

                if (1-prob)*mean(df_out[i][(line, 'O')]) > 1.2:
                    p = 1.05 / mean(df_out[i][(line, 'O')])
                    f = p - (1-p) / (mean(df_out[i][(line, 'O')]) - 1)
                    f = 0.01
                    bet = f*curr_capital*1
                    if df_out[i]['HomeGoals'] + df_out[i]['AwayGoals'] > line:
                        capital += bet * (mean(df_out[i][(line, 'O')]) - 1)
                        win = True
                        pos_ct += 1
                    else:
                        capital -= bet
                        win = False
                    ct += 1

    print(file, pos_ct, ct, pos_ct/ct, capital)
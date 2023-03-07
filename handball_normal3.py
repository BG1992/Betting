import pandas as pd
from numpy import mean, std
from collections import defaultdict
from scipy.stats import norm

df = pd.read_csv(r'C:\Users\Marzena\PycharmProjects\DS\pgnig_test.csv', encoding='latin1', delimiter=';')
df = df[['HomeTeam','AwayTeam','FTHG','FTAG']]
df = df.rename(columns={'FTHG': 'HomeGoals', 'FTAG': 'AwayGoals'})

df.reset_index(inplace=True)

pos_ct, ct = 0, 0

goals_ct = defaultdict(list)
params = defaultdict(tuple)

df_in = df.iloc[:df.shape[0]-9]
df_out = df.iloc[df.shape[0]-9:]

df_in.reset_index(inplace=True)
df_out.reset_index(inplace=True)

for i in range(df_in.shape[0]):
    goals_ct[(df.iloc[i]['HomeTeam'], 'A')].append(df.iloc[i]['HomeGoals'])
    goals_ct[(df.iloc[i]['HomeTeam'], 'D')].append(df.iloc[i]['AwayGoals'])
    goals_ct[(df.iloc[i]['AwayTeam'], 'A')].append(df.iloc[i]['AwayGoals'])
    goals_ct[(df.iloc[i]['AwayTeam'], 'D')].append(df.iloc[i]['HomeGoals'])

for el in goals_ct:
    params[el] = (mean(goals_ct[el]), std(goals_ct[el]))

for i in range(df_out.shape[0]):
    print(df_out.iloc[i]['HomeTeam'], df_out.iloc[i]['AwayTeam'],
          df_out.iloc[i]['HomeGoals'], df_out.iloc[i]['AwayGoals'])

    for j in range(45, 70):
        prob = norm.cdf(j+0.5, 0.5*params[(df_out.iloc[i]['HomeTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['AwayTeam'], 'D')][0]+
                        0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][0],
                        pow(0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][1]**2 + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][1]**2
                        + 0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][1]**2 + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][1]**2, 0.5))
        print(j+0.5, 1-prob, prob)
    # print(0.5*params[(df_out.iloc[i]['HomeTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['AwayTeam'], 'D')][0] -
    #       0.5*params[(df_out.iloc[i]['HomeTeam'], 'A')][1] - 0.5*params[(df_out.iloc[i]['AwayTeam'], 'D')][1],
    #       0.5*params[(df_out.iloc[i]['HomeTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['AwayTeam'], 'D')][0] +
    #       0.5*params[(df_out.iloc[i]['HomeTeam'], 'A')][1] + 0.5*params[(df_out.iloc[i]['AwayTeam'], 'D')][1])
    # print(0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][0] -
    #       0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][1] - 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][1],
    #       0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][0] + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][0] +
    #       0.5*params[(df_out.iloc[i]['AwayTeam'], 'A')][1] + 0.5*params[(df_out.iloc[i]['HomeTeam'], 'D')][1])
    print('*****************************************')
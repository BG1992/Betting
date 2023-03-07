import pandas as pd
from sklearn.linear_model import LogisticRegression
import scipy.optimize as sc
from random import uniform

file_path = r'C:\Users\Marzena\PycharmProjects\DS\flashscore_gap_seasons\pko-bp-ekstraklasa-2020-2021.csv'
df = pd.read_csv(file_path)
df = df.fillna(0)
df['Gospodarze Posiadanie piłki'] = df['Gospodarze Posiadanie piłki'].str.rstrip('%').astype('float')/100.0
df.drop(columns = ['Unnamed: 0'], inplace = True)
df = df.iloc[::-1]
df.reset_index(inplace = True, drop = True)

df['y'] = df.apply(lambda row: 0 if row['Gospodarze Gole'] + row['Goście Gole'] < 2.5 else 1, axis = 1)

#train, test = df.iloc[0:int(df.shape[0]*0.8)], df.iloc[int(df.shape[0]*0.8):]
teams_set = set(df['Gospodarze']).union(set(df['Goście']))

x_cols = []
cols_to_remove = {'Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole', 'Goście Posiadanie piłki', 'y'}

for col in df.columns:
    if col not in cols_to_remove:
        if df[col].min() == df[col].max() and df[col].max() == 0:
            pass
        else:
            x_cols.append(col)

teams = {}
pred_cols = set()
for col in x_cols:
    if 'Gospodarze ' in col:
        c = col.replace('Gospodarze ', '')
        pred_cols.add(c)

inds = {}
i = 0
for t in teams_set:
    #teams[t + ' Dom'] = 0
    #inds[t + ' Dom'] = i
    #i += 1
    for col in ['Sytuacje bramkowe']: #pred_cols:
        teams[t + ' A ' + col] = 0
        inds[t + ' A ' + col] = i
        i += 1
        teams[t + ' D ' + col] = 0
        inds[t + ' D ' + col] = i
        i += 1

def f(x, train):
    sm = 0
    for i in range(train.shape[0]):
        home_team = train.iloc[i].loc['Gospodarze']
        away_team = train.iloc[i].loc['Goście']
        for col in ['Sytuacje bramkowe']: #pred_cols.difference({'Posiadanie piłki'}):
            sm += (x[inds[home_team + ' A ' + col]] -
             x[inds[away_team + ' D ' + col]] -
                   train.iloc[i].loc['Gospodarze ' + col])**2
            sm += (x[inds[away_team + ' A ' + col]] -
                   x[inds[home_team + ' D ' + col]] -
                   train.iloc[i].loc['Goście ' + col])**2
        # frac_home = x[inds[home_team + ' A Posiadanie piłki']]/(x[inds[home_team + ' A Posiadanie piłki']] +
        #        x[inds[away_team + ' D Posiadanie piłki']])
        # sm += (frac_home - train.iloc[i].loc['Gospodarze Posiadanie piłki'])**2
        # frac_away = x[inds[away_team + ' A Posiadanie piłki']] / (x[inds[away_team + ' A Posiadanie piłki']] +
        #             x[inds[home_team + ' D Posiadanie piłki']])
        # sm += (frac_away - (1-train.iloc[i].loc['Gospodarze Posiadanie piłki']))**2
    print(sm)
    return sm

bnds = [(None, None) for _ in range(len(inds))]
# for it in list(inds.items()):
#     if 'Dom' in it[0]:
#         bnds[it[1]] = (0,1)

positive_ct, main_ct = 0, 0
start_ind = len(teams_set)*4//2-1
for i in range(start_ind, df.shape[0]-len(teams_set)//2, len(teams_set)//2):
    train = df.iloc[:i]
    test = df.iloc[i:i+len(teams_set)//2]
    print('hehe')
    res = sc.minimize(f, x0=[uniform(-10,10) for _ in range(len(inds))], method='Nelder-Mead',
                      tol=pow(10, -8), options={'maxiter': 2000000}, args=train)
    for it in list(inds.items()):
        teams[inds[it[0]]] = res.x[it[1]]

    cols_to_remove = {'Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole', 'Goście Posiadanie piłki', 'y'}
    for col in df.columns:
        if col not in cols_to_remove:
            if df[col].min() == df[col].max() and df[col].max() == 0:
                pass
            else:
                x_cols.append(col)

    train_X = train[x_cols]
    train_y = train['y']
    test_X = test[x_cols]
    test_y = test['y']

    data = {}
    for col in x_cols:
        data[col] = []
    for j in range(len(test.shape[0])):
        home_team, away_team = test.iloc[j].loc['Gospodarze'], test.iloc[j].loc['Goście']
        for g in ('Gospodarze', 'Goście'):
            for col in x_cols:
                if col != 'Posiadanie piłki':
                    data[col].append(teams[home_team + ' A ' + col] -
                                     teams[away_team + ' D ' + col])
                    data[col].append(teams[away_team + ' A ' + col] -
                                     teams[home_team + ' D ' + col])
                else:
                    h = teams[home_team + ' A Posiadanie piłki']
                    a = teams[away_team + ' D Posiadanie piłki']
                    data[col].append(h/(h+a))
    test_pred = pd.DataFrame(data)
    test_pred = test_pred[[x_cols]]

    for col in train_X.columns:
        m, s = train_X[col].mean(), train_X[col].std()
        train_X[col] = train_X[col].apply(lambda row: (row - m) / s)
        test_X[col] = test_X[col].apply(lambda row: (row - m) / s)
        test_pred[col] = test_pred[col].apply(lambda row: (row - m) / s)

    logit_model = LogisticRegression()
    result = logit_model.fit(train_X, train_y)
    score = logit_model.predict(train_X)
    pred_y = logit_model.predict(train_X)
    res = pd.DataFrame(train_y)
    res['pred'] = pred_y
    res['check'] = res.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)
    print(res['check'].sum() / res.shape[0])
    print(result.score(train_X, train_y))

    pred_y_test = logit_model.predict(test_pred)
    res_test = pd.DataFrame(test_y)
    res_test['pred'] = pred_y_test
    res_test['check'] = res_test.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)
    res_test['pred_proba'] = result.predict_proba(test_X)[:, 1]
    print(res_test['check'].sum() / res_test.shape[0])

    #pozmieniac x0 w zaleznosci od wartości kolumn
    #dodac wspolczynnik czasu do optimizera?


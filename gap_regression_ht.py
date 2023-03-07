import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

file_path = r'C:\Users\Marzena\PycharmProjects\DS\flashscore_gap_seasons\pko-bp-ekstraklasa-2017-2018_HT.csv'
df = pd.read_csv(file_path)
df = df.fillna(0)
df = df[df['Gospodarze Posiadanie piłki'] != 0]

df['Gospodarze Posiadanie piłki'] = df['Gospodarze Posiadanie piłki'].str.rstrip('%').astype('float')/100.0
df.drop(columns = ['Unnamed: 0'], inplace = True)
df = df.iloc[::-1]
df.reset_index(inplace = True, drop = True)

df['Gospodarze HT'] = df['HT'].str[1].astype(int)
df['Goście HT'] = df['HT'].str[-2].astype(int)

df['y'] = df.apply(lambda row: 0 if row['Gospodarze Gole'] - row['Gospodarze HT'] < 0.5 else 1, axis = 1)

# train, test = df.iloc[0:int(df.shape[0]*0.8)], df.iloc[int(df.shape[0]*0.8):]
teams_set = set(df['Gospodarze']).union(set(df['Goście']))

for t in teams_set:
    df[t] = 0

for t in teams_set:
    df[t] = df.apply(lambda row: 1 if row['Gospodarze'] == t else 0, axis = 1)
    df[t] = df.apply(lambda row: -1 if row['Goście'] == t else 0, axis=1)

x_cols = []
cols_to_remove = {'Data', 'Gospodarze', 'Goście', 'Gospodarze Gole', 'Goście Gole',
                  'Goście Posiadanie piłki', 'HT', 'y'}

for col in df.columns:
    if col not in cols_to_remove:
        if df[col].min() == df[col].max() and df[col].max() == 0:
            pass
        else:
            x_cols.append(col)

positive_cts, cts = [], []
positive_train_cts, train_cts = [], []
ct0, ct1 = 0, 0
for i in range(5*len(teams_set)//2, df.shape[0], len(teams_set)//2):

    train_X = df.iloc[:i][x_cols]
    train_y = df.iloc[:i]['y']
    test_X = df.iloc[i:i+len(teams_set)//2][x_cols]
    test_y = df.iloc[i:i+len(teams_set)//2]['y']

    for col in train_X.columns:
        if col not in teams_set:
            m, s = train_X[col].mean(), train_X[col].std()
            if abs(s) > 0.001:
                train_X[col] = train_X[col].apply(lambda row: (row - m)/s)
                test_X[col] = test_X[col].apply(lambda row: (row - m)/s)

    logit_model = LogisticRegression(class_weight='balanced')
    result = logit_model.fit(train_X, train_y)
    score = logit_model.predict(train_X)
    pred_y = logit_model.predict(train_X)
    res = pd.DataFrame(train_y)
    res['pred'] = pred_y
    res['check'] = res.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)

    pred_y_test = logit_model.predict(test_X)
    res_test = pd.DataFrame(test_y)
    res_test['pred'] = pred_y_test
    res_test['check'] = res_test.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)
    res_test['pred_proba'] = result.predict_proba(test_X)[:,1]
    print(i, res['check'].sum()/res.shape[0], res_test['check'].sum()/res_test.shape[0],
          res_test['pred'].sum()/res_test.shape[0])
    positive_cts.append(res_test['check'].sum())
    cts.append(res_test.shape[0])
    positive_train_cts.append(res['check'].sum())
    train_cts.append(res.shape[0])
    ct0 += res_test[(res_test['check'] == 1) & (res_test['y'] == 0)].shape[0]
    ct1 += res_test[(res_test['check'] == 1) & (res_test['y'] == 1)].shape[0]

print(positive_cts)
print(cts)

print(df['y'].sum()/df.shape[0])
print(sum(positive_train_cts)/sum(train_cts))
print(sum(positive_cts), sum(cts), sum(positive_cts)/sum(cts), sum(cts)/sum(positive_cts))
print(ct0, ct1)
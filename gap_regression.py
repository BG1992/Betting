import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

file_path = r'C:\Users\Marzena\PycharmProjects\DS\flashscore_gap_seasons\pko-bp-ekstraklasa-2020-2021.csv'
df = pd.read_csv(file_path)
df = df.fillna(0)
df['Gospodarze Posiadanie piłki'] = df['Gospodarze Posiadanie piłki'].str.rstrip('%').astype('float')/100.0
df.drop(columns = ['Unnamed: 0'], inplace = True)
df = df.iloc[::-1]
df.reset_index(inplace = True, drop = True)

df['y'] = df.apply(lambda row: 0 if row['Gospodarze Gole'] + row['Goście Gole'] < 2.5 else 1, axis = 1)

train, test = df.iloc[0:int(df.shape[0]*0.8)], df.iloc[int(df.shape[0]*0.8):]
teams_set = set(df['Gospodarze']).union(set(df['Goście']))

x_cols = []
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

for col in train_X.columns:
    m, s = train_X[col].mean(), train_X[col].std()
    train_X[col] = train_X[col].apply(lambda row: (row - m)/s)
    test_X[col] = test_X[col].apply(lambda row: (row - m)/s)

logit_model = LogisticRegression()
result = logit_model.fit(train_X, train_y)
score = logit_model.predict(train_X)
pred_y = logit_model.predict(train_X)
res = pd.DataFrame(train_y)
res['pred'] = pred_y
res['check'] = res.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)
print(res['check'].sum()/res.shape[0])
print(result.score(train_X, train_y))

pred_y_test = logit_model.predict(test_X)
res_test = pd.DataFrame(test_y)
res_test['pred'] = pred_y_test
res_test['check'] = res_test.apply(lambda row: 1 if row['y'] == row['pred'] else 0, axis=1)
res_test['pred_proba'] = result.predict_proba(test_X)[:,1]
print(result.coef_)
print(res_test['check'].sum()/res_test.shape[0])
print(result.score(test_X, test_y))

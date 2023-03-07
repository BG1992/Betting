import csv
import numpy as np
import statsmodels.api as sm
import pandas as pd

def compare(predicted, score):
    if predicted < 0.5 and score == 0: return 'TN'
    elif predicted >= 0.5 and score == 1: return 'TP'
    elif predicted >= 0.5 and score == 0: return 'FP'
    else: return 'FN'

def get_score(score):
    left = int(score[:score.index('--')])
    right = int(score[score.index('--')+2:])
    if left > right:
        return 1
    else:
        return 0

def format_row(row):
    _row = []
    for el in row:
        if el == '':
            _row.append(0)
        else:
            _row.append(float(el))
    return _row

data = []
data_unknown = []
with open('C://Users//Marzena//Documents//fortuna 30102020.csv', newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    header = next(reader)
    for row in reader:
        data.append(format_row(row[:-1]) + [get_score(row[-1])])

#print(data)
print(len(header))
data = pd.DataFrame(data, columns=header)
data = sm.add_constant(data)
#data = data.sample(frac=1)
samples_ct = 230
#to_drop = ['4.5 -']
#data = data[['0.5 -', '1.5 -', '2.5 -', '3.5 -', '4.5 -', 'const', 'score']]
#print(data)
# with open('C://Users//Marzena//Documents//fortuna 30102020 unknown.csv', newline='') as datafile:
#     reader = csv.reader(datafile, delimiter=';')
#     header = next(reader)
#     for row in reader:
#         data_unknown.append(format_row(row))

X_train = data.iloc[:samples_ct, :-1]
X_test = data.iloc[samples_ct:, :-1]
y_train = data.iloc[:samples_ct, -1]
y_test = data.iloc[samples_ct:, -1]
results = sm.Logit(y_train, X_train).fit()
print(results.summary())

summ_train = pd.concat([results.predict(X_train), y_train], axis=1)
summ_train.columns = ['predicted', 'score']
check_train = pd.DataFrame(summ_train.apply(lambda row: compare(row['predicted'], row['score']), axis=1))
check_train.columns = ['result']
#print(check_train)
print('TP:', check_train[check_train['result']=='TP'].count())
print('TN:', check_train[check_train['result']=='TN'].count())
print('FP:', check_train[check_train['result']=='FP'].count())
print('FN:', check_train[check_train['result']=='FN'].count())

summ_test = pd.concat([results.predict(X_test), y_test], axis=1)
check_test = pd.DataFrame(summ_test.apply(lambda row: compare(row['predicted'], row['score']), axis=1))
check_test.columns = ['result']
print('*********************************')
print('TP:', check_test[check_test['result']=='TP'].count())
print('TN:', check_test[check_test['result']=='TN'].count())
print('FP:', check_test[check_test['result']=='FP'].count())
print('FN:', check_test[check_test['result']=='FN'].count())

# data_unknown = pd.DataFrame(data_unknown, columns=header)
# data_unknown = sm.add_constant(data_unknown)
# data_unknown = data_unknown[['0.5 -', '1.5 -', '2.5 -', '3.5 -', '4.5 -', 'const']]
# #print(data_unknown)
# print(results.predict(data_unknown))
print(X_test)
print(results.predict(X_test))
print(check_test)
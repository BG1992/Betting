import csv
import statsmodels.api as sm
import statsmodels.stats.proportion as sm2
import numpy as np
import fortuna_helper as fh
import pandas as pd

def compare(predicted, score):
    if predicted < 0.5 and score == 0: return 'TN'
    elif predicted >= 0.5 and score == 1: return 'TP'
    elif predicted >= 0.5 and score == 0: return 'FP'
    else: return 'FN'

data = []
data_path = 'C://Users//Marzena//PycharmProjects//DS//flashscore_ous.csv'
with open(data_path, newline='') as datafile:
    reader = csv.reader(datafile, delimiter=';')
    for row in reader:
        if row[2] == 'o':
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
        else:
            data.append([float(row[0]), fh.calc_equilibrium(float(row[0]), float(row[1])), 0])
            data.append([float(row[1]), fh.calc_equilibrium(float(row[0]), float(row[1])), 1])

rate_interval = [1.3, 2]
eq_interval = [-0.11, -0.05]
data2 = []
for row in data:
    if row[0] > rate_interval[0] and row[0] < rate_interval[1] \
        and row[1] > eq_interval[0] and row[1] < eq_interval[1]:
            data2.append(row)

data = np.array(data2)
m0, d0 = np.mean(data[:,0]), np.std(data[:,0])
m1, d1 = np.mean(data[:,1]), np.std(data[:,1])

for k in range(data.shape[0]):
    data[k,0] -= m0
    data[k,0] /= d0
    data[k,1] -= m1
    data[k,1] /= d1

data = pd.DataFrame(data)
data = sm.add_constant(data)

X_train = data.iloc[:,:-1]
y_train = data.iloc[:,-1]

results = sm.Logit(y_train, X_train).fit()
print(results.summary())

summ_test = pd.concat([results.predict(X_train), y_train], axis=1)
summ_test.columns = ['predicted', 'score']
check_test = pd.DataFrame(summ_test.apply(lambda row: compare(row['predicted'], row['score']), axis=1))
check_test.columns = ['result']
print('*********************************')
print('TP:', check_test[check_test['result']=='TP'].count())
print('TN:', check_test[check_test['result']=='TN'].count())
print('FP:', check_test[check_test['result']=='FP'].count())
print('FN:', check_test[check_test['result']=='FN'].count())

print(sm2.proportion_confint(check_test[check_test['result']=='TP'].count()+
                             check_test[check_test['result']=='TN'].count(),len(data2)))
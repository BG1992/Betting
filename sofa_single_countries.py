from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text, export_graphviz
import pandas as pd
from sklearn.model_selection import KFold
import os
import statsmodels.stats.proportion as sm
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz 2.44.1/bin'

def add_score(row):
    if row['Home Score'] > row['Away Score']:
        return '1'
    elif row['Home Score'] == row['Away Score']:
        return '0'
    else:
        return '2'

def calc_y(row):
    if max(row['predict 1'], row['predict 0'], row['predict 2']) > 0.5:
        if row['y'] != row['y_pred']:
            return abs(row['predict ' + str(row['y_pred'])])
        return 0
    return 0

def avg(row, num, k):
    return sum(row['predict ' + str(num) + '_temp'])/k

clf = DecisionTreeClassifier(random_state=0, class_weight='balanced')
data2 = pd.read_csv('sofascore_test_data_Germany.csv', encoding = "ISO-8859-1", delimiter=';')

# regions = []
# for region in data2['Region'].unique():
#     #print(region, data2[data2['Region'] == region].shape[0])
#     regions.append((region, data2[data2['Region'] == region].shape[0]))
#
# regions.sort(key= lambda x: -x[1])
# for el in regions:
#     print(el)

#data2 = data2[data2.Region.isin(list(map(lambda x: x[0], regions[:20])))]
#data2 = pd.get_dummies(data2, columns=['Region'])
data2['y'] = data2.apply(lambda row: add_score(row), axis = 1)
data = data2.drop(columns=['date', 'x', 'Home', 'Away', 'Region', 'Home Score', 'Away Score'])
print(pd.DataFrame.head(data))

data = data.sample(frac=1)
data = data.reset_index()
data = data[data.apply(lambda x: x['1'] + x['0'] + x['2'] > 1000, axis=1)]
X, y = data.drop(columns=['y', 'index']), data['y']

# X_new = pd.read_csv('new_data.csv',encoding = "ISO-8859-1", delimiter=';')
# X_new = X_new.drop(columns=['Home', 'Away'])
#results_new = X_new
k = 5
for i in range(3, 20):
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    kf = KFold(n_splits=k)
    positive, ct = 0, 0
    ind = 0
    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        clf = DecisionTreeClassifier(max_depth=i)
        clf = clf.fit(X_train, y_train)
        y_pred = pd.DataFrame(clf.predict(X_test), columns=['y_pred'])
        y_pred_proba = pd.DataFrame(clf.predict_proba(X_test), columns=['predict 0', 'predict 1', 'predict 2'])
        y_pred_proba = y_pred_proba.reindex(columns = ['predict 1', 'predict 0', 'predict 2'])
        y_test_new = y_test.reset_index()
        result = pd.concat([y_test_new['y'], y_pred, y_pred_proba], axis=1)
        result['check1'] = result.apply(lambda row: 1 if row['y'] == row['y_pred'] and
                                        max(row['predict 1'], row['predict 0'], row['predict 2']) > 0.47
                                                         and max(row['predict 1'], row['predict 0'], row['predict 2']) < 0.75
        else 0, axis = 1)
        result['check2'] = result.apply(lambda row: 1 if max(row['predict 1'],
                                                             row['predict 0'], row['predict 2']) > 0.47
                                                         and max(row['predict 1'], row['predict 0'], row['predict 2']) < 0.75
        else 0, axis=1)
        #print(pd.DataFrame.head(result, n=50))
        # result['check'] = result.apply(lambda row: calc_y(row), axis=1)
        positive += sum(result['check1'])
        ct += sum(result['check2'])
        # y_new_pred = pd.DataFrame(clf.predict_proba(X_new), columns=['predict 0_temp', 'predict 1_temp', 'predict 2_temp'])
        # y_new_pred = y_new_pred.reindex(columns=['predict 1_temp', 'predict 0_temp', 'predict 2_temp'])
        # results_new = pd.concat([results_new, y_new_pred], axis=1)
        ind += 1

        #res += sum(result['check'])
        #ct += result.shape[0]
    print(i, positive//k, ct//k, sm.proportion_confint(positive//k, ct//k, alpha=0.01))
    # results_new['predict 1'] = results_new.apply(lambda row: avg(row, 1, k), axis=1)
    # results_new['predict 0'] = results_new.apply(lambda row: avg(row, 0, k), axis=1)
    # results_new['predict 2'] = results_new.apply(lambda row: avg(row, 2, k), axis=1)
    #print(i, res/k)

#results_new.to_csv('results_new.csv', sep=';')


# pred = pd.DataFrame(clf.predict_proba(X_test))
# p = pd.concat([data2, y_test], axis=1, join='inner')
# p = p.reset_index()
# result2 = pd.concat([p, pred], axis=1)
# print(clf.classes_)
# print(pd.DataFrame.head(result2, n=100))
# print(sm.proportion_confint(sum(result['check']), result.shape[0], alpha=0.01))
# result2.to_csv('result2_df.csv', sep=';')
# graph_tree = export_graphviz(clf, out_file='graph_tree.dot')
# print('hehe')
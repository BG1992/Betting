import csv
from collections import defaultdict
from random import uniform
import scipy.optimize as sc
from math import exp, factorial

variables = {}
ind_variables = {}
teams = set()
filename = 'premierleague_scores.csv'
with open(filename, newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        teams.add(row[0])

for team in teams:
    variables[(team, 'A')] = [0, 0]
    variables[(team, 'D')] = [0, 0]

def find_prob(team_a, team_d, k):
    return (pow(variables[(team_a, 'A')], k)*exp(-variables[(team_a, 'A')])+
            pow(variables[(team_d, 'D')], k)*exp(-variables[(team_d, 'D')]))/(2*factorial(k))
    # sm = 0
    # for i in range(2*k+1):
    #     sm += pow(variables[(team_a, 'A')], i)*exp(-variables[(team_a, 'A')])*\
    #           pow(variables[(team_d, 'D')], 2*k-i)*exp(-variables[(team_d, 'D')])\
    #           /(factorial(i)*factorial(2*k-i))
    # return sm

with open(filename, newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        variables[(row[0], 'A')][0] += int(row[2])
        variables[(row[0], 'A')][1] += 1
        variables[(row[1], 'D')][0] += int(row[2])
        variables[(row[1], 'D')][1] += 1
        variables[(row[1], 'A')][0] += int(row[3])
        variables[(row[1], 'A')][1] += 1
        variables[(row[0], 'D')][0] += int(row[3])
        variables[(row[0], 'D')][1] += 1

for v in variables:
    print(v, variables[v], variables[v][0]/variables[v][1])
    variables[v] = variables[v][0]/variables[v][1]


# matches = [('Leicester City', 'Everton', '2-1'),
#            ('Manchester United', 'Aston Villa', '2-2'),
#            ('Norwich City', 'Arsenal Londyn', '2-2'),
#            ('Wolverhampton', 'Sheffield United', '1-1'),
#            ('Southampton FC', 'Watford FC', '2-1'),
#            ('Burnley FC', 'Crystal Palace', '0-2'),
#            ('Chelsea Londyn', 'West Ham United', '0-1'),
#            ('Liverpool FC', 'Brighton & Hove', '2-1'),
#            ('Tottenham Hotspur', 'AFC Bournemouth', '3-2'),
#            ('Newcastle United', 'Manchester City', '2-2')]
print(teams)
# matches = [('PSG', 'Lyon', '0-1'),
#            ('Lille', 'Bordeaux', '2-1'),
#            ('Brest', 'Reims', '2-1'),
#            ('Lorient', 'Nimes', '3-0'),
#            ('Nantes', 'Dijon', '1-1'),
#            ('Strasbourg', 'Metz', '2-2'),
#            ('Nice', 'Rennes', '0-1'),
#            ('Lens', 'Montpellier', '2-3'),
#            ('Marsylia', 'Monaco', '2-1'),
#            ('St. Etienne', 'Angers', '0-0')]

# matches = [('Lechia', 'Wisła Płock', '0-1'),
#            ('Raków', 'Jagiellonia', '3-2'),
#            ('Stal', 'Lech', '1-1'),
#             ('Wisła Kraków', 'Legia', '1-2'),
#             ('Górnik', 'Cracovia', '0-2'),
#             ('Warta', 'Pogoń', '1-2'),
#             ('Zagłębie', 'Śląsk', '2-1'),
#             ('Podbeskidzie', 'Piast', '0-5')]

# matches = [('Schalke', 'Freiburg', '0-2'),
#            ('Bremen', 'Dortmund', '1-2'),
#            ('Hertha', 'Mainz', '0-0'),
#             ('Stuttgart', 'Union Berlin', '2-2'),
#             ('Frankfurt', 'Moenchengladbach', '3-3'),
#            ('Bayern', 'Wolfsburg'), ('Bielefeld', 'Augsburg'), ('FC Koeln', 'Leverkusen'), ('Hoffenheim', 'RB Lipsk')]

# matches = [('RB Salzburg', 'LASK Linz', '3-1'),
#            ('SK Rapid Wiedeń', 'Swarovski Tirol', '0-3'),
#            ('Wolfsberger AC', 'FK Austria Wiedeń', '3-2'),
#            ('SV Ried', 'SC Rheindorf Altach', '1-4'),
#            ('SKN Sankt Pölten', 'Hartberg', '2-2'),
#            ('SK Sturm Graz', 'Admira', '3-0')]
#
# matches = [('Celtic Glasgow FC', 'Kilmarnock FC', '2-0'),
#            ('Dundee United FC', 'Glasgow Rangers FC', '1-2'),
#            ('Saint Johnstone FC', 'Livingston FC', '1-2'),
#            ('Motherwell FC', 'Saint Mirren FC', '0-1'),
#            ('Hamilton Academicals FC',	'Hibernian FC', '0-4'),
#            ('Aberdeen FC', 'Ross County', '2-0')]


matches = []
with open('premierleague_scores.csv', newline='') as csvfile:
    _reader = csv.reader(csvfile, delimiter=';')
    next(_reader)
    for row in _reader:
        matches.append([(row[0], row[1], int(row[2]), int(row[3]))])

counts_102 = [0, 0, 0]
counts_numgoals = [0,0,0,0,0]
counts_intervals = [0,0,0,0]
counts_singles = [0,0,0,0]
counts_exacts = [0,0,0,0,0,0,0,0]

counts_12 = [0,0,0,0]
for m in matches:
    scores = []
    scores_numgoals = defaultdict(float)
    scores_102 = defaultdict(float)
    scores_intervals = defaultdict(float)
    scores_teams = defaultdict(int)
    scores_1 = defaultdict(float)
    scores_2 = defaultdict(float)
    scores_12 = defaultdict(float)
    for i in range(15):
        for j in range(15):
            p = find_prob(m[0][0], m[0][1], i)*find_prob(m[0][1], m[0][0], j)
            if i != j:
                scores_12[12] += p
            else:
                scores_12[0] += p
    t = 0.745
    if scores_12[12] >= t and m[0][2] != m[0][3]:
        counts_12[0] += 1
    elif scores_12[12] < t and m[0][2] != m[0][3]:
        counts_12[1] += 1
    elif scores_12[12] < t and m[0][2] == m[0][3]:
        counts_12[2] += 1
    else:
        counts_12[3] += 1
            # scores.append(((i, j), p))
            # scores_numgoals[(i+j)] += p
            # if i+j == 0: scores_intervals['0'] += p
            # elif i+j == 1: scores_intervals['1'] += p
            # elif i+j == 2: scores_intervals['2'] += p
            # else: scores_intervals['3+'] += p
            # if i > j: scores_102[1] += p
            # elif i == j: scores_102[0] += p
            # else: scores_102[2] += p
            # if i == 0: scores_1['0'] += p
            # elif i == 1: scores_1['1'] += p
            # elif i == 2: scores_1['2'] += p
            # else: scores_1['3+'] += p
            # if j == 0: scores_2['0'] += p
            # elif j == 1: scores_2['1'] += p
            # elif j == 2: scores_2['2'] += p
            # else: scores_2['3+'] += p
    # _scores_102 = [scores_102[1], scores_102[0], scores_102[2]]
    # _scores_102.sort(reverse=True)
    # _scores_numgoals = [scores_numgoals[0], scores_numgoals[1], scores_numgoals[2],
    #                     scores_numgoals[3], scores_numgoals[4], scores_numgoals[5],
    #                     scores_numgoals[6], scores_numgoals[7]]
    # _scores_numgoals.sort(reverse=True)
    # _scores_intervals = [scores_intervals['0'], scores_intervals['1'], scores_intervals['2'], scores_intervals['3+']]
    # _scores_intervals.sort(reverse=True)
    # _scores_1 = [scores_1['0'], scores_1['1'], scores_1['2'], scores_1['3+']]
    # _scores_2 = [scores_2['0'], scores_2['1'], scores_2['2'], scores_2['3+']]
    # _scores_1.sort(reverse=True)
    # _scores_2.sort(reverse=True)
    # if max(_scores_102) > 0.37 and max(_scores_102) < 0.9:
    #     if int(m[0][2]) > int(m[0][3]):
    #        counts_102[_scores_102.index(scores_102[1])] += 1
    #     elif int(m[0][2]) == int(m[0][3]):
    #        counts_102[_scores_102.index(scores_102[0])] += 1
    #     else:
    #        counts_102[_scores_102.index(scores_102[2])] += 1
    # try:
    #     counts_numgoals[_scores_numgoals.index(scores_numgoals[int(m[0][2]) + int(m[0][3])])] += 1
    # except: pass
    # if int(m[0][2]) + int(m[0][3]) == 0:
    #     counts_intervals[_scores_intervals.index(scores_intervals['0'])] += 1
    # elif int(m[0][2]) + int(m[0][3]) == 1:
    #     counts_intervals[_scores_intervals.index(scores_intervals['1'])] += 1
    # elif int(m[0][2]) + int(m[0][3]) == 2:
    #     counts_intervals[_scores_intervals.index(scores_intervals['2'])] += 1
    # else:
    #     counts_intervals[_scores_intervals.index(scores_intervals['3+'])] += 1
    # if int(m[0][2]) == 0:
    #     counts_singles[_scores_1.index(scores_1['0'])] += 1
    # if int(m[0][2]) == 1:
    #     counts_singles[_scores_1.index(scores_1['1'])] += 1
    # if int(m[0][2]) == 2:
    #     counts_singles[_scores_1.index(scores_1['2'])] += 1
    # if int(m[0][2]) >= 3:
    #     counts_singles[_scores_1.index(scores_1['3+'])] += 1
    # if int(m[0][3]) == 0:
    #     counts_singles[_scores_2.index(scores_2['0'])] += 1
    # if int(m[0][3]) == 1:
    #     counts_singles[_scores_2.index(scores_2['1'])] += 1
    # if int(m[0][3]) == 2:
    #     counts_singles[_scores_2.index(scores_2['2'])] += 1
    # if int(m[0][3]) >= 3:
    #     counts_singles[_scores_2.index(scores_2['3+'])] += 1
    # scores.sort(key= lambda x: -x[1])
    # for i in range(8):
    #     if scores[i][0] == (int(m[0][2]), int(m[0][3])):
    #         counts_exacts[i] += 1
    #         break


    # scores.sort(key= lambda x: -x[1])
    # print(m)
    # print('match score:')
    # #print(sum(map(lambda x: x[1], scores)))
    # for s in scores[:7]:
    #     print(s)
    # print('sum of goals:')
    # for i in range(7):
    #     print(i, scores_uo[i])
    # print('p1: ' + str(scores_102[1]) + ', p0: ' + str(scores_102[0]) + ', p2: ' + str(scores_102[2]))
    # print('********************')

# print(counts_102)
# print(counts_numgoals)
# print(counts_intervals)
# print(counts_singles)
# print(counts_exacts)

print(counts_12)
import statsmodels.stats.proportion as sm
print(counts_12[0]/(counts_12[0]+counts_12[3]))
print(sm.proportion_confint(counts_12[0], counts_12[0]+counts_12[3]))
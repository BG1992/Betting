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


# matches = [('Aston Villa', 'Burnley', '0-0'),
#            ('Fulham', 'Brighton', '0-0'),
#            ('Liverpool', 'Tottenham', '2-1'),
#            ('West Ham', 'Crystal Palace', '1-1'),
#            ('Arsenal', 'Southampton', '1-1'),
#            ('Leeds', 'Newcastle', '5-2'),
#            ('Leicester', 'Everton', '0-2'),
#            ('Manchester City', 'West Brom', '1-1'),
#            ('Wolves', 'Chelsea', '2-1')]
print(teams)
# matches = [('Bordeaux', 'St. Etienne', '1-2'),
#            ('Lyon', 'Brest', '2-2'),
#            ('Monaco', 'Lens', '0-3'),
#            ('PSG', 'Lorient', '2-0'),
#            ('Rennes', 'Marsylia', '2-1'),
#            ('Metz', 'Strasbourg', '2-2'),
#            ('Dijon', 'Montpelier', '0-2'),
#            ('Montpelier', 'Metz', '0-2'),
#            ('Reims', 'Rennes', '0-2'),
#            ('Nice', 'Lille', '3-2')]

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

# matches = [('Kilmarnock FC', 'Aberdeen FC'),
#            ('Hibernian FC', 'Dundee United FC'),
#            ('Glasgow Rangers FC', 'Motherwell FC'),
#            ('Ross County',	'Hamilton Academicals FC'),
#            ('Saint Mirren FC', 'Saint Johnstone FC')]

matches = [('Crystal Palace', 'Liverpool'), ('Southampton', 'Manchester City'), ('Everton', 'Arsenal'),
           ('Newcastle', 'Fulham'), ('Brighton', 'Sheffield Utd'), ('Tottenham', 'Leicester'),
           ('Manchester Utd', 'Leeds'), ('West Brom', 'Aston Villa'), ('Burnley', 'Wolves'), ('Chelsea', 'West Ham')]

# matches = [('Liverpool', 'Wolves'), ('West Ham', 'Aston Villa'), ('Southampton', 'Manchester Utd'),
#            ('Aston Villa', 'Brighton'), ('Newcastle', 'Chelsea'), ('Manchester City', 'Liverpool'),
#            ('Southampton', 'Everton'), ('Arsenal', 'Sheffield Utd')]

for m in matches:
    scores = []
    scores_uo = defaultdict(float)
    scores_102 = defaultdict(float)
    for i in range(15):
        for j in range(15):
            p = find_prob(m[0], m[1], i)*find_prob(m[1], m[0], j)
            scores.append(((i, j), p))
            scores_uo[(i+j)] += p
            if i > j: scores_102[1] += p
            elif i == j: scores_102[0] += p
            else: scores_102[2] += p
    scores.sort(key= lambda x: -x[1])
    print(m)
    print('match score:')
    #print(sum(map(lambda x: x[1], scores)))
    for s in scores[:7]:
        print(s)
    print('sum of goals:')
    for i in range(7):
        print(i, scores_uo[i])
    print('p1: ' + str(scores_102[1]) + ', p2:' + str(scores_102[2]) + ', p0: ' + str(scores_102[0]))
    print('********************')

    print()

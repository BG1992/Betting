def get_score(score):
    left = int(score[:score.index('--')])
    right = int(score[score.index('--')+2:])
    return [left, right]

def format_row(row):
    _row = []
    for el in row:
        if el == '':
            _row.append(0)
        else:
            _row.append(float(el))
    return _row

def calc_equilibrium(left, right):
    p = ((right-1)*0.88+1)/((left-1)*0.88+1+(right-1)*0.88+1)
    return (left-1)*0.88*p - (1-p)

def new_bet(left, right, bet, under=None, score=None):
    if score is None: return [min(left, right), calc_equilibrium(left, right), bet][:]
    if bet == '1':
        if score[0] > score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == '0':
        if score[0] == score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == '2':
        if score[0] < score[1]:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    elif bet == 'goals':
        if sum(score) < under:
            if left < right: _result = 1
            else: _result = 0
        else:
            if left > right: _result = 1
            else: _result = 0
    return [min(left, right), calc_equilibrium(left, right), _result][:]

def new_bet2(left, right, bet, under=None, score=None):
    if bet == '1':
        try:
            if score[0] > score[1]:
                return [left, calc_equilibrium(left, right), 1][:]
            else:
                return [left, calc_equilibrium(left, right), 0][:]
        except:
            return [left, calc_equilibrium(left, right), bet][:]
    elif bet == '0':
        try:
            if score[0] == score[1]:
                return [left, calc_equilibrium(left, right), 1][:]
            else:
                return [left, calc_equilibrium(left, right), 0][:]
        except:
            return [left, calc_equilibrium(left, right), bet][:]
    elif bet == '2':
        try:
            if score[0] < score[1]:
                return [left, calc_equilibrium(left, right), 1][:]
            else:
                return [left, calc_equilibrium(left, right), 0][:]
        except:
            return [left, calc_equilibrium(left, right), bet][:]
    elif bet == '02':
        try:
            if score[0] <= score[1]:
                return [right, calc_equilibrium(left, right), 1][:]
            else:
                return [right, calc_equilibrium(left, right), 0][:]
        except:
            return [left, calc_equilibrium(left, right), bet][:]
    elif bet == '12':
        try:
            if score[0] != score[1]:
                return [right, calc_equilibrium(left, right), 1][:]
            else:
                return [right, calc_equilibrium(left, right), 0][:]
        except:
            return [right, calc_equilibrium(left, right), bet][:]
    elif bet == '10':
        try:
            if score[0] >= score[1]:
                return [right, calc_equilibrium(left, right), 1][:]
            else:
                return [right, calc_equilibrium(left, right), 0][:]
        except:
            return [right, calc_equilibrium(left, right), bet][:]
    elif bet == 'goals -':
        try:
            if sum(score) < under:
                _result = 1
            else:
                _result = 0
            return [left, calc_equilibrium(left, right), _result][:]
        except:
            return [left, calc_equilibrium(left, right), bet][:]
    elif bet == 'goals +':
        try:
            if sum(score) > under:
                _result = 1
            else:
                _result = 0
            return [right, calc_equilibrium(left, right), _result][:]
        except:
            return [right, calc_equilibrium(left, right), bet][:]

def check_bet(bet, score):
    if bet == '1':
        if score[0] > score[1]: return 1
    elif bet == '2':
        if score[0] < score[1]: return 1
    elif bet == '0':
        if score[0] == score[1]: return 1
    elif bet == '10':
        if score[0] >= score[1]: return 1
    elif bet == '02':
        if score[0] <= score[1]: return 1
    elif bet == '12':
        if score[0] != score[1]: return 1
    elif 'goals +' in bet:
        if sum(score) > float(bet[-3:]): return 1
    elif 'goals -' in bet:
        if sum(score) < float(bet[-3:]): return 1
    return 0
import random
import scipy.optimize

##sort rates by maximin

def maximin(probs, rate):
    return -min(map(lambda p, r: (r-1)*p - (1-p), probs, rate))

def constraint_probs(p):
    return sum(p) - 1

rates = [[1.37, 3.25], [2.75, 1.95, 4.1]]
updated_rates = []

for el in rates:
    res = scipy.optimize.minimize(maximin, x0=[1/len(el)]*len(el), bounds=[(0, 1) for _ in range(len(el))],
                                  method='SLSQP', args=(el,), constraints=({'type': 'eq', 'fun': constraint_probs}))
    updated_rates.append(tuple(el) + (-res.fun,))

updated_rates.sort(key=lambda x: -x[-1])

print(updated_rates)

## products over updated rates

tax = 0.12
N = 2
C = 0.9
cpn_nums = 2

calc_rates = updated_rates[:N]
full_comb_rates = []
n = len(calc_rates)

def dfs(comb_rates, prod):
    if len(comb_rates) == n:
        full_comb_rates.append(comb_rates + (round(prod,2),))
    else:
        for rate in calc_rates[len(comb_rates)][:-1]:
            dfs(comb_rates + (rate,), prod*rate)

dfs((), 1)
full_comb_rates.sort(key=lambda x:x[-1])
for el in full_comb_rates[:cpn_nums]:
    print(el)

def gen_weights(n):
    _weights = []
    left, right = 0, 1
    for i in range(n-1):
        _weights.append(random.uniform(left, right))
        right -= _weights[-1]
    _weights.append(right)
    return _weights

def f(weights):
    _coefs = []
    for i in range(len(full_comb_rates[:cpn_nums])):
        _coefs.append((1-tax)*(full_comb_rates[i][-1]-1)*weights[i] - (1-weights[i]))
    return -min(_coefs)

def constraint_weights(weights):
    return sum(weights) - 1

bnds = [(0,1) for _ in range(cpn_nums)]

weights = gen_weights(cpn_nums)
res = scipy.optimize.minimize(f, x0=weights, constraints=({'type': 'eq', 'fun': constraint_weights}),
                              method='SLSQP', bounds=bnds, tol=pow(10,-40), options={'maxiter':200000000})

print(res)
profits = []

for i in range(len(res.x)):
    profits.append(res.x[i]*(full_comb_rates[i][-1]-1)*(1-tax) - (1-res.x[i]))

print(profits)
print(min(profits)*C - (1-C))
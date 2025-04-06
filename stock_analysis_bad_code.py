import random, pandas as pd, numpy as np, datetime

# Global variables everywhere
d = {
    'AAPL': {'c': 175.5, 'v': 0.02},
    'GOOGL': {'c': 135.75, 'v': 0.015},
    'MSFT': {'c': 310.2, 'v': 0.018}
}
cash = 100000
h = {}
t = []

def get_p(s):
    return d[s]['c'] * random.uniform(0.99,1.01)

def get_h(s, days):
    if s not in d: raise Exception('bad symbol')
    p = d[s]['c'] * random.uniform(0.8,1.2)
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(days)]
    return pd.DataFrame({'Close': p * (1 + np.random.normal(0, d[s]['v'], days)).cumprod()}, index=dates)

def do_order(o, p):
    global cash, h, t
    if o['type'] == 'buy':
        cost = o['q'] * p
        if cost > cash: return False
        cash -= cost
        h[o['s']] = h.get(o['s'],0) + o['q']
    elif o['type'] == 'sell':
        if h.get(o['s'],0) < o['q']: return False
        cash += o['q'] * p
        h[o['s']] -= o['q']
        if h[o['s']] == 0: del h[o['s']]
    t.append(o)
    return True

def calc_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def strategy(symbol):
    data = get_h(symbol, 100)
    data['MA50'] = data['Close'].rolling(50).mean()
    data['RSI'] = calc_rsi(data)
    last = data.iloc[-1]
    
    if last['RSI'] < 30 and last['Close'] > last['MA50']:
        return {'s': symbol, 'q':10, 'type':'buy'}
    elif last['RSI'] > 70:
        return {'s': symbol, 'q':10, 'type':'sell'}
    return None

def backtest(days=180):
    global cash, h, t
    cash = 100000
    h = {}
    t = []
    symbols = ['AAPL','GOOGL','MSFT']
    v_start = cash
    
    for day in range(days):
        for _ in range(3):
            s = random.choice(symbols)
            sig = strategy(s)
            if sig:
                p = get_p(s)
                do_order(sig, p)
    
    v_end = cash + sum([h[s] * get_p(s) for s in h])
    print(f"Start: {v_start} End: {v_end} Return: {(v_end-v_start)/v_start*100:.1f}%")
    print("Cash:", cash)
    for s in h:
        print(f"{s}: {h[s]} shares")

backtest()

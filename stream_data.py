from ib_insync import *
import pandas as pd
from IPython.display import display, clear_output
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)
contracts = [Forex(pair) for pair in ('EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD')]
ib.qualifyContracts(*contracts)

eurusd = contracts[0]

for contract in contracts:
    ib.reqMktData(contract, '', False, False)

df = pd.DataFrame(
    index=[c.pair() for c in contracts],
    columns=['bidSize', 'bid', 'ask', 'askSize', 'high', 'low', 'close'])

def onPendingTickers(tickers):
    for t in tickers:
        df.loc[t.contract.pair()] = (
            t.bidSize, t.bid, t.ask, t.askSize, t.high, t.low, t.close)
        clear_output(wait=True)
    display(df)        

ib.pendingTickersEvent += onPendingTickers
ib.sleep(30)
ib.pendingTickersEvent -= onPendingTickers

for contract in contracts:
    ib.cancelMktData(contract)

def disconnect():
    bool_connected = ib.isConnected()
    print(f'Currently the connection to TWS is {bool_connected}')
    if bool_connected:
        ib.disconnect()
        bool_connected = ib.isConnected()
    return print(f'Currently the connection to TWS is {bool_connected}')

disconnect()




import time
import pandas as pd
from send_email import send_email
from ibapi.client import *
from ibapi.wrapper import *
from threading import Thread , Lock
import datetime as dt
import warnings

class TradingApp(EWrapper, EClient):
    def __init__(self, host, port, client_id):
        EClient.__init__(self, self)
        self.connect(host, port, client_id)
        self.thread = Thread(target=self.run)
        self.thread.start()
        self.batch_data = []
        self.lock = Lock()
        self.batch_threshold = 5


        time.sleep(1)  # Give some time to establish connection
        if self.isConnected():
            print(f"Successfully connected to IB API")
        else:
            raise ConnectionError("Failed to connect to IB API, did you login to the IBKR TWS Application?")
        #Dataframes to store relevant information about current portfolio
        self.acc_summary = pd.DataFrame(columns=['Date','reqId', 'Account','Tag', 'Value', 'Currency'])
        self.pnl_summary = pd.DataFrame(columns=['Date','reqId', 'DailyPnL','UnrealizedPnL', 'RealizedPnL'])
        self.position_summary = pd.DataFrame(columns=['Date','account', 'contract', 'position', 'avgCost'])


    def _add_to_batch(self, data, batch_index):
        """Adds data to the corresponding sub-list in a thread-safe manner"""
        with self.lock:
            while len(self.batch_data) <= batch_index:
                self.batch_data.append([])
            
            self.batch_data[batch_index].append(data)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,currency: str):
        """Receive summary of the current acount by providing the requested tag, their respective value and currency.

        Args:
            reqId (int): request ID, keep consistent with end call
            account (str): account number
            tag (str): variable requested for the account summary
            value (str): returned value
            currency (str): returned currency
        """
        warnings.filterwarnings("ignore", category=FutureWarning)
        super().accountSummary(reqId, account, tag, value, currency)
        t = dt.datetime.now()
        data = {
            'Date': t,
            'reqId': reqId,
            'Account': account,
            'Tag': tag,
            'Value': value,
            'Currency': currency
        }
        self._add_to_batch(data,0)
        if len(self.batch_data[0])>=self.batch_threshold:
            df_data = pd.DataFrame(self.batch_data[0])
            self.acc_summary = pd.concat([self.acc_summary,df_data],ignore_index=True)
            self.batch_data[0].clear()

    
    def accountSummaryEnd(self, reqId: int):
        # unsubscribe from account summary
        print("AccountSummaryEnd. reqId:", reqId)
    
    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        """Receive current profit and loss of the current portfolio. Taking the request ID and receiving daily profit and loss, unrealized PnL and realized PnL.

        Args:
            reqId (_type_): request ID, keep consistent with end call
            dailyPnL (_type_): daily PnL of entire portfolio
            unrealizedPnL (_type_): Unrealized PnL of entire portfolio
            realizedPnL (_type_): Realized PnL of entire portfolio
        """
        warnings.filterwarnings("ignore", category=FutureWarning)
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
        t = dt.datetime.now()
        data = {
              "Date" : t,
              "reqId":reqId,
              "DailyPnL": dailyPnL,
              "UnrealizedPnL": unrealizedPnL,
              "RealizedPnL": realizedPnL
              }
        self._add_to_batch(data,1)
        if len(self.batch_data[1])>=self.batch_threshold:
            df_data = pd.DataFrame(self.batch_data[1])
            self.pnl_summary = pd.concat([self.pnl_summary,df_data],ignore_index=True)
            self.batch_data[1].clear()

    def position(self, account: str, contract: Contract, position: Decimal, avgCost: float):
        warnings.filterwarnings("ignore", category=FutureWarning)
        # super.position(account, contract, position, avgCost)
        t = dt.datetime.now()
        data = {
              "Date" : t,
              "account":account,
              "contract": contract,
              "position": position,
              "avgCost": avgCost
              }
        self._add_to_batch(data,2)
        if len(self.batch_data[2])>=self.batch_threshold:
            df_data = pd.DataFrame(self.batch_data[2])
            self.position_summary = pd.concat([self.position_summary,df_data],ignore_index=True)
            self.batch_data[2].clear()
    
    def positionEnd(self):
        print("PositionEnd")


    def disconnect_api(self):
        # check connection, if true disconnect
        if self.isConnected():
            self.disconnect()
            print("Disconnected from IB API")
            
def daily_update(client):
    """Call daily update by receiving portfolio information and sending out email.

    Args:
        client (Class): connection to IBKR api
    """
    client.reqAccountSummary(1, "All", "$LEDGER:BASE")
    time.sleep(1)
    client.cancelAccountSummary(1)
    print('account summary request canceled')

    client.reqPnL(2, "U14552292", "")
    time.sleep(1)
    client.cancelPnL(2)
    print('account pnl request canceled')
    send_email(client.acc_summary, client.pnl_summary)

def portfolio_positions_overview(client):
    client.reqPositions()
    time.sleep(1)
    client.cancelPositions()
    print(client.position_summary)
    return



def main():
    client = TradingApp('127.0.0.1', 7496, 1)
    daily_update(client)
    # portfolio_positions_overview(client)
    client.disconnect_api()



if __name__ == "__main__":
    main()

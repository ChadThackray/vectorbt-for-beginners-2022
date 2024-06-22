import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime
import talib
from numba import njit

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(days=2)


btc_price = pd.read_csv("data.csv")
btc_price["Datetime"] = pd.to_datetime(btc_price["Datetime"])
btc_price.set_index("Datetime", inplace=True)

print(btc_price)

RSI = vbt.IndicatorFactory.from_talib('RSI')


@njit
def produce_signal(rsi, entry, exit):
    trend = np.where( rsi > exit, -1, 0)
    trend = np.where( (rsi < entry) , 1, trend)
    return trend

def custom_indicator(close, rsi_window = 14, entry = 30, exit = 70):
    rsi = RSI.run(close, rsi_window).real.to_numpy()
    return produce_signal(rsi, entry, exit)

ind = vbt.IndicatorFactory(
        class_name = "Combination",
        short_name = "comb",
        input_names = ["close"],
        param_names = ["rsi_window","entry","exit"],
        output_names = ["value"]
        ).from_apply_func(
                custom_indicator,
                rsi_window = 14,
                entry = 30,
                exit = 70,
                )

rsi_windows = np.arange(10,40,step=1,dtype=int)
entries = np.arange(10,40,step=1,dtype=int)

master_returns = []

for window in rsi_windows:
    res = ind.run(
            btc_price,
            rsi_window = window,
            entry = entry,
            exit = np.arange(60,85,step=1,dtype=int),
            param_product = True
            )
    entries = res.value == 1.0
    exits = res.value == -1.0
    pf = vbt.Portfolio.from_signals(btc_price, entries, exits)
    master_returns.append(pf.total_return())

print(master_returns)

returns = pd.concat(master_returns)

#returns = returns[ returns.index.isin(["BTC-USD"], level="symbol")]

#returns = returns.groupby(level=["comb_exit","comb_entry","symbol"]).mean()

print(returns.to_string())

print(returns.max())
print(returns.idxmax())



import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(days=2)


btc_price = vbt.YFData.download(
        ["BTC-USD","ETH-USD"],
        missing_index='drop',
        start=start_time,
        end=end_time,
        interval="1m").get("Close")

def custom_indicator(close, rsi_window = 14, ma_window = 50, entry = 30, exit = 70):
    close_5m = close.resample("5T").last()
    rsi = vbt.RSI.run(close_5m, window = rsi_window).rsi
    rsi, _ = rsi.align(close, 
            broadcast_axis=0,
            method='ffill',
            join='right')

    close = close.to_numpy()
    rsi = rsi.to_numpy()
    ma = vbt.MA.run(close, ma_window).ma.to_numpy()
    trend = np.where( rsi > exit, -1, 0)
    trend = np.where( (rsi < entry) & (close < ma), 1, trend)
    return trend

ind = vbt.IndicatorFactory(
        class_name = "Combination",
        short_name = "comb",
        input_names = ["close"],
        param_names = ["rsi_window", "ma_window","entry","exit"],
        output_names = ["value"]
        ).from_apply_func(
                custom_indicator,
                rsi_window = 14,
                ma_window = 50,
                entry = 30,
                exit = 70,
                keep_pd=True
                )

res = ind.run(
        btc_price,
        rsi_window = np.arange(10,40,step=3,dtype=int),
        #ma_window = np.arange(20,200,step=20,dtype=int),
        entry = np.arange(10,40,step=4,dtype=int),
        exit = np.arange(60,85,step=4,dtype=int),
        param_product = True
        )

#print(res.value.to_string())

entries = res.value == 1.0
exits = res.value == -1.0

pf = vbt.Portfolio.from_signals(btc_price, entries, exits)

returns = pf.total_return()

#returns = returns[ returns.index.isin(["BTC-USD"], level="symbol")]

#returns = returns.groupby(level=["comb_exit","comb_entry","symbol"]).mean()

print(returns.to_string())

print(returns.max())
print(returns.idxmax())

"""comb_rsi_window  comb_ma_window"""

fig = returns.vbt.volume(
        x_level = "comb_rsi_window",
        y_level = "comb_entry",
        z_level = "comb_exit",
        slider_level = "symbol",
        )
fig.show()


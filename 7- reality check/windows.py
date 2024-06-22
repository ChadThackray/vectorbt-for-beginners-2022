
import pandas as pd
import vectorbt as vbt
import numpy as np
import datetime

now = datetime.datetime.now()
before = now - datetime.timedelta(days=3)

btc_price = vbt.YFData.download(
        "BTC-USD",
        missing_index="drop",
        interval="1m",
        start=before.timestamp(),
        end=now.timestamp()).get("Close")


btc_price, range_indexes = btc_price.vbt.range_split(n=100, range_len=1440)

# RSI SECTION
def optimize_rsi(close, window, entry, exit):
    rsi = vbt.IndicatorFactory.from_talib("RSI").run(close, timeperiod=window).real
    return rsi < entry, rsi > exit

rsi_ind = vbt.IndicatorFactory(
        class_name="optimizeRsi",
        short_name="rsi",
        input_names=["close"],
        param_names=["window","entry","exit"],
        output_names=["entries","exits"]
        ).from_apply_func(
                optimize_rsi,
                window=14,
                entry=30,
                exit=70)


step_size =10
entries = np.arange(10,45, step=step_size, dtype =int)
exits = np.arange(55,95, step=step_size, dtype =int)
windows = np.arange(10,45, step=step_size, dtype =int)

rsi_res = rsi_ind.run(
        btc_price,
        window=14,
        entry=20,
        exit=80,
        )

rsi_entries = rsi_res.entries
rsi_exits = rsi_res.exits

rsi_exits.iloc[-1, :] = True

rsi_pf = vbt.Portfolio.from_signals(btc_price, rsi_entries, rsi_exits, freq="1T")

rsi_tot_returns = rsi_pf.total_return()

def random_signal(close):
    return np.random.randint(0,2, size=close.shape)

rand_ind = vbt.IndicatorFactory(
        class_name="Random",
        short_name="rand",
        input_names=["close"],
        output_names=["signal"]
        ).from_apply_func(
                random_signal)



rand_res = rand_ind.run(
        btc_price
        )

rand_entries = rand_res.signal == 1
rand_exits = rand_res.signal == 0

rand_exits.iloc[-1, :] = True

rand_pf = vbt.Portfolio.from_signals(btc_price, rand_entries, rand_exits, freq="1T")

rand_tot_returns = rand_pf.total_return()


df = pd.DataFrame({
    "rsi":list(rsi_tot_returns),
    "rand":list(rand_tot_returns)
    })

print(df.median())

box = vbt.plotting.Box(
        data = df,
        trace_names=["rsi","rand"])

box.fig.show()

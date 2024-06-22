import vectorbt as vbt
import datetime

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days = 3)

vbt.settings.set_theme("seaborn")
vbt.settings['plotting']['layout']['width'] = 1200
vbt.settings['plotting']['layout']['height'] = 600

btc_price = vbt.YFData.download(
        ["BTC-USD"],
        interval="1m",
        start = start_date,
        end = end_date,
        missing_index='drop').get("Close")

print(btc_price)

fast_ma = vbt.MA.run(btc_price, window =50)
slow_ma = vbt.MA.run(btc_price, window =200)

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(btc_price, entries, exits)

fig = pf.plot(subplots = [
    ('price', dict(
        title='Price',
        yaxis_kwargs=dict(title='Price')
        )),
    ('price', dict(
        title='Price',
        yaxis_kwargs=dict(title='Price')
        )),
    'orders',
    'trade_pnl',
    'cum_returns',
    'drawdowns'],
    make_subplots_kwargs=dict(rows=10, cols=2))

scatter = vbt.plotting.Scatter(
        data = btc_price,
        x_labels = btc_price.index,
        trace_names = ["Price"],
        trace_kwargs=dict(line=dict(color='red')),
        add_trace_kwargs=dict(row=1,col=1),
        fig=fig)

fast_ma_scatter = vbt.plotting.Scatter(
        data = fast_ma.ma,
        x_labels = fast_ma.ma.index,
        trace_names = ["Fast_ma"],
        trace_kwargs=dict(line=dict(color='green')),
        add_trace_kwargs=dict(row=1,col=2),
        fig=fig)

slow_ma_scatter = vbt.plotting.Scatter(
        data = slow_ma.ma,
        x_labels = slow_ma.ma.index,
        trace_names = ["slow_ma"],
        trace_kwargs=dict(line=dict(color='blue')),
        add_trace_kwargs=dict(row=1,col=2),
        fig=fig)


entries_plot = entries.vbt.signals.plot_as_entry_markers(
        slow_ma.ma,
        add_trace_kwargs=dict(row=1,col=2),
        fig=fig)

exits_plot = exits.vbt.signals.plot_as_exit_markers(
        slow_ma.ma,
        add_trace_kwargs=dict(row=1,col=2),
        fig=fig)

fig.add_hline( y= 38000,
                line_color="#FFFFFF",
                row=1,
                col = 2,
                line_width=20)

"""
fig = btc_price.vbt.plot(trace_kwargs=dict(name='Price',line=dict(color='red')))
fig = fast_ma.ma.vbt.plot(trace_kwargs=dict(name='Fast_ma',line=dict(color='blue')), fig=fig)
fig = slow_ma.ma.vbt.plot(trace_kwargs=dict(name='Slow_ma',line=dict(color='green')), fig=fig)
fig = entries.vbt.signals.plot_as_entry_markers(btc_price, fig=fig)
fig = exits.vbt.signals.plot_as_exit_markers(btc_price, fig=fig)
"""

fig.show()

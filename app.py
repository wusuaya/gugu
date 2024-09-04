import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
from datetime import datetime, timedelta

# 初始化会话状态
if 'current_day' not in st.session_state:
    st.session_state.current_day = 0
if 'cash' not in st.session_state:
    st.session_state.cash = 10000  # 初始资金
if 'shares' not in st.session_state:
    st.session_state.shares = 0
if 'portfolio_value' not in st.session_state:
    st.session_state.portfolio_value = []
if 'actions' not in st.session_state:
    st.session_state.actions = []

# 设置页面标题
st.title("交互式K线模拟交易系统")

# 用户输入股票代码和日期范围
stock_symbol = st.sidebar.text_input("输入股票代码 (例如: AAPL, TSLA)", value="AAPL")
start_date = st.sidebar.date_input("选择开始日期", value=(datetime.today() - timedelta(days=180)))
end_date = st.sidebar.date_input("选择结束日期", value=datetime.today())

# 获取股票数据
def load_stock_data(symbol, start, end):
    stock_data = yf.download(symbol, start=start, end=end)
    stock_data.rename(columns={'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
    return stock_data

df = load_stock_data(stock_symbol, start_date, end_date)

# 如果没有数据，提示用户
if df.empty:
    st.error("无法获取股票数据，请检查股票代码或时间范围。")
else:
    total_days = len(df)
    current_data = df.iloc[st.session_state.current_day]

    # 显示当前账户信息
    st.sidebar.header("账户信息")
    st.sidebar.write(f"现金: ${st.session_state.cash:.2f}")
    st.sidebar.write(f"持股: {st.session_state.shares} 股")
    current_price = current_data['Close']
    portfolio = st.session_state.cash + st.session_state.shares * current_price
    st.sidebar.write(f"总资产: ${portfolio:.2f}")

    # 显示K线图
    def plot_kline(data):
        mpf.plot(data, type='candle', volume=True, style='charles', mav=(3,6,9), show_nontrading=False, returnfig=True)

    if st.session_state.current_day > 0:
        plot_data = df.iloc[:st.session_state.current_day + 1]
    else:
        plot_data = df.iloc[:1]

    fig, axlist = mpf.plot(plot_data, type='candle', volume=True, style='charles', mav=(3,6,9), returnfig=True)
    st.pyplot(fig)

    # 显示当前交易日信息
    st.header(f"第 {st.session_state.current_day + 1} 天: {current_data.name.date()}")
    st.write(f"收盘价: ${current_price:.2f}")

    # 创建交易按钮
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("全仓买入"):
            if st.session_state.cash >= current_price:
                shares_to_buy = st.session_state.cash // current_price
                cost = shares_to_buy * current_price
                st.session_state.shares += shares_to_buy
                st.session_state.cash -= cost
                st.session_state.actions.append(f"Day {st.session_state.current_day + 1}: 全仓买入 {shares_to_buy} 股 at ${current_price:.2f}")
                st.success(f"买入 {shares_to_buy} 股")
            else:
                st.error("资金不足以买入")

    with col2:
        if st.button("半仓买入"):
            if st.session_state.cash >= current_price:
                shares_to_buy = (st.session_state.cash // current_price) // 2
                cost = shares_to_buy * current_price
                st.session_state.shares += shares_to_buy
                st.session_state.cash -= cost
                st.session_state.actions.append(f"Day {st.session_state.current_day + 1}: 半仓买入 {shares_to_buy} 股 at ${current_price:.2f}")
                st.success(f"买入 {shares_to_buy} 股")
            else:
                st.error("资金不足以买入")

    with col3:
        if st.button("全仓卖出"):
            if st.session_state.shares > 0:
                revenue = st.session_state.shares * current_price
                st.session_state.cash += revenue
                st.session_state.actions.append(f"Day {st.session_state.current_day + 1}: 全仓卖出 {st.session_state.shares} 股 at ${current_price:.2f}")
                st.success(f"卖出 {st.session_state.shares} 股")
                st.session_state.shares = 0
            else:
                st.error("没有持股可卖")

    with col4:
        if st.button("半仓卖出"):
            if st.session_state.shares > 0:
                shares_to_sell = st.session_state.shares // 2
                revenue = shares_to_sell * current_price
                st.session_state.cash += revenue
                st.session_state.actions.append(f"Day {st.session_state.current_day + 1}: 半仓卖出 {shares_to_sell} 股 at ${current_price:.2f}")
                st.success(f"卖出 {shares_to_sell} 股")
                st.session_state.shares -= shares_to_sell
            else:
                st.error("没有持股可卖")

    with col5:
        if st.button("不操作"):
            st.session_state.actions.append(f"Day {st.session_state.current_day + 1}: 不操作")
            st.info("保持不变")

    # 下一天按钮
    if st.session_state.current_day < total_days - 1:
        if st.button("下一天"):
            st.session_state.current_day += 1
            portfolio = st.session_state.cash + st.session_state.shares * df.iloc[st.session_state.current_day]['Close']
            st.session_state.portfolio_value.append(portfolio)
    else:
        st.success("已到最后一天")

    # 显示交易记录
    st.header("交易记录")
    for action in st.session_state.actions:
        st.write(action)

    # 显示最终收益
    if st.session_state.current_day == total_days - 1:
        final_portfolio = st.session_state.cash + st.session_state.shares * current_price
        initial_capital = 10000
        profit = final_portfolio - initial_capital
        roi = (profit / initial_capital) * 100
        st.header("最终收益")
        st.write(f"最终总资产: ${final_portfolio:.2f}")
        st.write(f"总收益: ${profit:.2f}")
        st.write(f"投资回报率: {roi:.2f}%")


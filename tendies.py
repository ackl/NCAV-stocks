import os
import yfinance as yf
from yahooquery import Ticker
import pandas as pd

tickers = None

with open('./r2k.csv', 'r') as f:
    tickers = [line.rstrip('\n') for line in f]

CUR_ASS = 'Total Current Assets'
TOT_LIB = 'Total Liab'

P2FCF_SECTOR = {
    'Technology': 17.7,
    'Healthcare':  12.53,
    'Consumer Defensive':  30.59,
    'Industrials': 45.42,
    'Industrial Goods': 46.43,
    'Communication Services': 17.93,
    'Consumer Cyclical': 25.9,
    'Utilities': 41.40,
    'Energy': 6.05,
    'Basic Materials': 8.16,
    'Real Estate': 7.72,
    'Financial Services': 25.08
}

data = []
total = len(tickers)

def get_info(ticker, key):
    if key in ticker.quotes[t]:
        return ticker.quotes[t][key]
    else:
        return None

for i, t in enumerate(tickers):
    print('Getting data for {}, {} / {} ({}%)'.format(t, i, total, i / total * 100))
    ticker = Ticker(t)

    if type(ticker.asset_profile[t]) is not dict:
        print('{} aint cash money G'.format(t))
        continue

    if type(ticker.cash_flow()) is str:
        print('{} got no cash flo'.format(t))
        continue

    if type(ticker.balance_sheet()) is str:
        print('{} got no BS'.format(t))
        continue

    free_cash_flow = ticker.cash_flow()['FreeCashFlow'][-1]

    try:
        current_assets = ticker.balance_sheet()['CurrentAssets'][-1]
    except KeyError:
        print('{} no currentAssets avail'.format(t))
        continue

    total_liabs = ticker.balance_sheet()['TotalLiabilitiesNetMinorityInterest'][-1]
    shares_outstanding = ticker.quotes[t]['sharesOutstanding']
    NCAV = (current_assets - total_liabs) / shares_outstanding

    price_to_fcf = ticker.quotes[t]['marketCap'] / free_cash_flow

    data = [ [
        t,
        ticker.quotes[t]['longName'],
        current_assets,
        total_liabs,
        shares_outstanding,
        NCAV,
        get_info(ticker, 'trailingPE'),
        get_info(ticker, 'forwardPE'),
        get_info(ticker, 'epsTrailingTwelveMonths'),
        get_info(ticker, 'epsForward'),
        price_to_fcf,
        P2FCF_SECTOR[ticker.summary_profile[t]['sector']],
        ticker.summary_profile[t]['sector'],
        ticker.summary_profile[t]['industry']
        ] ]

    data_frame = pd.DataFrame(data, columns=['Ticker', 'Name', CUR_ASS, TOT_LIB, 'Shares Outstanding',
        'Net Current Asset Value', 'PE (trailing)', 'PE (forward)',
        'EPS (trailing)', 'EPS (forward)', 'Price to FCF', 'Sector avg P2FCF', 'Sector', 'Industry'])

    data_frame.to_csv('tendies_output.csv', index=False, mode='a', header=not os.path.exists('tendies_output.csv'))


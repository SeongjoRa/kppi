import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

st.set_page_config(
    page_title="K/PP Index",
    page_icon="🧊",
    layout="wide",
)

if 'greeting' not in st.session_state:
    st.session_state['greeting'] = 'Hello, there!'
st.write(st.session_state['greeting'])	# Hello, there!

# st.sidebar.success("Select a page above")
col1, col2, col3, col4 = st.columns(4)
col1.title("K/PP Idx")

pd.options.display.float_format = '{:.3f}'.format

url = "https://api.pro.coins.ph//openapi/quote/v1/ticker/price" # All Coins available in Coins Pro
try:
    res_pro = requests.get(url, verify= False)
    df = pd.read_json(res_pro.url)
    df.rename(columns= {"symbol":"Coins Pro", "price":"PHP"}, inplace=True)
    php_only = df[df["Coins Pro"].str.contains("PHP") == False].index # Condition to dorp rows of non-PHP Coins
    df.drop(php_only, inplace= True)
    php_coins = list(df["Coins Pro"])
except:
    st.error("Error occured from Coins Pro Ticker data : Try to Reload!", icon="🚨")
    sys.exit()

url3 = "https://api.upbit.com/v1/market/all?isDetails=false" # All Coins available in UPbit
header = {"accept": "application/json"}
try:
    res_upbit = requests.get(url3, headers= header,verify= False)
    upbit = res_upbit.json()
except:
    st.error("Error occured from Upbit Market data : Try to Reload!", icon="🚨")
    sys.exit()

krw_coins = []; krw_temp = []; krw_temp2 = [] 
for market in upbit:
    if "KRW-" in market["market"]:
        krw_coins.append(market["market"]) # All available KRW coins
        krw_temp.append(market["market"].replace("KRW-","") + "PHP") #Change the name of KRW coins to compare with All PHP coins
        
for coin in krw_temp:
    if coin in php_coins:
        krw_temp2.append(coin) # Coins available in both Coins Pro and UPbit

df = df[df["Coins Pro"].isin(krw_temp2)]
df.reset_index(drop= True, inplace= True)

def prices(url, payload):
    return requests.get(url, params=payload, verify= False)
try:
    fixer_url = "https://api.apilayer.com/fixer/latest"
    fixer_payload = {"apikey":"YUSsztE6yPPsmvM5N7soeY2g0NucdN18", "symbols":"KRW", "base":"PHP"}
    res_fixer = prices(fixer_url, fixer_payload)
    phpkrw = res_fixer.json()["rates"]["KRW"]
except:
    pass
finally:
    url2 = "https://www.google.com/finance/quote/PHP-KRW?sa=X&ved=2ahUKEwjdo7-ajMX-AhUFbt4KHSOzAYcQmY0JegQIARAZ"
    response = requests.get(url2, verify= False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    phpkrw = float(soup.find("div", attrs={"class":"YMlKec fxKbKc"}).get_text().strip())

df["*Converted KRW"] = df["PHP"] * phpkrw
php_coins = list(df["Coins Pro"])
        
krw_coins.clear()
for coin in php_coins:
    krw_coins.append("KRW-" + coin.replace("PHP",""))    

prices = []; trade_time = []
try:
    res_upbit2 = requests.get("https://api.upbit.com/v1/ticker?markets="+"{}".format(",".join(krw_coins)),headers= header, verify= False)
    upbit2 = res_upbit2.json()
except:
    st.error("Error occured from Upbit Ticket data : Try to Reload!", icon="🚨")
    sys.exit()

for i in range(len(krw_coins)):
    prices.append(upbit2[i]["trade_price"])
    trade_time.append(upbit2[i]["trade_time_kst"])
df3 = pd.DataFrame(list(zip(krw_coins, prices, trade_time)), columns= ["UPbit", "KRW", "KSTime"])

df2 = pd.concat([df, df3], axis=1)
df2["K/PPI"] = df2["*Converted KRW"]/df2["KRW"]
st.session_state['df2'] = df2

df3 = df2[["Coins Pro", "*Converted KRW", "UPbit", "KRW", "K/PPI"]]
max_i = round((df3["K/PPI"].max() - 1) * 100, 3) 
min_i = round((df3["K/PPI"].min() - 1) * 100, 3)

max_only = df3.iloc[df2.idxmax(axis=0, skipna=True, numeric_only=True)["K/PPI"]]
min_only = df3.iloc[df2.idxmin(axis=0, skipna=True, numeric_only=True)["K/PPI"]]

col2.metric(label= "MAX K/PPI", value= max_only[0][:-3], delta= f"{max_i}%")
col3.metric(label= "MIN K/PPI", value= min_only[0][:-3], delta= f"{min_i}%")
col4.metric(label= "Exchange Rate", value= phpkrw)

# st.divider()
col11, col22 = st.columns(2)
col11.json(max_only.to_json())
col22.json(min_only.to_json())

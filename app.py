from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
from pycoingecko import CoinGeckoAPI
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

cg = CoinGeckoAPI()
app = Flask(__name__)

menu = ("""       ✨Welcome! I am Amanda✨\n
Your crypto companion \n
               🛠 MENU 🛠 
🔸 Type any coin to learn it
🔹 Type 'T' -> Trending Coins
🔸 Type 'WB' -> Bitcoin Whales
🔹 Type 'WE' -> Ethereum Whales
🔸 Type 'E' -> Top Exchanges
🔹 Type 'NFT' -> 20 R NFTs
🔸 Type 'stats' -> Crypto Stats

📌 Type 'ping' to Ping Me!
📌 Type 'amanda' for more info

🔥 Anything else would return this menu 🙂
🔥 I might break: Am under active dev't...

               __amanda__
""")


"""COIN INFO FROM COIN Market Cap"""
url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
api = "7a08b482-9d34-4681-9c9b-688e9f866e3f"

parameters = {
'start':'1',
'limit':'200',
'convert':'USD'
}
headers = {
'Accepts': 'application/json',
'X-CMC_PRO_API_KEY': api,
}

session = Session()
session.headers.update(headers)

top_200_coins = list()

def return_coins():
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        for i in range(200):
            d = data["data"][i]["name"]
            top_200_coins.append(d)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

return_coins()

@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    
    # More info about the bot: Amanda
    if 'amanda' == incoming_msg:
        about = "Yay! Am Amanda, crafted by Ronnie Atuhaire: I am using CoinGecko & CoinMarket APIs for crypto related tasks... anything else contact @ 0703151746 ❣ "
        msg.body(about)
        responded = True
        
    # Getting to learn a particular crypto sent by user  
    if incoming_msg in list(map(lambda x: x.lower(), top_200_coins)):
        learn = cg.get_coin_by_id(id=incoming_msg)
        learn = learn["description"]["en"].split()[:100]
        learn_info = " ".join(learn)
        msg.body(learn_info)
        responded = True
        
    # Get latest and trending coins on the platform  
    if 't' == incoming_msg:
        t = cg.get_search_trending()
        for i in range(5):
            trends_data = f'🔥{i}🔥 {t["coins"][i]["item"]["name"]} with a market cap rank of {t["coins"][i]["item"]["market_cap_rank"]}'
            msg.body(trends_data)
        responded = True
        
    # Get Bitcoin Whales abbreviated as 'wb' 
    if "wb" == incoming_msg:
        wb = cg.get_companies_public_treasury_by_coin_id(coin_id="bitcoin")

        w_b = wb["companies"]
        for i in range(10):
            w_b_data = f'🔥{i}🔥 {w_b[i]["name"]} has {w_b[i]["total_holdings"]} bitcoins'
            msg.body(w_b_data)
        responded = True
        
    # Get Ethereum Whales abbreviated as 'we'
    if "we" == incoming_msg:
        we = cg.get_companies_public_treasury_by_coin_id(coin_id="ethereum")
        w_e = we["companies"]
        for i in range(3):
            w_e_data = f'🔥{i}🔥 {w_e[i]["name"]} has {w_e[i]["total_holdings"]} eth coins'
            msg.body(w_e_data)
        responded = True
        
    # Get top exchanges  
    if 'e' == incoming_msg:
        e = cg.get_exchanges_list() 
        for i in range(10):
            e_data = f""" 🔥{i}🔥 {e[i]["name"]} : Since {e[i]["year_established"]}: Origin:{e[i]["country"]} """
            msg.body(e_data)
        responded = True
        
    # Get current global crypto stats
    if 'stats' == incoming_msg:
        stats = cg.get_global()
        data_stats = f'There are currently {stats["active_cryptocurrencies"]} active crypto currencies and {stats["ongoing_icos"]} ongoing ICOs with around {stats["markets"]} markets!'
        msg.body(data_stats)
        responded = True
        
    # Get 20 random NFTs   
    if 'nft' == incoming_msg:
        top_nfts = "https://api.coingecko.com/api/v3/nfts/list"
        r = requests.request("GET", top_nfts)
        for i in range(20):
            if r.status_code == 200:
                data = r.json()
                nft = f'🚩{i}🚩 {data[i]["name"]} : {data[i]["asset_platform_id"]}'
                msg.body(nft)
        responded = True
        
    # If Amanda is up and running:
    if 'ping' == incoming_msg:
        ping = cg.ping()
        if ping["gecko_says"]:
            p_msg = f"Yeah... am up! & My main server is Up too...Let's do this >>>!"
            msg.body(p_msg)
        else:
            p_msg = f"Oooops , my server is down..Amanda will return shortly"
            msg.body(p_msg)
        responded = True
        
    # If no response, return menu    
    if not responded:
        msg.body(menu)
                
    return str(resp)

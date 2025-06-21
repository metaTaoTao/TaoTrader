import requests

# 替换成你的API Key和Secret Key
api_key = "G6Gbmnb18VnKyZhlD1m1JDMR0ukUeOxbSzyhVI2WWo7DGq5vUw6j4PZtUKlx3vWO"
secret_key = "b6IHw0rR9OpggwNHUfYBx680Mm61oPfLJJnkbdOg7ZtTMUb12dldvt2L4k9IaEhY"

# 构造请求头
headers = {
    "X-MBX-APIKEY": api_key
}

# 获取所有交易对的信息
url = "https://api.binance.com/api/v3/exchangeInfo"
response = requests.get(url)
data = response.json()

# 打印所有交易对的信息
for symbol_info in data['symbols']:
    print(symbol_info['symbol'])

# 获取指定交易对的信息，例如BTCUSDT
url = f"https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
response = requests.get(url)
ticker_info = response.json()
print(ticker_info)
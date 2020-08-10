from flask import Flask
from flask import jsonify 
from flask import request
from flask_cors import CORS, cross_origin
from iqoptionapi.stable_api import IQ_Option
from os import environ
import time
import re
from datetime import datetime
from dateutil import tz

idCompra = 0
iqoption = IQ_Option(environ['USUARIO'], environ['SENHA'])
iqoption.connect()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/from", methods=["GET"])
@cross_origin()
def send_pair2():
    currency = request.args.get('currency')
    if currency is not None:
        content = ''
        with open('pairs.txt') as f:
            content = f.read()
        print(content)
        pairs = re.findall(r"USD\w{3}|\w{3}USD", content, flags=re.MULTILINE)
        print(pairs)
        to_options = list(map(lambda x: x.replace('USD', '') , pairs))
        to_options_2 = list(map(lambda x: x.replace(currency, 'USD'), to_options))
        print(to_options_2)
        return jsonify(to_options_2)

@app.route("/", methods=["GET"])
@cross_origin()
def send_pair():
    currency = 'BRL'
    if currency is not None:
        content = ''
        with open('pairs.txt') as f:
            content = f.read()
        print(content)
        pairs = re.findall(r"USD\w{3}|\w{3}USD", content, flags=re.MULTILINE)
        print(pairs)
        to_options = list(map(lambda x: x.replace('USD', '') , pairs))
        to_options_2 = list(map(lambda x: x.replace(currency, 'USD'), to_options))
        to_options_2.insert(0, currency)
        return jsonify(to_options_2)


@app.route("/convert", methods=["GET"])
@cross_origin()
def process_pairs():
    value = request.args.get('value')
    pair = request.args.get('pair')
    fromCurrency = pair[0:3]
    toCurrency = pair[3:6]
    print(pair)
    print(fromCurrency+toCurrency)
    print(toCurrency+fromCurrency)
    content = ''
    with open('pairs.txt') as f:
        content = f.read()
    if fromCurrency+toCurrency in content:
        print('FROM/TO')
        print(fromCurrency+toCurrency)
        candles = iqoption.get_candles(fromCurrency+toCurrency,60,2,time.time())
        forex = candles[0]['close']
        return jsonify({"hasForexData": True, "forex": forex, "value": float(value) * forex})
    if toCurrency+fromCurrency in content:
        print('TO/FROM')
        print(toCurrency+fromCurrency)
        candles = iqoption.get_candles(toCurrency+fromCurrency,60,2,time.time())
        forex = candles[0]['close']
        return jsonify({"hasForexData": True, "forex": forex, "value": float(value) / forex})
    if 'USD'+fromCurrency in content and 'USD'+toCurrency in content:
        print('USD'+fromCurrency)
        print('USD'+toCurrency)
        candles = iqoption.get_candles('USD'+fromCurrency,60,2,time.time())
        print(candles)
        forex = candles[0]['close']
        valueInDolars = float(value) / forex
        print(valueInDolars)
        candles2 = iqoption.get_candles('USD'+toCurrency,60,2,time.time())
        forex2 = candles2[0]['close']
        print(float(valueInDolars) * forex2)
        return jsonify({"hasForexData": False, "forex": forex2, "value": float(valueInDolars) * forex2})
    if 'USD'+fromCurrency in content and toCurrency+'USD' in content:
        print('USD'+fromCurrency)
        print(toCurrency+'USD')
        candles = iqoption.get_candles('USD'+fromCurrency,60,2,time.time())
        print(candles)
        forex = candles[0]['close']
        valueInDolars = float(value) / forex
        print(valueInDolars)
        candles2 = iqoption.get_candles(toCurrency+'USD',60,2,time.time())
        forex2 = candles2[0]['close']
        print(float(valueInDolars) / forex2)
        return jsonify({"hasForexData": False, "forex": forex2, "value": float(valueInDolars) / forex2})
    if 'USD'+toCurrency in content and fromCurrency+'USD' in content:
        print('USD'+toCurrency)
        print(fromCurrency+'USD')
        candles = iqoption.get_candles(fromCurrency+'USD',60,2,time.time())
        forex = candles[0]['close']
        valueInDolars = float(value) * forex
        candles2 = iqoption.get_candles('USD'+toCurrency,60,2,time.time())
        forex2 = candles2[0]['close']
        return jsonify({"hasForexData": False, "forex": forex2, "value": float(valueInDolars) * forex2})
            
def timestamp_converter(x):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))
    print('HORA', hora)
    horas = str(hora.astimezone(tz.gettz('America/Sao_Paulo')))
    print('HORA LOCAL', horas)
    return horas

@app.route("/history", methods=["GET"])
@cross_origin()
def get_history():
    pair = request.args.get('pair')
    period = request.args.get('period')
    fromCurrency = pair[0:3]
    toCurrency = pair[3:6]

    content = ''
    with open('pairs.txt') as f:
        content = f.read()
    if fromCurrency+toCurrency in content:
        print('FROM/TO')
        print(fromCurrency+toCurrency)
        pair = fromCurrency+toCurrency
    if toCurrency+fromCurrency in content:
        print('TO/FROM')
        print(toCurrency+fromCurrency)
        pair = toCurrency+fromCurrency
    if 'USD'+fromCurrency in content and 'USD'+toCurrency in content:
        pair = 'USD'+toCurrency
    if 'USD'+fromCurrency in content and toCurrency+'USD' in content:
        pair = toCurrency+'USD'
    if 'USD'+toCurrency in content and fromCurrency+'USD' in content:
        pair = fromCurrency+'USD'

    candles = ''
    if (period == 'month'):
        candles = iqoption.get_candles(pair, 86400, 30, time.time())
    if (period == 'day'):
        candles = iqoption.get_candles(pair, 3600, 24, time.time())
    if (period == 'hour'):
        candles = iqoption.get_candles(pair, 60, 60, time.time())

    dates = list(map(lambda x: timestamp_converter(x['to']), candles))
    data = list(map(lambda x: x['close'], candles))
    return jsonify({"values": data, "dates": dates})
    

def get_forex(fromCurrency, toCurrency, value):
    content = ''
    with open('pairs.txt') as f:
        content = f.read()
    if fromCurrency+toCurrency in content:
        print('FROM/TO')
        print(fromCurrency+toCurrency)
        candles = iqoption.get_candles(fromCurrency+toCurrency,60,2,time.time())
        forex = candles[1]['close']
        return forex
    if toCurrency+fromCurrency in content:
        print('TO/FROM')
        print(toCurrency+fromCurrency)
        candles = iqoption.get_candles(toCurrency+fromCurrency,60,2,time.time())
        forex = candles[1]['close']
        return forex
    if toCurrency+fromCurrency not in content and fromCurrency+toCurrency not in content:
        candles = iqoption.get_candles('USD'+fromCurrency,60,2,time.time())
        forex = candles[1]['close']
        valueInDolars = float(value) / forex
        print(valueInDolars)
        candles2 = iqoption.get_candles('USD'+toCurrency,60,2,time.time())
        forex2 = candles2[1]['close']
        print(float(valueInDolars) * forex2)
        return {"dollarForex": forex, "toCurrencyForex": forex2}

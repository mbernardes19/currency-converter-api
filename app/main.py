from flask import Flask
from flask import jsonify 
from flask import request
from iqoptionapi.stable_api import IQ_Option
from os import environ

idCompra = 0
iqoption = IQ_Option(environ['USUARIO'], environ['SENHA'])
iqoption.connect()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def teste():
    print(request.args.get('pair'))
    return "<h1>Oi</h1>"

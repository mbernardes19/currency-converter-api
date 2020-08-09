import pytest

from app import main

@pytest.fixture
def client():
    main.app.config['TESTING'] = True

    with main.app.test_client() as client:
        yield client

def test_get_all_possible_from_currencies(client):
    response = client.get('/')
    expected_body = b'["BRL","NZD","THB","AUD","CHF","SEK","CZK","MXN","TRY","JPY","EUR","PLN","HUF","RUB","GBP","SGD","CAD","INR","USD","NOK","DKK"]\n'
    assert expected_body == response.data

def test_get_all_possible_to_currencies_from_BRL(client):
    response = client.get('/from?currency=BRL')
    expected_body = b'["NZD","THB","AUD","CHF","SEK","CZK","MXN","TRY","JPY","EUR","PLN","HUF","RUB","GBP","SGD","CAD","INR","USD","NOK","DKK"]\n'
    assert expected_body == response.data

def test_convert_from_BRL_to_USD(client):
    response = client.get('/convert?value=20.5&pair=BRLUSD')
    response_str = response.data.decode('utf-8')
    convertion = 20.5 / main.get_forex('BRL', 'USD', 20.5)
    assert str(convertion) in response_str

def test_convert_from_USD_to_BRL(client):
    response = client.get('/convert?value=30.5&pair=USDBRL')
    response_str = response.data.decode('utf-8')
    convertion = 30.5 * main.get_forex('USD', 'BRL', 30.5)
    assert str(convertion) in response_str

def test_convert_from_BRL_to_JPY(client):
    response = client.get('/convert?value=32.5&pair=BRLJPY')
    response_str = response.data.decode('utf-8')
    forexes = main.get_forex('BRL', 'JPY', 32.5)
    toDollar = 32.5 / forexes["dollarForex"]
    toToCurrency = toDollar * forexes["toCurrencyForex"]
    assert str(toToCurrency) in response_str

def test_convert_from_JPY_to_BRL(client):
    response = client.get('/convert?value=160&pair=JPYBRL')
    response_str = response.data.decode('utf-8')
    forexes = main.get_forex('JPY', 'BRL', 160)
    toDollar = 160 / forexes["dollarForex"]
    toToCurrency = toDollar * forexes["toCurrencyForex"]
    assert str(toToCurrency)[0:4] in response_str[0:4]
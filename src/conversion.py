
def convertCurrency(currency):

    currencies = {
        "Canadian Dollars": "CAD",
        "Argentina Pesos": "ARS",
        "Australian Dollars": "AUD",
        "Brazilian Real": "BRL",
        "Chile Pesos": "CLP",
        "Chinese Yuan": "CNY",
        "Hong Kong Dollars": "HKD",
        "Colombia Pesos": "COP",
        "Czech Republic": "CZK",
        "Danish Kroner": "DKK",
        "Egypt Pounds": "EGP",
        "Hungary Forint": "HUF",
        "Indian Rupees": "INR",
        "Indonesia Rupiahs": "IDR",
        "Malaysian": "MYR",
        "Mexican Pesos": "MXN",
        "Morocco Dirhams": "MAD",
        "Norwegian Kroner": "NOK",
        "Peru Nuevos": "PEN",
        "Philippines Pesos": "PHP",
        "Poland Zlotych": "PLN",
        "Qatar Riyals": "QAR",
        "Romania New Lei": "RON",
        "U.S. Dollars": "USD",
        "Saudi Arabia": "SAR",
        "Pounds": "GBP",  # Assuming British Pounds
        "Singapore Dollars": "SGD",
        "Swedish Kronor": "SEK",
        "Swiss Francs": "CHF",
        "United Arab": "AED",
        "Venezuela Bolivar": "VEF"
    }
    return currencies.get(currency)


def convertUnit(currency):

    currencies = {
        "M2": "SM"
    }
    return currencies.get(currency)

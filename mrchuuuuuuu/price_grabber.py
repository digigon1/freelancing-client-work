from binance.client import Client
import time
import datetime

symbol_list = ['ICX', 'NEO', 'ETH', 'BTC']
values = []

while True:
    command = input('Choose an option: ')

    if command == 'get':
        price_list = Client('', '').get_all_tickers()

        price_dict = {}
        for price in price_list:
            price_dict[price['symbol']] = price['price']

        btc_usd = float(price_dict['BTCUSDT'])

        # taken from
        # https://stackoverflow.com/questions/13890935/does-pythons-time-time-return-the-local-or-utc-timestamp
        current_values = [datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')]

        # Needed because you might be removing a value (python just jumps values otherwise)
        temp_list = symbol_list.copy()

        for symbol in temp_list:
            if symbol + 'USDT' in price_dict:
                print(symbol + 'USDT: ' + price_dict[symbol + 'USDT'])
                current_values.append(price_dict[symbol + 'USDT'])  # Adds gotten value to current value list
            elif symbol + 'BTC' in symbol_list:
                middle_value = float(price_dict[symbol + 'BTC'])
                print(symbol + 'USDT: ' + str(btc_usd * middle_value) + ' (calculated)')
                current_values.append(str(btc_usd * middle_value))  # Adds calculated value to current value list
            else:
                print(symbol + ' is not a valid symbol, removing')
                symbol_list.remove(symbol)

        values.append(current_values)

    elif command == 'exit':
        break

    # New from this line down
    elif command == 'add':  # Takes care of adding a new symbol to the list, resets stored values
        new_sym = input('Choose a new symbol: ')
        symbol_list.append(new_sym.upper())
        print('Symbol '+new_sym+' added')
        values = []

    elif command == 'remove':   # Takes care of adding a new symbol to the list, resets stored values
        sym = input('Choose a symbol to remove: ')
        try:    # Tries to remove
            symbol_list.remove(sym.upper())
            print('Symbol '+sym+' removed')
        except ValueError as e:     # If value does not currently exist in list, warn the user
            print('Symbol does not exist in current list')

    elif command == 'export':   # Allows exportation of values
        with open('values.csv', 'w') as f:
            f.write('time,' + ','.join(symbol_list) + '\n')
            for value_list in values:
                f.write(','.join(value_list) + '\n')
            print('Values fully exported')

    else:
        print('Invalid command, available: get, add, remove, exit')

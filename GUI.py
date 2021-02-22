import PySimpleGUI as Sg
import json
import sys
from web3 import Web3, HTTPProvider
import pandas as pd
from pandas import DataFrame
import easygui

Sg.theme('DarkAmber')

try:
    blockchain_address = 'http://127.0.0.1:9545'
    # Client instance to interact with the blockchain
    web3 = Web3(HTTPProvider(blockchain_address))
    # Set the default account (so we don't need to set the "from" for every transaction call)
    web3.eth.defaultAccount = web3.eth.accounts[0]
    # Deployed contract address (see `migrate` command output: `contract address`)
    deployed_contract_address = '0x4462D1eDc59E529aF9b8fa7D56c4c429BeA0cbf9'

    with open('node_modules/.bin/build/contracts/SplitAssets.json') as file:
        contract_json = json.load(file)  # load contract info as JSON
        # fetch contract's abi - necessary to call its functions
        contract_abi = contract_json['abi']
    # Fetch deployed contract reference
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
except:
    print("aa")
    easygui.msgbox("Error:\n" + str(sys.exc_info()[0]), title="Connecting Error to the Blockchain")
    exit(0)

create_list = [
    [
        Sg.Button("Create"),
        Sg.Text('Name:'),
        Sg.InputText(key="name", size=(15, 1)),
        Sg.Text('Value:'),
        Sg.InputText(key="value", size=(15, 1)),
        Sg.Text('Max Owners:'),
        Sg.InputText(key="max_owners", size=(15, 1)),
        Sg.Text('Keep Percent:'),
        Sg.InputText(key="keep_percent", size=(15, 1))
    ]
]

buy_list = [
    [
        Sg.Button("Buy"),
        Sg.Text('Percent: '),
        Sg.InputText(key="buy_percent", size=(15, 1)),
        Sg.Text('0/100')
    ]
]

sell_list = [
    [
        Sg.Button("Sell"),
        Sg.Text('Percent: '),
        Sg.InputText(key="sell_percent", size=(15, 1)),
        Sg.Text('0/0')
    ]
]

# --------------------------------------------------------
# Table
# create dataframe to simulate database with names and dates
"""
data = {'Name':  ['Joe Smith', 'Jason Leary','Bill Murray'],
        'Start Date': ['2019/10/01', '2019/11/01','2019/12/01'],
        'End Date': ['2019/10/15', '2019/11/15','2019/12/15']
        }
df = pd.DataFrame (data, columns = ['Name','Start Date','End Date'])
Data_Table = df.to_string()


header_list = [str(x) for x in range(len(data[0]))]
table_list = [
    [
        sg.Table(values=Data_Table, max_col_width=25, background_color='cyan', auto_size_columns=True, justification='right', alternating_row_color='blue', key='_table_', headings = header_list)
    ]
]
"""

"""
menu_def = [['Name', ['carWash', 'sopermercado']],
            ['City', ['Beer-Sheva', 'Tel-Aviv']],
            ['Price', ['1.5M', '2.3M']

             ]]
"""
table_list = [
    [

    ]
]
# All the stuff inside your window.
layout = [[Sg.Column(create_list)],
          [Sg.Column(buy_list)],
          [Sg.Column(sell_list)],
          # [Sg.Menu(menu_def)],
          [Sg.T('Table of the products:')],
          [Sg.In(key='inputRow', justification='right', size=(8, 1), pad=(1, 1), do_not_clear=True),
           Sg.In(key='inputCol', size=(8, 1), pad=(1, 1), justification='right', do_not_clear=True),
           Sg.In(key='current_value', size=(8, 1), pad=(1, 1), justification='right', do_not_clear=True)],
          [Sg.Button('Ok'), Sg.Button('Cancel')]]
"""
for i in range(20):
    inputs = [Sg.In(size=(18, 1), pad=(1, 1), justification='right', key=(i, j), do_not_clear=True) for j in range(10)]
    line = [Sg.Combo(('Customer ID', 'Customer Name', 'Customer Info')), inputs]
    layout.append(inputs)

form = Sg.FlexForm('Table', return_keyboard_events=True, grab_anywhere=False)
form.Layout(layout)
"""


# validate for the input, flag: 0 - Create, 1 = Buy, 2= Sell
def validate(args, flag):
    if flag == 0:
        if args['name'] != "" and args['value'].isnumeric() and args['max_owners'].isnumeric() and \
                int(args['max_owners']) > 0 and args['keep_percent'].isnumeric() and \
                0 < float(args['keep_percent']) < 100:
            return True
    elif flag == 1 and args['buy_percent'].isnumeric() and 0 < float(args['buy_percent']) < 100:
        return True
    elif flag == 2 and args['sell_percent'].isnumeric() and 0 < float(args['sell_percent']) < 100:
        return True
    return False


def create_assets(name, value, max_owners, keep_percent):
    contract.functions.uploadAsset(name, int(value), int(max_owners), int(keep_percent)).transact()
    print("\n-----------------\n")
    message = contract.functions.printAsset().call()
    print(message)


def buy_asset(percent):
    contract.functions.buyAsset(int(percent)).transact()
    assetInfo = contract.functions.getInfo().call()
    Sg.popup_quick_message("You've bought " + str(percent) + "% of the asset: " + str(assetInfo[0]) + " successfully.",
                           no_titlebar=True)


def sell_asset(percent):
    contract.functions.sellAsset(int(percent)).transact()
    assetInfo = contract.functions.getInfo().call()
    Sg.popup_quick_message("You've sold " + str(percent) + "% of the asset: " + str(assetInfo[0]) + " successfully.",
                           no_titlebar=True)


# Create the Window
window = Sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == Sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    elif event == 'Create':
        if validate(values, 0):
            create_assets(values['name'], values['value'], values['max_owners'], values['keep_percent'])
        else:
            Sg.popup_quick_message("Please Enter all of the fields to CREATE an asset", title="Input Error",
                                   location=window.current_location())
    elif event == 'Buy':
        if validate(values, 1):
            buy_asset(values['buy_percent'])
        else:
            Sg.popup_quick_message("Please Enter a valid percent to BUY an asset", title="Input Error",
                                   location=window.current_location())
    elif event == 'Sell':
        if validate(values, 2):
            sell_asset(values['sell_percent'])
        else:
            Sg.popup_quick_message("Please Enter a valid percent to SELL an asset", title="Input Error",
                                   location=window.current_location())
window.close()

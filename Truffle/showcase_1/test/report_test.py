from web3 import Web3
import json
import os.path
from datetime import datetime
from time import time
import subprocess

# ----- PARAMETERS -----

APPLICATION_ABI = ""
APPLICATION_ADD = ""

MONOLITH_ABI = ""
MONOLITH_ADD = ""

BUSINESS_ABI = ""
BUSINESS_ADD = ''

LOGGING_ABI = ""
LOGGING_ADD = ''

HTTP_ADD = ""
SENDER_LIST = ['', '']


# ----- REQUIREMENTS -----

web3 = Web3(Web3.HTTPProvider(HTTP_ADD))
print(web3.isConnected())

with open(APPLICATION_ABI) as f:
    compiled = json.load(f)
    application = web3.eth.contract(address=Web3.toChecksumAddress(APPLICATION_ADD), abi=compiled["abi"])

with open(MONOLITH_ABI) as f:
    compiled = json.load(f)
    monolith = web3.eth.contract(address=Web3.toChecksumAddress(MONOLITH_ADD), abi=compiled["abi"])

with open(BUSINESS_ABI) as f:
    compiled = json.load(f)
    business = web3.eth.contract(address=Web3.toChecksumAddress(BUSINESS_ADD), abi=compiled["abi"])

with open(LOGGING_ABI) as f:
    compiled = json.load(f)
    logging = web3.eth.contract(address=Web3.toChecksumAddress(LOGGING_ADD), abi=compiled["abi"])



print("\n\n ----- ONLY APPLICATION RUN ----- ")
print(web3.eth.wait_for_transaction_receipt( application.functions.SignUP('Andrea Rossi').transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.addProduct('Smartphone model K', 800, ["green","black"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.Create_Order(SENDER_LIST[0], "android_app").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.add_orderline(0,('Smartphone model K', 800, ["green","black"]),2).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.pick_item(0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.wrap_item(0,["Fragile","Box too large"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.deliveryItems(0,SENDER_LIST[0], 'Via Aldo Moro 1, Rome IT').transact({'from':SENDER_LIST[0]}) ))



print("\n\n ----- MONOLITH LOGGING RUN ----- ")
print(web3.eth.wait_for_transaction_receipt( monolith.functions.SignUP('Andrea Rossi').transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.addProduct('Smartphone model K', 800, ["green","black"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.Create_Order(SENDER_LIST[0], "android_app").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.add_orderline(0,('Smartphone model K', 800, ["green","black"]),2).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.pick_item(0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.wrap_item(0,["Fragile","Box too large"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.deliveryItems(0,SENDER_LIST[0], 'Via Aldo Moro 1, Rome IT').transact({'from':SENDER_LIST[0]}) ))



print("\n\n ----- DECOUPLED LOGGING RUN ----- ")
print(web3.eth.wait_for_transaction_receipt( business.functions.SignUP('Andrea Rossi').transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.addProduct('Smartphone model K', 800, ["green","black"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.Create_Order(SENDER_LIST[0], "android_app").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_orderline(0,('Smartphone model K', 800, ["green","black"]),2).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.pick_item(0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.wrap_item(0,["Fragile","Box too large"]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.deliveryItems(0,SENDER_LIST[0], 'Via Aldo Moro 1, Rome IT').transact({'from':SENDER_LIST[0]}) ))

print(" -- ")

print(web3.eth.wait_for_transaction_receipt( business.functions.SignUP('Mario Bianchi').transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.addProduct('Console model Y', 500, ["black"]).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.Create_Order(SENDER_LIST[1], "desktop_website_promo5").transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_orderline(1,('Console model Y', 500, ["black"]),1).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.pick_item(1).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.wrap_item(1,["Fragile"]).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.deliveryItems(1,SENDER_LIST[1], 'Via Ciceraucchio 2, Milan IT').transact({'from':SENDER_LIST[1]}) ))


print("\n\n ----- BYTECODE SIZES ----- ")
for abi_path in [APPLICATION_ABI,MONOLITH_ABI,BUSINESS_ABI,LOGGING_ABI]:
    cmd = "cat "+abi_path+" | jq -r '.deployedBytecode' | wc -c"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(abi_path," -> ",output)
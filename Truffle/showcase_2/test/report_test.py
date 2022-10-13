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


time_departure = int(time())
time_arrival = time_departure+ (1*60*60)
time_gate = int(time()) - (30*60)

print("\n\n ----- ONLY APPLICATION RUN ----- ")

print(web3.eth.wait_for_transaction_receipt( application.functions.add_flight( "Rome","Milan",time_departure,time_arrival,"Alitaly" ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.add_traveller( "Andrea", "Rossi", "Italy").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.add_luggage( 'blue', 20, SENDER_LIST[0]).transact({'from':SENDER_LIST[0]}) ))

print(web3.eth.wait_for_transaction_receipt( application.functions.buy_trip(['A'], ['19c'], [SENDER_LIST[0]]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.check_in( [0], 1, time_gate, SENDER_LIST[0], 0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.deliver_luggage( 0 , [0] ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.security_controls( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.start_flight( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( application.functions.cancel_flight( 0 ).transact({'from':SENDER_LIST[0]})  ))


print("\n\n ----- MONOLITH LOGGING RUN ----- ")
print(web3.eth.wait_for_transaction_receipt( monolith.functions.add_flight( "Rome","Milan",time_departure,time_arrival,"Alitaly" ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.add_traveller( "Andrea", "Rossi", "Italy").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.add_luggage( 'blue', 20, SENDER_LIST[0]).transact({'from':SENDER_LIST[0]}) ))

print(web3.eth.wait_for_transaction_receipt( monolith.functions.buy_trip(['A'], ['19c'], [SENDER_LIST[0]]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.check_in( [0], 1, time_gate, SENDER_LIST[0], 0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.deliver_luggage( 0 , [0] ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.security_controls( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.start_flight( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( monolith.functions.cancel_flight( 0 ).transact({'from':SENDER_LIST[0]})  ))

print("\n\n ----- DECOUPLED LOGGING RUN ----- ")
print(web3.eth.wait_for_transaction_receipt( business.functions.add_flight( "Rome","Milan",time_departure,time_arrival,"Alitaly" ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_traveller( "Andrea", "Rossi", "Italy").transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_luggage( 'blue', 20, SENDER_LIST[0]).transact({'from':SENDER_LIST[0]}) ))

print(web3.eth.wait_for_transaction_receipt( logging.functions.buy_trip(['A'], ['19c'], [SENDER_LIST[0]]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.check_in( [0], 1, time_gate, SENDER_LIST[0], 0).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.deliver_luggage( 0 , [0] ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.security_controls( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.start_flight( 0 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.cancel_flight( 0 ).transact({'from':SENDER_LIST[0]})  ))

print(" -- ")

print(web3.eth.wait_for_transaction_receipt( business.functions.add_flight( "Rome","Florence",time_departure+(24*60*60),time_arrival+(24*60*60),"Alitaly" ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_traveller( "Giorgio", "Bianchi", "Italy").transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( business.functions.add_luggage( 'green', 10, SENDER_LIST[1]).transact({'from':SENDER_LIST[1]}) ))

print(web3.eth.wait_for_transaction_receipt( logging.functions.buy_trip(['A','B'], ['19c','19b'], [SENDER_LIST[0], SENDER_LIST[1]]).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.check_in( [1,2], 1, time_gate+(24*60*60), SENDER_LIST[0], 1).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.check_in( [1,2], 1, time_gate+(24*60*60), SENDER_LIST[1], 1).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.deliver_luggage( 1 , [0] ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.deliver_luggage( 2 , [1]).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.security_controls( 1 ).transact({'from':SENDER_LIST[0]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.security_controls( 2 ).transact({'from':SENDER_LIST[1]}) ))
print(web3.eth.wait_for_transaction_receipt( logging.functions.start_flight( 1 ).transact({'from':SENDER_LIST[0]}) ))


print("\n\n ----- BYTECODE SIZES ----- ")
for abi_path in [APPLICATION_ABI,MONOLITH_ABI,BUSINESS_ABI,LOGGING_ABI]:
    cmd = "cat "+abi_path+" | jq -r '.deployedBytecode' | wc -c"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(abi_path," -> ",output)
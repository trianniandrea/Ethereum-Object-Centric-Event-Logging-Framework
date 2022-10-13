""" Grabber Module: Grab data from transaction and put into the logger """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import warnings

from web3 import Web3
import json
from datetime import datetime
import time
import pandas as pd
from tqdm import tqdm

from Logger import *

DEFAULTS = {'address': "0x0000000000000000000000000000000000000000", 'bool':False,
            'string': "", 'array': [], 
            'int':0, 'int8':0, 'int16':0, 'int24':0, 'int32':0, 'int40':0,'int48':0, 'int56':0, 'int64':0, 'int72':0, 'int80':0,
            'int88':0, 'int96':0, 'int104':0, 'int112':0, 'int120':0, 'int128':0, 'int136':0, 'int144':0, 'int152':0,
            'int160':0, 'int168':0, 'int176':0, 'int184':0, 'int192':0, 'int200':0, 'int208':0, 'int216':0, 'int224':0,
            'int232':0, 'int240':0, 'int248':0, 'int256':0,
            'uint':0, 'uint8':0, 'uint16':0, 'uint24':0, 'uint32':0, 'uint40':0, 'uint48':0, 'uint56':0, 'uint64':0, 'uint72':0,
            'uint80':0, 'uint88':0, 'uint96':0, 'uint104':0, 'uint112':0, 'uint120':0, 'uint128':0, 'uint136':0,
            'uint144':0, 'uint152':0, 'uint160':0, 'uint168':0, 'uint176':0, 'uint184':0, 'uint192':0, 'uint200':0,
            'uint208':0, 'uint216':0, 'uint224':0, 'uint232':0, 'uint240':0, 'uint248':0, 'uint256':0,
}


class Grabber(ABC):

    @abstractmethod
    def __init__(self) -> None:
        """_summary_
        """
        pass

    @abstractmethod
    def scan_network(self, min: int=0, max:int =0) -> None:
        """_summary_

        Args:
            min (int, optional): _description_. Defaults to 0.
            max (int, optional): _description_. Defaults to 0.
        """
        pass

    @abstractmethod
    def listen_network(self, min=0, max='latest', poll_interval=5) -> None:
        """_summary_

        Args:
            min (int, optional): _description_. Defaults to 0.
            max (str, optional): _description_. Defaults to 'latest'.
            poll_interval (int, optional): _description_. Defaults to 5.
        """
        pass

    @abstractmethod
    def connect(self, address: str) -> bool:
        """_summary_

        Args:
            address (str): _description_

        Returns:
            bool: _description_
        """
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        pass



class EthereumGrabber(Grabber):

    def __init__(self, w3:Web3.eth, event_schema:dict, object_schema:dict, contract:Web3.eth.Contract, logger:Logger) -> None:
        """_summary_

        Args:
            w3 (Web3.eth): _description_
            event_schema (dict): _description_
            object_schema (dict): _description_
            contract (Web3.eth.Contract): _description_
            logger (Logger): _description_
        """

        self.event_schema =  event_schema
        self.object_schema = object_schema
        self.w3 = w3
        self.contract = contract
        self.logger = logger

        # can be filled afterwards
        self.e2o_optionals = {}
        self.o2o_optionals = {}

        print("Connection -> ",self.check_connection())
        warnings.filterwarnings("ignore")



    @staticmethod
    def from_ABI(abi_path:str, contract_address:str, blockchain_address:str):
        """_summary_

        Args:
            abi_path (str): _description_
            contract_address (str): _description_
            blockchain_address (str): _description_

        Returns:
            _type_: _description_
        """

        importer = ABIImporter()
        importer.connect(blockchain_address)
        importer.load_contract(abi_path, contract_address)
        importer.get_event_schema(abi_path, flat = True)
        importer.get_object_schema(abi_path)
        return importer.build()


    def __str__(self) -> str:
        return "Grabber Object --> \n\n" + str(self.config)


    def connect(self, address:str):
        """_summary_

        Args:
            address (str): _description_

        Returns:
            _type_: _description_
        """
        return Web3(Web3.HTTPProvider(address))


    def check_connection(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.w3.isConnected()

    
    def load_contract(self, abi_path: str, address: str) -> Web3.eth.contract:
        """_summary_

        Args:
            abi_path (str): _description_
            address (str): _description_

        Returns:
            Web3.eth.contract: _description_
        """

        with open( abi_path) as f:
            compiled = json.load(f)

        return self.w3.eth.contract(address=address, abi=compiled["abi"])


    def scan_network(self, min: int=0, max: int=0) -> None:
        """_summary_

        Args:
            min (int, optional): _description_. Defaults to 0.
            max (int, optional): _description_. Defaults to 0.
        """

        self.logger.clear()
        event_names = [el['name'] for el in self.contract.abi if el['type'] == "event"]
        if max == 0 : max = self.w3.eth.get_block_number()
	
        for ib in tqdm(range(min, max+1)):
            b = self.w3.eth.get_block(ib, full_transactions=True)
            for tx in b['transactions']:
                if (self.contract.address == tx['to']):
                    receipt = self.w3.eth.getTransactionReceipt(tx['hash'])
                    for name in event_names:
                        events = getattr(self.contract.events, name)().processReceipt(receipt)
                        for event in events:
                            self.add_record(b, tx, event)


    def listen_network(self, min: int=0, max: int='latest', poll_interval: int=5) -> None:
        """_summary_

        Args:
            min (int, optional): _description_. Defaults to 0.
            max (int, optional): _description_. Defaults to 'latest'.
            poll_interval (int, optional): _description_. Defaults to 5.

        Returns:
            _type_: _description_
        """
        self.logger.clear()
        event_names = [el['name'] for el in self.contract.abi if el['type'] == "event"]
        contract_filter = self.w3.eth.filter({'fromBlock': min, 'toBlock': max, 'address':  self.contract.address})

        try:
            while True:
                for entry in contract_filter.get_new_entries():
                    b = self.w3.eth.get_block(entry['blockNumber'])
                    tx = self.w3.eth.get_transaction(entry['transactionHash'])
                    receipt = self.w3.eth.getTransactionReceipt(entry['transactionHash'])
                    for name in event_names:
                        events = getattr(self.contract.events, name)().processReceipt(receipt)
                        for e in events:
                            self.add_record(b, tx, e)
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            return None


    def add_record(self, block: dict, tx:dict, event:dict) -> None:
        """_summary_

        Args:
            block (dict): _description_
            tx (dict): _description_
            event (dict): _description_
        """

        # build event entry
        e = {"ocel:eid":str(int(len(self.logger.events))),
            "ocel:activity":event['event'],  
            "ocel:timestamp": str(datetime.fromtimestamp(block['timestamp'])),
            "ocel:vmap":{'from': tx['from'], "to": tx['to'], "value": tx['value']}}

        # add only if it is 'call_' type event
        if 'update_' not in e['ocel:activity']:
            self.logger.add_event(e)


        # print(event)

        for (obj_type,obj_def), (obj_name,obj_fields) in zip(self.event_schema[event['event']].items(), event['args'].items()):
            
            # print("OBJ_TYPE ->",obj_type)
            # print("OBJ_DEF ->",obj_def)
            # print("OBJ_NAME ->",obj_name)
            # print("OBJ_FIELDS ->",obj_fields)

            # if it is not an object at levelo depth 0, it is a field of the event.
            if  (obj_type not in self.object_schema.keys()):
                e['ocel:vmap'][obj_type] = obj_fields

            # it can be multiple object if *-N relation
            elif obj_type in self.object_schema.keys() and obj_def[1] == "array":
                for o_f in obj_fields:
                    self.add_object_relations(o_f, obj_type, obj_def, e)

            # or single object if *-1 relation
            elif obj_type in self.object_schema.keys():
                self.add_object_relations( obj_fields, obj_type, obj_def, e)


    
    def add_object_relations(self, obj_fields:tuple, obj_type:str, obj_def:list, e:dict):
        """_summary_

        Args:
            obj_fields (tuple): _description_
            obj_type (str): _description_
            obj_def (list): _description_
            e (dict): _description_
        """

        if type(obj_fields) is tuple:
            obj_fields = json.loads(json.dumps(obj_fields))

            objs,rels = self.get_object_relations(e, obj_fields, obj_type, obj_def)
            #print(objs,"\n",rels,"\n","-"*20)


            # Aggiungo gli oggetti: 
            for o in objs: 
                # gli oggetti senza id esplicito vengono aggiunti solo se non presenti
                if ('AutoID_' in o['ocel:oid']): 
                    if( self.logger.objects[(self.logger.objects['ocel:type']== o['ocel:type']) & (self.logger.objects['ocel:ovmap']== o['ocel:ovmap'])].empty):
                        self.logger.add_object(o)
                # gli oggetti con id esplicito vengono aggiunti solo se non presenti o presenti in maniera naive
                else:
                    if(o['ocel:oid'] not in self.logger.objects.index) or (o['ocel:ovmap'] != {}):
                        self.logger.add_object(o)


            # Aggiungo le relazioni
            for r in rels:
                if ('AutoID_' in r['ocel:oid1']):
                    o = [o for o in objs if o['ocel:oid'] == r['ocel:oid1']][0]
                    s = self.logger.objects[(self.logger.objects['ocel:type']== o['ocel:type']) & (self.logger.objects['ocel:ovmap']== o['ocel:ovmap'])]
                    r['ocel:oid1'] = s.index.tolist()[0]
                    
                if ('AutoID_' in r['ocel:oid2']):
                    o = [o for o in objs if o['ocel:oid'] == r['ocel:oid2']][0]
                    s = self.logger.objects[(self.logger.objects['ocel:type']== o['ocel:type']) & (self.logger.objects['ocel:ovmap']== o['ocel:ovmap'])]
                    r['ocel:oid2'] = s.index.tolist()[0]

                self.logger.add_o2o_rel(r, undirect=True)

            # Aggiungo solo se evento è di tipo 'call_'
            if 'update_' not in e['ocel:activity']:
                r = {"ocel:eid": e["ocel:eid"], "ocel:oid":objs[0]['ocel:oid']}
                self.logger.add_e2o_rel(r)
 


    def get_object_relations(self, e:dict, obj_fields:list, obj_type:str, obj_def:list, father: dict=None, count:int = 0):
        """_summary_

        Args:
            e (dict): _description_
            obj_fields (list): _description_
            obj_type (str): _description_
            obj_def (list): _description_
            father (dict, optional): _description_. Defaults to None.
            count (int, optional): _description_. Defaults to 0.
        """

        # arrays containing the final results
        objects = []
        rels = []

        # building the actual object
        o =  {'ocel:oid':'', 'ocel:type':obj_type, 'ocel:ovmap':{}}

        # fill the vmap
        obj_def = obj_def[0] if type (obj_def)==tuple else obj_def 
        for param_value, (param_name, param_type) in zip(obj_fields,obj_def):
            if not (param_name in self.object_schema.keys() or '_id' in param_name):
                o['ocel:ovmap'][param_name] =param_value
        
        # process the id
        if 'id' in o['ocel:ovmap']:  o['ocel:oid'] = obj_type+"_"+str(o['ocel:ovmap'].pop('id'))
        else:                        o['ocel:oid'] = obj_type+"_AutoID_"+str(len(self.logger.objects)+count)
        
        # Check for the type
        if 'ocel:type' not in o.keys():  o['ocel:type'] = "Unknown"
        

        # Finding nested relations or explicit references.
        if self.check_non_default(e, o['ocel:type'], father['ocel:type'] if father is not None else "",  obj_fields, obj_def, count):
            objects += [o]

            # add relations for nested objects respect father (caller)
            if father != None:
                rels += [{'ocel:oid1':father['ocel:oid'],'ocel:oid2':o['ocel:oid']}]

            # Recursive inductive step
            for param_value, (param_name, param_type) in zip(obj_fields,obj_def):

                # nested object relation
                if param_name in self.object_schema.keys():
                    new_objects, new_rels = self.get_object_relations( e, param_value, param_name, self.object_schema[param_name], o, count+len(objects) )
                    objects += new_objects
                    rels += new_rels
                
                # explicit reference
                elif '_id' in param_name:
                    param_value = param_value if type(param_value) == list else [param_value]
                    for id in param_value:
                        if (param_name[:-3]+str(id) in self.logger.objects.index) or (self.check_non_default(e, param_name[:-3], o['ocel:type'], [id], [(param_name, param_type)], count)): # or id = 0 ma id gia in log.obj
                            rels += [{'ocel:oid1':o['ocel:oid'],'ocel:oid2':param_name[:-2]+str(id)}]
                            objects += [{'ocel:oid':param_name[:-2]+str(id), 'ocel:type':param_name[:-3], 'ocel:ovmap':{}}]

        return objects,rels


    def check_non_default (self, e:dict, obj_type:str, father:str,  obj_fields:list, obj_def:list, count:int):
        """_summary_

        Args:
            e (dict): _description_
            obj_type (str): _description_
            father (str): _description_
            obj_fields (list): _description_
            obj_def (list): _description_
            count (int): _description_

        Returns:
            _type_: _description_
        """

        # controllo  optionals e2o
        if (count==0) and ((obj_type not in self.e2o_optionals.get(e['ocel:activity'],self.object_schema.keys()) \
                      and (obj_type[:-3] not in self.e2o_optionals.get(e['ocel:activity'],self.object_schema.keys())) )):
            return True

        # controllo optionals o2o
        if obj_type[:-3] not in  self.o2o_optionals.get(father,self.object_schema.keys()) and \
           obj_type not in  self.o2o_optionals.get(father,self.object_schema.keys()):
             return True

        # if optionals, non-default check is required
        for param_value, (param_name, param_type) in zip(obj_fields,obj_def):
            
            # array check
            if param_type[-2:] == "[]":
                return param_value != DEFAULTS["array"]

            # recursive step
            elif param_type not in DEFAULTS.keys(): 
                if self.check_non_default(e, param_type, obj_type, param_value, self.object_schema[param_type],count):
                    return True

            # if at least 1 parameter is not default, everything until now is not default.
            elif param_value != DEFAULTS[param_type]:
                return True

        return False





class ABIImporter():
    """_summary_
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self.w3 = None
        self.logger = Logger()
        self.event_schema = {}
        self.object_schema = {}
        self.contract = None

    def build (self) -> Logger:
        """_summary_

        Returns:
            Logger: _description_
        """
        res = EthereumGrabber(self.w3, self.event_schema, self.object_schema, self.contract, self.logger)
        self.reset()
        return res


    def connect(self, address:str):
        """_summary_

        Args:
            address (str): _description_
        """
        self.w3 = Web3(Web3.HTTPProvider(address))


    def load_contract(self, abi_path:str, address:str):
        """_summary_

        Args:
            abi_path (str): _description_
            address (str): _description_
        """
        with open( abi_path) as f:
            compiled = json.load(f)
        self.contract = self.w3.eth.contract(address=address, abi=compiled["abi"])


    def get_object_schema(self, abi_path:str):
        """_summary_

        Args:
            abi_path (str): _description_
        """

        event_schema = self.get_event_schema(abi_path, flat=False, save=False)
        obj_schema = {}

        for ev_name, ev_def in event_schema.items():
            for ev_obj, (ev_params,ev_types) in ev_def.items():

                if type(ev_params) == list:
                    obj_schema[ev_obj] = [ x if type(x) != dict  else  (list(x.keys())[0], list(x.keys())[0]) for x in ev_params] 

                    for x in ev_params:
                        if type(x) == dict:
                            obj_schema[list(x.keys())[0]] = list(x.values())[0]

        self.object_schema = obj_schema

                

    def extract_obj(self, param: dict, flat: bool=True) -> list[dict]:
        """_summary_

        Args:
            param (dict): _description_
            flat (bool, optional): _description_. Defaults to True.

        Returns:
            list[dict]: _description_
        """

        obj = []

        for p in param:
            if 'components' in p.keys():
                # se tolgo [ e ] diventa non ricorsivo, ottimo se voglio solo il primo livello.
                if flat:
                    obj += [(p['internalType'].split(".")[-1] , p['internalType'].split(".")[-1])]
                else:
                    obj += [{p['internalType'].split(".")[-1]:self.extract_obj(p['components'])}]
            else:
                obj += [(p['name'],p['internalType'])]

        return obj


    def get_event_schema(self, abi_path:str, flat:bool=True, save:bool=True) -> dict[list]:
        """_summary_

        Args:
            abi_path (str): _description_
            flat (bool, optional): _description_. Defaults to True.
            save (bool, optional): _description_. Defaults to True.

        Returns:
            dict[list]: _description_
        """

        with open( abi_path) as f:
            abi = json.load(f)['abi']

        events = [(el['name'],el['inputs']) for el in abi if el['type'] == "event"]
        params = {n:{} for n,e in events}

        for name, event in events:
            for param in event:
                if 'components' in param.keys():
                    #print('PROCESSANDO -> ',param['internalType'],"\n\n", param)

                    obj_name = param['internalType'].split(".")[-1]

                    if obj_name[-2:] == "[]":
                        params[name][obj_name[:-2]] = (self.extract_obj(param['components'], flat=flat), "array")
                    else:
                        params[name][obj_name] = (self.extract_obj(param['components'], flat=flat), obj_name)
                else:
                    params[name][param['name']]=(param['name'], param['internalType'])


        if save:  self.event_schema = params 

        return params








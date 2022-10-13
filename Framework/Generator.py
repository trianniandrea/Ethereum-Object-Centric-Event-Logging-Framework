""" Generator Module: contains utilities to automatically generate logging contract from manifest definition and business logic ABI """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod

import json



class ContractFactory():
    """_summary_
    """

    def __init__(self) -> None:
        pass

    def generate(self, abi_path:str, name:str, relations:dict, mode:str) -> dict:
        """_summary_

        Args:
            abi_path (str): _description_
            name (str): _description_
            relations (dict): _description_
            mode (str): _description_

        Returns:
            dict: _description_
        """

        self.load_source(abi_path)

        contract = self.get_license()+"\n\n"
        contract += "pragma solidity >="+ self.get_sol_version()+";\n\n"
        contract += "import \"./"+ self.get_import()+"\";\n\n"
        contract += "contract "+name+" is "+self.get_source_name()+" {\n\n"
        contract += "\tContract inner_contract; \n\n"   
        contract += self.add_events( relations )
        contract += "\n"+self.get_constructor()+"\n"
        contract += self.add_methods(mode, relations)

        return contract

    def to_file(self, contract:str, filename:str) -> None:
        """_summary_

        Args:
            contract (str): _description_
            filename (str): _description_
        """
        with open(filename+'.sol', 'w') as f:
            f.write(contract)


    def load_source(self, abi_path:str):
        with open(abi_path) as f:
            self.source = json.load(f)

    def get_source_name(self):
        return self.source["contractName"]

    def get_sol_version(self):
        return self.source["compiler"]["version"].split("+")[0]
    
    def get_license(self):
        return "// SPDX-License-Identifier: CC-BY-SA-4.0"

    def get_import(self):
        return self.source["sourcePath"].split("/")[-1]

    def get_constructor(self):
        return "\tconstructor (address add) {\n\t\tinner_contract = Contract(add); \n\t}\n"


    def get_methods(self):
        signatures = {}

        functions = [obj for obj in self.source['abi'] if obj['type'] == 'function' and obj["stateMutability"] == "nonpayable"]
        for func in functions:
            args = []; out = []

            # input parameters 
            for input in func['inputs']:
                if "tuple" in str(input['type']):
                     args += [(str(input['internalType']).split(".")[-1],str(input['name']), "memory", "object")] 
                else:
                    args += [(str(input['type']),str(input['name']), "memory" if "string" in str(input ['type']) or "[]" in str(input ['type']) else "", "field")] 
           
            # return parameters
            for output in func['outputs']:
                if "tuple" in str(output ['type']):
                     out += [(str(output ['internalType']).split(".")[-1],str(output ['name']),"memory","object")] 
                else:
                    out += [(str(output ['type']), str(output ['name']), "memory" if "string" in str(output ['type']) or "[]" in str(output ['type']) else "", "field")] 
            
            signatures[func['name']] = (args,out)

        return signatures


    def add_events(self, relations:dict):
        res = ""

        for e in self.get_methods().keys():
            rel = relations.get(e,[])
            params = ", ".join([ r[0]+" par"+str(i) if r[2] != "N" else r[0]+"[] par"+str(i) for i,r in enumerate(rel)  ]) +", " 
            res += "\tevent call_"+str(e)+"("+ params[:-2] +");\n"

        return res


    def add_methods(self, mode:str, relations:dict):
        res = ""

        methods = self.get_methods()
        for e in methods.keys():

            params = ", ".join([p[0]+" "+p[2]+ " "+p[1] for p in methods[e][0]])
            output = " returns ("+", ".join([p[0]+" "+p[2]+ " "+p[1]  for p in methods[e][1]]) + ")" if len(methods[e][1]) else ""

            if mode == "interface":
                signature = "\tfunction "+e+ " ("+ params +") external "+output+"{\n"
            if mode == "inheritance":
                signature = "\tfunction "+e+ " ("+ params +") public override "+output+"{\n"    

            params = ", ".join([p[1] for p in methods[e][0]])
            comment = "\t\t // Your code goes here ..\n"

            rel = relations.get(e,[])
            ev = ", ".join([ r[0]+"_par"+str(i) for i,r in enumerate(rel)  ]) +", " 

            body = "\t\tinner_contract."+e+" ("+ params +");\n"+comment+"\t\temit  call_"+str(e)+"("+ ev[:-2] +");"
            close = "\n\t}\n\n"

            method = signature + body + close
            res += method

        return res + "}\n"
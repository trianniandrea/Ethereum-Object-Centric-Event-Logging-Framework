""" App.py Module containing Main entrypoint and App class """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod

from Grabber import EthereumGrabber
from Graph import GraphFactory
from Generator import *
from Model import *
from Logger import *

filter = __import__("Filter")



class App():
    """_summary_
    """

    def __init__(self, model_path:str):
        """_summary_

        Args:
            model_path (str): _description_
        """

        self.model = Model.from_manifest(model_path)
        self.l = None 


    def execute_commands(self):
        """_summary_
        """

        for command in self.model.commands:
            print(command)

            if command['run_type'] == "RUN_GRAB":        self.run_grab(command)
            elif command['run_type'] == "RUN_IMPORT":    self.run_import(command)
            elif command['run_type'] == "RUN_EXPORT":    self.run_export(command)
            elif command['run_type'] == "RUN_PLOT":      self.run_plot(command)
            elif command['run_type'] == "RUN_GENERATE":  self.run_generate(command)
            elif command['run_type'] == "RUN_FILTER":    self.run_filter(command)
                

    def run_grab(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_

        Raises:
            Exception: _description_
            Exception: _description_
        """

        try: 
            connection = self.model.definitions['DEFINE_CONNECTION'][0]
            g = EthereumGrabber.from_ABI(contract_address= connection['contract_address'], 
                                         blockchain_address= connection['ip_address'], 
                                         abi_path= connection['abi_path'])
            
            # adding manifest infos for perfect handling of cardinality and default check
            opt = {r['event']:[] for r in self.model.definitions['DEFINE_E2O_REL']}
            for r in self.model.definitions['DEFINE_E2O_REL']:
                if r['min_card'] == '0':   opt[r['event']] += [r['object']]
            g.e2o_optionals = opt

            opt = {**{ r['o1']:[] for r in self.model.definitions['DEFINE_O2O_REL']}, \
                   **{ r['o2']:[] for r in self.model.definitions['DEFINE_O2O_REL']}}
            for r in self.model.definitions['DEFINE_O2O_REL']:
                if r['min_card_o1'] == '0':   opt[r['o1']] += [r['o2']]
                if r['min_card_o2'] == '0':   opt[r['o2']] += [r['o1']]                       
            g.o2o_optionals = opt

        except:
            raise Exception("Connection to blockchain failed.")

        if command['mode'] == "listen":
            g.listen_network(poll_interval = int(command['min_block/freq']))
            self.l = g.logger

        elif command['mode'] == "scan":
            g.scan_network(min = int(command['min_block/freq']), max = int(command['max_block']))  
            self.l = g.logger

        else:
            raise Exception("Grab mode not valid.")
    

    def run_import(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_

        Raises:
            Exception: _description_
            Exception: _description_
        """

        try:
            if "xml" in command['path']:     self.l = Logger.from_xml(command['path'])
            elif "json" in command['path']:  self.l = Logger.from_json(command['path'] )                     
            else:                            raise Exception("File format not supported")

        except:
            raise Exception("Error in log syntax!")


    def run_export(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_

        Raises:
            Exception: _description_
            Exception: _description_
            Exception: _description_
        """

        if self.l is None: 
            raise Exception("To export, you have first to grab or import logs.")

        try:
            if command['format'] == "xml":
                self.l.to_xml(filename=command['filename'], relations=True if command['o2o_rel_flag']=="true" else False)
            elif command['format'] == "json":
                self.l.to_json(filename=command['filename'], relations=True if command['o2o_rel_flag']=="true" else False)                     
            else:
                raise Exception("File format not supported")

        except:
            raise Exception("No data to export, grab first!")


    def run_plot(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_

        Raises:
            Exception: _description_
        """

        if self.l is None: 
            raise Exception("To plot, you have first to grab or import logs.")

        f = GraphFactory()
        area = [area['items'] for area in self.model.definitions['DEFINE_AREA'] if area['id'] == command['area']][0]
        
        if command['type'] == "id":
            e2o_id = f.build_e2o_id_graph(self.l)
            #e2o_id.plot("./output/plot/"+command['path']+"_area_"+command['area']+"_e2o_id",area)
            o2o_id = f.build_o2o_id_graph(self.l)
            #o2o_id.plot("./output/plot/"+command['path']+"_area_"+command['area']+"_o2o_id",area)
            e2o_id.merge(o2o_id).plot(command['path']+"_area_"+command['area']+"_o2o_e2o_id" ,area, command['theme'])

        elif command['type'] == "type":
            o2o_type = f.build_o2o_type_graph(self.l)
            #o2o_type.plot("./output/plot/"+command['path']+"_area_"+command['area']+"_o2o_type",area)
            e2o_type = f.build_e2o_type_graph(self.l)
            #e2o_type.plot("./output/plot/"+command['path']+"_area_"+command['area']+"_e2o_type",area)
            e2o_type.merge( o2o_type ).plot(command['path']+"_area_"+command['area']+"_o2o_e2o_type",area, command['theme'])


    def run_generate(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_
        """

        cg = ContractFactory()

        rel = { r['event']:[] for r in self.model.definitions['DEFINE_E2O_REL']}
        for r in self.model.definitions['DEFINE_E2O_REL']:
            rel[r['event']] += [(r['object'], r['min_card'], r['max_card'])]

        cg.to_file(cg.generate(self.model.definitions['DEFINE_LOGIC'][0]['path'], command['filename'].split("/")[-1], rel, command['mode']), command['filename'])


    def run_filter(self, command:dict):
        """_summary_

        Args:
            command (dict): _description_
        """
        constraints = [getattr(filter, c['type']+"Constraint")(c['activity1'], c['activity2'], c['area']) for c in self.model.definitions['DEFINE_CONSTRAINT']]
        areas = {area['id']:area['items'] for area in self.model.definitions['DEFINE_AREA']}
        f = filter.Filter(self.l, constraints, areas)
        f.check_constraints()



# [!] Main entrypoint
if __name__ == "__main__":
    m = App(sys.argv[1]) #path to manifest
    m.execute_commands()

""" Model module """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
import sys


class Model():
    """_summary_
    """

    def __init__(self, definitions:dict, commands:list):
        """_summary_

        Args:
            definitions (dict): _description_
            commands (list): _description_
        """
        self.commands = commands
        self.definitions = definitions


    @classmethod
    def from_manifest(cls, path_manifest:str):
        """_summary_

        Args:
            path_manifest (str): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """

        define_commands = {}
        run_commands = []

        with open(path_manifest, "r") as f:
            manifest = f.read()
        
        for i, command in enumerate(manifest.split("\n")):

            # riga di commento
            if len([par for par in command.split(" ") if par!= ""]) == 0 or command[0] == "%": 
                continue
            
            # define commands ..
            elif "DEFINE_CONNECTION" in command:
                command_par = [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row","id", "ip_address", "contract_address", "abi_path"]
                define_commands['DEFINE_CONNECTION'] = define_commands.get('DEFINE_CONNECTION',[]) + [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "DEFINE_AREA" in command:
                command_par =  [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "id", "items"]
                define_commands['DEFINE_AREA'] = define_commands.get('DEFINE_AREA',[]) + [{"row":command_par[0], "id": command_par[1], "items":command_par[2:] }]
            elif "DEFINE_CONSTRAINT" in command:
                command_par =  [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "type", "activity1", "activity2","area"]
                define_commands['DEFINE_CONSTRAINT'] = define_commands.get('DEFINE_CONSTRAINT',[]) + [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "DEFINE_LOGIC" in command:
                command_par =  [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "path", "mode"]
                define_commands['DEFINE_LOGIC'] = define_commands.get('DEFINE_LOGIC',[]) + [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "DEFINE_E2O_REL" in command:
                command_par =  [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row","event", "object", "min_card","max_card"]
                define_commands['DEFINE_E2O_REL'] = define_commands.get('DEFINE_E2O_REL',[]) + [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "DEFINE_O2O_REL" in command:
                command_par =  [i] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "o1", "o2", "min_card_o1", "max_card_o1", "min_card_o2", "max_card_o2"]
                define_commands['DEFINE_O2O_REL'] = define_commands.get('DEFINE_O2O_REL',[]) + [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            
            # run commands ..
            elif "RUN_GENERATE" in command:
                command_par =  [i,"RUN_GENERATE" ] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "run_type", "filename", "mode"]
                run_commands += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "RUN_PLOT" in command:
                command_par =  [i, "RUN_PLOT"] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row","run_type", "type", "area", "path", "theme"]
                run_commands  += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "RUN_GRAB" in command:
                command_par =  [i, "RUN_GRAB"] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row","run_type", "mode", "min_block/freq", "max_block"][:max(3,len(command_par))]
                run_commands += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "RUN_EXPORT" in command:
                command_par =  [i, "RUN_EXPORT"] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row","run_type", "format", "filename", "o2o_rel_flag"]
                run_commands += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "RUN_FILTER" in command:
                command_par =  [i, "RUN_FILTER"] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "run_type"]
                run_commands += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            elif "RUN_IMPORT" in command:
                command_par =  [i, "RUN_IMPORT"] + [par for par in command.split(" ")[1:] if par!= ""]
                command_schema = ["row", "run_type", "path"]
                run_commands += [{par_name: par_value for par_name, par_value in zip(command_schema, command_par)}]
            
            # comando non riconosciuto
            else:
                raise Exception("Invalid Command at line: "+str(i+1))
        
        return cls(define_commands, run_commands)


    def __str__(self) -> str:
        return str(self.definitions)+str(self.commands)


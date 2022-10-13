""" Logger Module """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any 

import json
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime
import copy
import pandas as pd



class Logger():
    """_summary_
    """

    def __init__(self, events: pd.DataFrame=None, objects: pd.DataFrame=None, e2o_rel: pd.DataFrame=None, o2o_rel: pd.DataFrame=None) -> None:
        """_summary_

        Args:
            types (dict[list[str]]): _description_
            events (pd.DataFrame, optional): _description_. Defaults to None.
            objects (pd.DataFrame, optional): _description_. Defaults to None.
            e2o_rel (pd.DataFrame, optional): _description_. Defaults to None.
            o2o_rel (pd.DataFrame, optional): _description_. Defaults to None.
        """

        self.events = pd.DataFrame(columns=["ocel:eid","ocel:activity","ocel:timestamp","ocel:vmap"]) if events is None else events
        self.objects = pd.DataFrame(columns=["ocel:oid","ocel:type",'ocel:ovmap']) if objects is None else objects
        self.e2o_rel = pd.DataFrame(columns=["ocel:eid","ocel:oid"]) if e2o_rel is None else e2o_rel
        self.o2o_rel = pd.DataFrame(columns=["ocel:oid1","ocel:oid2"]) if o2o_rel is None else o2o_rel
        self.events = self.events.set_index('ocel:eid') #if events is None else events
        self.objects = self.objects.set_index('ocel:oid') #if objects is None else objects


    def clear(self) -> None:
        """ clear the log """
        self = Logger()


    def add_event(self, e: dict, duplicate: bool=False) -> None:
        """_summary_

        Args:
            e (dict): _description_
            duplicate (bool, optional): _description_. Defaults to False.
        """
        self.events = self.events.append(e, ignore_index=True)


    def add_object(self, o: dict, duplicate: bool=False) -> None:
        """_summary_

        Args:
            o (dict): _description_
            duplicate (bool, optional): _description_. Defaults to False.
        """
        o = copy.copy(o)
        id = o.pop('ocel:oid')
        self.objects.loc[id] = o


    def add_e2o_rel(self, r:dict, duplicate: bool=False) -> None:
        """_summary_

        Args:
            r (dict): _description_
            duplicate (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """

        if not duplicate:
            if ((self.e2o_rel['ocel:eid'] == r["ocel:eid"]) & (self.e2o_rel['ocel:oid'] == r["ocel:oid"])).any():
                return None

        self.e2o_rel = self.e2o_rel.append(r, ignore_index=True)


    def add_o2o_rel(self, r:dict, duplicate: bool=False, undirect: bool=False ) -> None:
        """_summary_

        Args:
            r (dict): _description_
            duplicate (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if not duplicate:
            if ((self.o2o_rel['ocel:oid1'] == r["ocel:oid1"]) & (self.o2o_rel['ocel:oid2'] == r["ocel:oid2"])).any():
                return None

        if undirect:
            self.add_o2o_rel({"ocel:oid1":r["ocel:oid2"], "ocel:oid2":r['ocel:oid1']},undirect=False)

        self.o2o_rel = self.o2o_rel.append(r, ignore_index=True)
        

    def __str__(self) -> str:
        return "Logger Object -->\n " + str(self.events) +"\n"+ str(self.objects)+"\n"+ str(self.e2o_rel) + "\n"+str(self.o2o_rel )

    def __len__(self) -> int:
        return len(self.events.index)

    # for iterator pattern
    def __getitem__(self, key:str) -> pd.Series:
        return self.events.loc[key]

    # Convert to std OCEL
    def to_std_OCEL(self, inplace=False):
        l = self if inplace else copy.deepcopy(self)
        
        l.o2o_rel = None
        l.events.drop(l.events[~l.events.index.isin(l.e2o_rel['ocel:eid'])].index, inplace=True)
        l.objects.drop(l.objects[~l.objects.index.isin(l.e2o_rel['ocel:oid'])].index, inplace=True)
        
        return l


    def to_xml(self, filename: str, relations: bool=False) -> None:
        """_summary_

        Args:
            filename (str): _description_
            relations (bool, optional): _description_. Defaults to False.
        """
        l = self if relations else self.to_std_OCEL(inplace=False)

        builder = XMLExporter()
        builder.add_event_global()
        builder.add_object_global()
        builder.add_version("custom" if relations else "1.0")
        builder.add_ordering()
        builder.add_attribute_names( [k for i,vmap in enumerate(l.events["ocel:vmap"]) for k in vmap.keys()] )
        builder.add_attribute_names( [k for i,ovmap in enumerate(l.objects["ocel:ovmap"]) for k in ovmap.keys()] )
        builder.add_object_types(list(l.objects['ocel:type'].unique()))
        builder.add_events(l.events, l.e2o_rel)
        builder.add_objects(l.objects, l.o2o_rel)
        builder.to_file(builder.build(), filename)
        
    def to_json(self, filename: str, relations:bool =False) -> None:
        """_summary_

        Args:
            filename (str): _description_
            relations (bool, optional): _description_. Defaults to False.
        """
        l = self if relations else self.to_std_OCEL(inplace=False)

        builder = JSONExporter()
        builder.add_event_global()
        builder.add_object_global()
        builder.add_version("custom" if relations else "1.0")
        builder.add_ordering()

        builder.add_attribute_names( [k for i,vmap in enumerate(l.events["ocel:vmap"]) for k in vmap.keys()] )
        builder.add_attribute_names( [k for i,ovmap in enumerate(l.objects["ocel:ovmap"]) for k in ovmap.keys()] )
        builder.add_object_types(list(l.objects['ocel:type'].unique()))

        builder.add_events(l.events, l.e2o_rel)
        builder.add_objects(l.objects, l.o2o_rel)

        builder.to_file(builder.build(), filename)


    @staticmethod
    def from_json(filepath: str) -> Logger:
        """_summary_

        Args:
            filepath (str): _description_

        Returns:
            Logger: _description_
        """
        return JSONImporter().produce(filepath)

    @staticmethod
    def from_xml(filepath: str) -> Logger:
        """_summary_

        Args:
            filepath (str): _description_

        Returns:
            Logger: _description_
        """
        return XMLImporter().produce(filepath)


    def concatenate(self, other:Logger, inplace = True):
        """_summary_

        Args:
            other (Logger): _description_
            inplace (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """

        l = self if inplace else Logger({})

        l.types = {**self.types, **other.types}
        l.events =  pd.concat([self.events, other.events], ignore_index=True)
        l.objects = pd.concat([self.objects, other.objects], ignore_index=True)
        l.o2o_rel = pd.concat([self.o2o_rel, other.o2o_rel], ignore_index=True)
        l.e2o_rel = pd.concat([self.e2o_rel, other.e2o_rel], ignore_index=True)

        return l


    # shortcut operator to concatenate 2 log
    def __add__(self, other):
        return self.concatenate(other, inplace = False)

    # shortcut operator to inplace concatenate 2 log
    def __iadd__(self, other):
        return self.concatenate(other, inplace=True)



class OCELImporter(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def produce(filepath: str) -> Logger:
        """_summary_

        Args:
            filepath (str): _description_

        Returns:
            Logger: _description_
        """
        pass



class JSONImporter(OCELImporter):
    """_summary_

    Args:
        OCELImporter (_type_): _description_
    """

    def __init__(self) -> None:
        pass

    def produce (self, filepath:str ) -> Logger:
        with open(filepath) as fp:
            disk_json = json.load(fp)

        events = self.add_events(disk_json)
        objects = self.add_objects(disk_json)
        e2o_rel = self.add_e2o_relations(disk_json)
        o2o_rel = self.add_o2o_relations(disk_json)

        return Logger(events, objects, e2o_rel, o2o_rel)


    def add_object_types(self, d:dict) -> dict:
        pass


    def add_events(self, d:dict) -> pd.DataFrame:

        events = pd.DataFrame(columns=["ocel:eid","ocel:activity","ocel:timestamp","ocel:vmap"])
        events = events.set_index('ocel:eid')

        for k,v in d["ocel:events"].items():
            record = copy.deepcopy(v)
            record["ocel:eid"]=k
            del record["ocel:omap"]
            events = events.append(record, ignore_index=True)

        return events


    def add_objects(self, d: dict) -> pd.DataFrame:

        objects = pd.DataFrame(columns=["ocel:oid","ocel:type",'ocel:ovmap'])
        objects = objects.set_index('ocel:oid')

        for k,v in d["ocel:objects"].items():
            record = copy.deepcopy(v)
            record["ocel:oid"]=k
            if "custom:rmap" in record.keys(): del record["custom:rmap"]
            objects = objects.append(record, ignore_index=True)

        return objects


    def add_o2o_relations(self, d: dict) -> pd.DataFrame:

        o2o_rel = pd.DataFrame(columns=["ocel:oid1","ocel:oid2"])

        for oid, o in d["ocel:objects"].items():
            if 'custom:rmap' in o.keys():
                for r in o['custom:rmap']:
                    o2o_rel = o2o_rel.append({'ocel:oid1':oid,'ocel:oid2':r}, ignore_index=True)

        return o2o_rel


    def add_e2o_relations(self, d: dict) -> pd.DataFrame:

        e2o_rel = pd.DataFrame(columns=["ocel:eid","ocel:oid"])

        for eid, e in d["ocel:events"].items():
            for oid in e['ocel:omap']:
                e2o_rel = e2o_rel.append({'ocel:eid':eid,'ocel:oid':oid}, ignore_index=True)

        return e2o_rel


  
class XMLImporter(OCELImporter):
    """_summary_

    Args:
        OCELImporter (_type_): _description_
    """

    def __init__(self) -> None:
        pass

    def produce (self, filepath: str) -> Logger:
        xml_log = ET.parse(filepath)
        xml_log = xml_log.getroot()
        events = self.add_events(xml_log)
        objects = self.add_objects(xml_log)
        e2o_rel = self.add_e2o_relations(xml_log)
        o2o_rel = self.add_o2o_relations(xml_log)
        return Logger(events, objects, e2o_rel, o2o_rel)


         
    def check_node(self, root:ET.Element, tag:str, ks: list[str], vs: list[str], first: bool=True) -> list[ET.Element]:
        """_summary_

        Args:
            root (ET.Element): _description_
            tag (str): _description_
            ks (list[str]): _description_
            vs (list[str]): _description_
            first (bool, optional): _description_. Defaults to True.

        Returns:
            list[ET.Element]: _description_
        """
        item_list = []

        for item in root.iter(tag=tag):
            flag = True
            for k,v in zip(ks, vs):
                if item.attrib[k]!=v:
                    flag= False
                    break
            if flag == True: 
                item_list+=[item]

        return None if len(item_list)==0 else item_list[0] if first else item_list


    def add_object_types(self, root: ET.Element) -> dict:
        pass


    def add_events(self, root: ET.Element) -> pd.DataFrame:

        events = pd.DataFrame(columns=["ocel:eid","ocel:activity","ocel:timestamp","ocel:vmap"])
        events = events.set_index('ocel:eid')

        for ev in root.iter('event'):
            record = { "ocel:"+el.attrib['key'] : el.attrib.get('value',{}) for el in ev}
            record["ocel:eid"] = record.pop("ocel:id")
            del record['ocel:omap']
            for p in self.check_node(ev, 'list', ['key'],['vmap']):
                record['ocel:vmap'][p.attrib['key']]= p.attrib['value']
            events = events.append(record, ignore_index=True)

        return events

    def add_objects(self, root: ET.Element) -> pd.DataFrame:

        objects = pd.DataFrame(columns=["ocel:oid","ocel:type",'ocel:ovmap'])
        objects = objects.set_index('ocel:oid')

        for obj in root.iter('object'):
            record = { "ocel:"+el.attrib['key'] : el.attrib.get('value',{}) for el in obj}
            record["ocel:oid"] = record.pop("ocel:id")
            del record['custom:rmap']
            for p in self.check_node(obj, 'list', ['key'],['ovmap']):
                record['ocel:ovmap'][p.attrib['key']]= p.attrib['value']
            objects = objects.append(record, ignore_index=True)

        return objects


    def add_o2o_relations(self, root: ET.Element) -> pd.DataFrame:

        o2o_rel = pd.DataFrame(columns=["ocel:oid1","ocel:oid2"])

        for obj in root.iter('object'):
            id1 = self.check_node(obj, 'string', ['key'],['id']).attrib['value']
            for r_obj in self.check_node(obj, 'list', ['key'],['rmap']):
                o2o_rel = o2o_rel.append({'ocel:oid1':id1,'ocel:oid2':r_obj.attrib['value']}, ignore_index=True)

        return o2o_rel


    def add_e2o_relations(self, root: ET.Element) -> pd.DataFrame:
 
        e2o_rel = pd.DataFrame(columns=["ocel:eid","ocel:oid"])

        for ev in root.iter('event'):
            eid = self.check_node(ev, 'string', ['key'],['id']).attrib['value']
            for obj in self.check_node(ev, 'list', ['key'],['omap']):
                e2o_rel = e2o_rel.append({'ocel:eid':eid,'ocel:oid':obj.attrib['value']}, ignore_index=True)

        return e2o_rel





class OCELExporter(ABC):
    """
    The Builder interface specifies methods for creating the different parts of
    the Product objects.
    """

    @abstractmethod
    def build (self) -> None:
        """_summary_
        """
        pass

    @abstractmethod
    def to_file(self, log, filename: str) -> None:
        """_summary_

        Args:
            log (_type_): _description_
            filename (str): _description_
        """
        pass

    @abstractmethod
    def add_version(self, version="1.0") -> None:
        pass

    @abstractmethod
    def add_ordering(self, criteria="timestamp") -> None:
        pass

    @abstractmethod
    def add_event_global(self) -> None:
        pass

    @abstractmethod
    def add_object_global(self) -> None:
        pass

    @abstractmethod
    def add_attribute_names(self, att_names: list[str]) -> None:
        pass

    @abstractmethod
    def add_object_types(self, obj_types: list[str]) -> None:
        pass

    @abstractmethod
    def add_events(self, events: pd.DataFrame, e2o_rel: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def add_objects(self, o2o_rel: pd.DataFrame=None) -> None:
        pass





class JSONExporter(OCELExporter):
    """_summary_

    Args:
        OCELExporter (_type_): _description_
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.json_log = {}
        self.json_log["ocel:global-log"] = {}


    def build(self) -> dict:

        res = self.json_log
        self.reset()
        return res

    def to_file(self, log:dict, filename:str) -> None:
        with open(filename+'.jsonocel', 'w') as f:
            json.dump(log , f, indent=4)


    def add_version(self, version="1.0") -> None:
        self.json_log["ocel:global-log"].update({"ocel:version":version})

    def add_ordering(self, criteria="timestamp") -> None:
        self.json_log["ocel:global-log"].update({"ocel:ordering":criteria})

    def add_event_global(self) -> None:
        self.json_log["ocel:global-event"] = {"ocel:activity":"__INVALID__"}
            
    def add_object_global(self) -> None:
        self.json_log["ocel:global-object"] = {"ocel:type":"__INVALID__"}

    def add_attribute_names(self, att_names: list[str]) -> None:
        att_names = list(set( att_names + self.json_log["ocel:global-log"].get("ocel:attribute-names",[]) ))
        self.json_log["ocel:global-log"].update({"ocel:attribute-names":att_names})

    def add_object_types(self, obj_types: list[str]) -> None:
        self.json_log["ocel:global-log"].update({"ocel:object-types":obj_types})

    def add_events(self, events: pd.DataFrame, e2o_rel: pd.DataFrame) -> None:
        if "ocel:eid" in events.columns:
             events = events.set_index("ocel:eid", drop=True)
        self.json_log['ocel:events'] = events.to_dict(orient="index")

        for id, e in self.json_log['ocel:events'].items():
            e['ocel:omap'] = e2o_rel.loc[e2o_rel['ocel:eid'] == id]["ocel:oid"].tolist()
                
    def add_objects(self, objects: pd.DataFrame, o2o_rel: pd.DataFrame=None) -> None:
        if "ocel:oid" in objects.columns:
            objects = objects.set_index("ocel:oid", drop=True)
        self.json_log['ocel:objects'] = objects.to_dict(orient="index")

        if o2o_rel is not None:
            for id, o in self.json_log['ocel:objects'].items():
                o['custom:rmap'] = o2o_rel.loc[o2o_rel['ocel:oid1'] == id]["ocel:oid2"].tolist()
                #+ \o2o_rel.loc[o2o_rel['ocel:oid2'] == id]["ocel:oid1"].tolist()



class XMLExporter(OCELExporter):
    """_summary_

    Args:
        OCELExporter (_type_): _description_
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """_summary_
        """
        self.root = ET.Element("log")
        ET.SubElement(self.root, "global",  scope="event")
        ET.SubElement(self.root, "global",  scope="object")
        ET.SubElement(self.root, "global",  scope="log")
        ET.SubElement(self.root, "events")
        ET.SubElement(self.root, "objects")     


    def build(self) -> ET.ElementTree:
        tree = ET.ElementTree(self.root)
        self.reset()
        return tree


    def _pretty_print(self, current: ET.Element, parent: ET.Element=None, index: int=-1, depth: int=0):
        """_summary_

        Args:
            current (ET.Element): _description_
            parent (ET.Element, optional): _description_. Defaults to None.
            index (int, optional): _description_. Defaults to -1.
            depth (int, optional): _description_. Defaults to 0.
        """
        for i, node in enumerate(current):
            self._pretty_print(node, current, i, depth + 1)

        if parent is not None:
            if index == 0:
                parent.text = '\n' + ('\t' * depth)
            else:
                parent[index - 1].tail = '\n' + ('\t' * depth)
            if index == len(parent) - 1:
                current.tail = '\n' + ('\t' * (depth - 1))


    def check_node(self, root: ET.Element, tag: str, ks: list[str], vs: list[str], first: bool=True):
        """_summary_

        Args:
            root (ET.Element): _description_
            tag (str): _description_
            ks (list[str]): _description_
            vs (list[str]): _description_
            first (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        item_list = []

        for item in root.iter(tag=tag):
            flag = True
            for k,v in zip(ks, vs):
                if item.attrib[k]!=v:
                    flag= False
                    break
            if flag == True: 
                item_list+=[item]

        return None if len(item_list)==0 else item_list[0] if first else item_list



    def to_file(self, tree:ET.ElementTree, filename: str):
        self._pretty_print(tree.getroot())
        tree.write(filename+".xmlocel", encoding="utf-8")

    def add_version(self, version="1.0") -> None:
        e = self.check_node(self.root, 'global', ['scope'], ['log'])
        ET.SubElement(e, "string", key="ocel:version", value=version)

    def add_ordering(self, criteria="timestamp") -> None:
        e = self.check_node(self.root, 'global', ['scope'], ['log'])
        ET.SubElement(e, "string", key="ocel:ordering", value=criteria)

    def add_event_global(self) -> None:
        e = self.check_node(self.root, 'global', ['scope'], ['event'])
        ET.SubElement(e, "string", key="activity", value="__INVALID__")

    def add_object_global(self) -> None:
        o = self.check_node(self.root, 'global', ['scope'], ['object'])
        ET.SubElement(o, "string", key="type", value="__INVALID__")

    def add_attribute_names(self, att_names: list[str]) -> None:
        att_names = list(set( att_names ))

        r = self.check_node(self.root, 'global', ['scope'], ['log'])
        alist = self.check_node(r, 'list', ['key'], ['attribute-names'])
        if alist is None:
            alist = ET.SubElement(r, "list", key="attribute-names")

        for n in att_names:
            if self.check_node(alist, 'string', ['value'], [n]) is None:
                ET.SubElement(alist, "string", key="attribute-name", value=n)


    def add_object_types(self, obj_types: list[str]) -> None:

        r = self.check_node(self.root, 'global', ['scope'], ['log'])
        list = self.check_node(r, 'list', ['key'], ['object-types'])
        if list is None:
            list = ET.SubElement(r, "list", key="object-types")

        for o in obj_types:
            ET.SubElement(list, "string", key="object-type", value=o)


    def add_events(self, events: pd.DataFrame, e2o_rel: pd.DataFrame) -> None:
        r = self.check_node(self.root, 'events', [], [])
        
        if "ocel:eid" in events.columns:
             events = events.set_index("ocel:eid", drop=True)
        list_events = events.to_dict(orient="index")

        for id, e in list_events.items():
            e['ocel:omap'] = e2o_rel.loc[e2o_rel['ocel:eid'] == id]["ocel:oid"].tolist()
        
        for id, ev in list_events.items():
            e = ET.SubElement(r, "event")
            ET.SubElement(e, "string", key="id", value=str(int(id)))
            ET.SubElement(e, "string", key="activity", value=ev['ocel:activity'])
            ET.SubElement(e, "string", key="timestamp", value=ev['ocel:timestamp'])
            l = ET.SubElement(e, "list", key="omap")
            for o in ev['ocel:omap']:
                ET.SubElement(l, "string", key="object-id", value=str(o))
            l = ET.SubElement(e, "list", key="vmap")
            for k,v in ev['ocel:vmap'].items():
                ET.SubElement(l, "string", key=k, value=str(v))


                
    def add_objects(self, objects: pd.DataFrame, o2o_rel: pd.DataFrame=None) -> None:
        r = self.check_node(self.root, 'objects', [], [])

        if "ocel:oid" in objects.columns:
            objects = objects.set_index("ocel:oid", drop=True)
        list_objects  = objects.to_dict(orient="index")

        if o2o_rel is not None:
            for id, o in list_objects.items():
                o['custom:rmap'] = o2o_rel.loc[o2o_rel['ocel:oid1'] == id]["ocel:oid2"].tolist() 
                
        for id, ob in list_objects.items():
            o = ET.SubElement(r, "object")
            ET.SubElement(o, "string", key="id", value=str(id))
            ET.SubElement(o, "string", key="type", value=ob['ocel:type'])
            l = ET.SubElement(o, "list", key="ovmap")
            for k,v in ob['ocel:ovmap'].items():
                ET.SubElement(l, "string", key=k, value=str(v))
            if o2o_rel is not None:
                l = ET.SubElement(o, "list", key="rmap")
                for o_r in ob['custom:rmap']:
                    ET.SubElement(l, "string", key=str(id), value=str(o_r))



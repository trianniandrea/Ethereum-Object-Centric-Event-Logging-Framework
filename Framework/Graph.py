""" Graph Module: custom graph data structure that allow to translate log to trace """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

import copy
import enum
from pyvis.network import Network

from Logger import *


class NodeType(enum.Enum):
    """ Enum for different (graph) node type  """
    object_type = 1
    object_id = 2
    event_type = 3 
    event_id = 4

# Global constant
PLOT_OPT = """const options = {"nodes": {"borderWidth": 3,"borderWidthSelected": 6,"font": {"face": "verdana"}},"edges": {"smooth": false},"layout": {"hierarchical": {"enabled": true,"direction": "LR"}},"interaction": {"hover": true},"physics": {"enabled": false,"hierarchicalRepulsion": {"centralGravity": 0,"avoidOverlap": null},"minVelocity": 0.75,"solver": "hierarchicalRepulsion"}}"""
PLOT_COL_LIGHT = {'unk':'#808080',NodeType.object_id:'#FF595E',NodeType.object_type:'#FFCA3A',NodeType.event_id:'#8AC926', NodeType.event_type:'#1982C4','edge':'#000000','bgcolor':'#FFFFFF', 'font_color':'black'}
PLOT_COL_DARK = {'unk':'#808080',NodeType.object_id:'#FF595E',NodeType.object_type:'#FFCA3A',NodeType.event_id:'#8AC926', NodeType.event_type:'#1982C4','edge':'#FFFFFF','bgcolor':'#222222', 'font_color':'white'}


class Node():
    """_summary_
    """


    def __init__(self, id: str, type: NodeType, param: dict=None) -> None:
        """_summary_

        Args:
            id (str): _description_
            type (NodeType): _description_
            param (dict, optional): _description_. Defaults to None.
        """
        self.id = id
        self.type = type
        self.param = param if param is not None else {}


    def __str__(self) -> str:
        return "<Id: "+str(self.id)+", "+str(self.type)+">"
    
    __repr__ = __str__

    # per abilitare inserimento su dizionari
    def __hash__(self) -> int:
        return hash((self.id, self.type))

    def __eq__(self, other: NodeType) -> bool:
        return (self.id, self.type) == (other.id, other.type)
    
    def __ne__(self, other: NodeType) -> bool:
        return not (self == other)

    # per abilitare il sort, durante la generazione della trace, si devono ordinare i nodi di tipo event_id
    def __lt__(self, other: NodeType) -> bool:
        t1 = self.param.get('ocel:timestamp',self.id) 
        t2 = other.param.get('ocel:timestamp',other.id)
        
        return int(self.id) < int(other.id) if t1 == t2 else t1 < t2

    def __gt__(self, other :NodeType) -> bool:
        return not (self < other)

    def __le__(self, other :NodeType) -> bool:
        return self.param.get('ocel:timestamp',self.id) <= other.param.get('ocel:timestamp',other.id)

    def __ge__(self, other :NodeType) -> bool:
        return not (self <= other)



    
class Graph():
    """_summary_
    """

    def __init__(self) -> None:
        self.edges = {} 


    def add_node(self, n: Node) -> None:
        """_summary_

        Args:
            n (Node): _description_
        """
        if n not in self.edges.keys():
            self.edges[n] = []

    # shortcut
    def add_nodes(self, nodes:list[Node]) -> None:
        for n in nodes:
            self.add_node(n)


    def add_edge(self, n1:Node, n2:Node, undirect: bool=False) -> None:
        """_summary_

        Args:
            n1 (Node): _description_
            n2 (Node): _description_
            undirect (bool, optional): _description_. Defaults to False.
        """
        if n2 not in self.edges[n1]:
            self.edges[n1] += [n2]
        if undirect and n1 not in self.edges[n2]:
            self.edges[n2] += [n1]


    def merge(self, other:Graph, inplace:bool =False):
        """_summary_

        Args:
            other (Graph): _description_
            inplace (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        g = self if inplace else Graph()

        nodes = set(list(self.edges.keys())+list(other.edges.keys()))
        g.add_nodes(nodes)

        for v in nodes:
            neighbours = list(set(self.edges.get(v,[])+other.edges.get(v,[])))
            for n in neighbours:
                g.add_edge(v,n,undirect=True)

        return g


    def get_connected_components(self, admitted) -> list[set[Node]]:
        """_summary_

        Returns:
            list[set[Node]]: _description_
        """
        ccs = []
        for n in self.edges.keys():
            if n not in [el for cc in ccs for el in cc] and n.param.get('ocel:type',n.param.get('ocel:activity',n.id))  in admitted :
                ccs += [self.get_connected_component(n, set(), admitted=admitted)]
        return ccs

    def get_connected_component(self, v:Node, visited:set[Node], admitted) -> set[Node]:
        """_summary_

        Args:
            v (Node): _description_
            visited (set[Node]): _description_

        Returns:
            set[Node]: _description_
        """
        visited.add(v)
        for f in self.edges[v]:
            if f not in visited and f.param.get('ocel:type',f.param.get('ocel:activity',f.id))  in admitted:
                self.get_connected_component(f,visited, admitted)
        return visited


    def plot(self, filename:str, admitted=[], theme = "dark") -> None:
        """_summary_

        Args:
            filename (str): _description_
        """
        plot_col = PLOT_COL_DARK if theme == "dark" else PLOT_COL_LIGHT
        net = Network(height='100%', width='100%', bgcolor=plot_col['bgcolor'], font_color=plot_col['font_color']) 
        net.add_nodes([str(n) for n in self.edges.keys()],
            title=[str(n) for n in self.edges.keys()],
            label=[str(n.id) for n in self.edges.keys()],
            color=[plot_col['unk'] if (n.param.get('ocel:type',n.param.get('ocel:activity',n.id)) not in admitted) else plot_col[n.type] for n in self.edges.keys()])

        for n,r in  self.edges.items():
            for v in r:
                col = plot_col['unk']  if (n.param.get('ocel:type',n.param.get('ocel:activity',n.id)) not in admitted ) \
                                 or (v.param.get('ocel:type',v.param.get('ocel:activity',v.id)) not in admitted)  \
                                 else plot_col['edge'] if n.type != v.type \
                                 else  plot_col[v.type]

                dashes = True if col == plot_col['unk']  else False
                width = 1 if col == plot_col['unk']  else 4
                net.add_edge(str(n), str(v), label='', color=col, width=width, dashes=dashes)

        net.set_options(PLOT_OPT)
        #net.show_buttons(filter_=[])
        net.show(filename+'.html')


    def __str__(self) -> str:
        s = "Graph:\n"
        for n, r in self.edges.items():
            s+= str(n) +": "+str(r)+"\n"
        return s
        
    # for iterator pattern
    def __getitem__(self, key:Node) -> list[Node]:
        return self.edges[key]

    def __len__(self) -> None:
        return len(self.edges)

    # merge shortcut operator '+'
    def __add__(self, other:Graph) -> Graph:
        return self.merge(other)

    # inplace merge shortcut operator '+'
    def __iadd__(self, other:Graph) -> Graph:
        return self.merge(other, inplace=True)



class GraphFactory():
    """_summary_
    """

    def build_o2o_id_graph(self, l: Logger) -> Graph:
        """_summary_

        Args:
            l (Logger): _description_

        Returns:
            Graph: _description_
        """
        g = Graph()
        g.add_nodes([Node(id,NodeType.object_id) for id in l.objects.index.tolist()])
        for v in g.edges.keys():
            v.param = {'ocel:type':l.objects.loc[v.id]['ocel:type']}

        for index, row in l.o2o_rel.iterrows():
            n1 = Node(row['ocel:oid1'],NodeType.object_id, {'ocel:type':l.objects.loc[row['ocel:oid1']]['ocel:type']})
            n2 = Node(row['ocel:oid2'],NodeType.object_id, {'ocel:type':l.objects.loc[row['ocel:oid2']]['ocel:type']})
            g.add_edge(n1,n2, undirect=True)

        return g


    def build_e2o_id_graph(self, l: Logger) -> Graph:
        """_summary_

        Args:
            l (Logger): _description_

        Returns:
            Graph: _description_
        """

        g = Graph()
        g.add_nodes([Node(eid,NodeType.event_id) for eid in l.events.index.tolist()])
        g.add_nodes([Node(oid,NodeType.object_id) for oid in l.objects.index.tolist()])

        for v in g.edges.keys():
            if v.type == NodeType.object_id:
                v.param = {'ocel:type':l.objects.loc[v.id]['ocel:type']}
            else:
                v.param = {'ocel:activity':l.events.loc[v.id]['ocel:activity'],
                          'ocel:timestamp':l.events.loc[v.id]['ocel:timestamp']}               

        for index, row in l.e2o_rel.iterrows():
            n1 = Node(l.events.loc[[row['ocel:eid']]].index[0], NodeType.event_id, {'ocel:activity':l.events.loc[row['ocel:eid']]['ocel:activity'],
                      'ocel:timestamp':l.events.loc[row['ocel:eid']]['ocel:timestamp']})
            n2 = Node(row['ocel:oid'], NodeType.object_id, {'ocel:type':l.objects.loc[row['ocel:oid']]['ocel:type']})
            g.add_edge(n1, n2, undirect=True)

        return g


    def build_o2o_type_graph(self, l: Logger) -> Graph:
        """_summary_

        Args:
            l (Logger): _description_

        Returns:
            Graph: _description_
        """

        g = Graph()
        g.add_nodes([Node(id,NodeType.object_type) for id in l.objects['ocel:type'].unique()])

        for index, row in l.o2o_rel.iterrows():
            n1 = Node(l.objects.loc[row['ocel:oid1']]['ocel:type'],NodeType.object_type)
            n2 = Node(l.objects.loc[row['ocel:oid2']]['ocel:type'],NodeType.object_type)
            g.add_edge(n1,n2, undirect=True)

        return g


    def build_e2o_type_graph(self, l: Logger) -> Graph:
        """_summary_

        Args:
            l (Logger): _description_

        Returns:
            Graph: _description_
        """

        g = Graph()
        g.add_nodes([Node(act,NodeType.event_type) for act in l.events['ocel:activity'].unique()])
        g.add_nodes([Node(obj,NodeType.object_type) for obj in l.objects['ocel:type'].unique()])

        for index, row in l.e2o_rel.iterrows():
            n1 = Node(l.events.loc[row['ocel:eid']]['ocel:activity'], NodeType.event_type)
            n2 = Node(l.objects.loc[row['ocel:oid']]['ocel:type'], NodeType.object_type)
            g.add_edge(n1, n2, undirect=True)

        return g
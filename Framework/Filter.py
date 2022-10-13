""" Filter Module: it contains everything that is needed to perform (time) constraint checking on log """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

import copy

from Graph import *
from Logger import Logger
from Logic import *



class Trace():
    """_summary_
    """

    def __init__(self, eids: list[str], oids: list[str], otypes: list[str], eactvities: list[str]) -> None:
        """_summary_

        Args:
            eids (list[str]): _description_
            oids (list[str]): _description_
            otypes (list[str]): _description_
            eactvities (list[str]): _description_
        """
        self.eids = eids
        self.oids = oids 
        self.otypes = otypes
        self.eactivities = eactvities
        self.ltl = self.generate_ltl()


    @staticmethod
    def from_connected_component(cc: list[Node]) -> Trace:
        """_summary_

        Args:
            cc (list[Node]): _description_

        Returns:
            Trace: _description_
        """
        ev = [v for v in cc if v.type==NodeType.event_id]
        ev.sort()

        e_ids = [v.id for v in ev]
        e_activities = [v.param['ocel:activity'] for v in ev] 

        o_ids = [v.id for v in cc if v.type==NodeType.object_id]
        o_types = [v.param['ocel:type'] for v in cc if v.type==NodeType.object_id]

        return Trace(e_ids,o_ids,o_types,e_activities)


    def generate_ltl(self) -> dict[list]:
        """_summary_

        Returns:
            dict[list]: _description_
        """

        ltl = {a:[(k,False) for k in range(0,len(self.eactivities))] for i,a in enumerate(self.eactivities)}
        for i1, a1 in enumerate(self.eactivities):
            ltl[a1][i1] = (i1,True)
        return ltl


    def reverse(self, inplace: bool=False) -> Trace:
        """_summary_

        Args:
            inplace (bool, optional): _description_. Defaults to False.

        Returns:
            Trace: _description_
        """

        obj = self if inplace else copy.deepcopy(self)

        for act, trace in obj.ltl.items():
            obj.ltl[act]= [(len(trace)-1-t[0],t[1]) for t in trace[::-1]]
        obj.eids = [id for id in obj.eids[::-1]]
        obj.eactivities = [act for act in obj.eactivities[::-1]]

        return obj

    def __str__(self) -> str:
        return "Trace -->"+ str(self.ltl)
    
    __repr__ = __str__

    # useful for python iterator pattern
    def __len__(self) -> int:
        return len(self.eids)

    # useful for python iterator pattern
    def __getitem__(self, key:int) -> str:
        return self.eids[key]




class Constraint(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def evaluate(self, trace:Trace) -> bool:
        """_summary_

        Args:
            trace (Trace): _description_

        Returns:
            bool: _description_
        """
        pass



class ResponseConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area) -> None:
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a,Eventually(self.b)))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__


class PrecedenceConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area) -> None:
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a,EventuallyPast(self.b)))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__


class NonResponseConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """
    def __init__(self, activity1: str, activity2: str, area) -> None:
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a,Always(Not(self.b))))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__


class NonPrecedenceConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area):
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a,AlwaysPast(Not(self.b))))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__


class UnaryResponseConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area):
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a, Until(Not(self.b),And(self.b,Always(Not(self.b)))) ))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__



class UnaryPrecedenceConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area):
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a, Since(Not(self.b), And(self.b, AlwaysPast(Not(self.b)))) ))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__



class RespondedExistenceConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area):
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a, Or(Eventually(self.b),EventuallyPast(self.b)) ))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__


class NonCoexistenceConstraint(Constraint):
    """_summary_

    Args:
        TimeConstraint (_type_): _description_
    """

    def __init__(self, activity1: str, activity2: str, area):
        self.area = area
        self.a = AtomicProposition(activity1)
        self.b = AtomicProposition(activity2)
        self.formula = Always(Implies(self.a, And(Always(Not(self.b)),AlwaysPast(Not(self.b))) ))

    def evaluate(self, trace: Trace) -> bool:
        return self.formula.evaluate(trace, step=-1)

    def __str__(self) -> str:
        return self.__class__.__name__+" : "+ str(self.formula)
    
    __repr__ = __str__



class Filter():
    """_summary_
    """

    def __init__(self, log:Logger, constraints:list, areas:dict) -> None:
        """_summary_

        Args:
            log (Logger): _description_
            constraints (list): _description_
            areas (dict): _description_
        """

        self.log = log
        self.constraints = constraints
        self.areas = areas
        # build main graph and traces from connected components
        self.graph =  GraphFactory().build_o2o_id_graph(self.log).merge(GraphFactory().build_e2o_id_graph(self.log))
        self.traces = {name: [Trace.from_connected_component(cc) for cc in self.graph.get_connected_components(area)]  for name,area in areas.items()  }



    def check_constraints(self, propagate:bool =True) -> list[list[bool]]:
        """_summary_

        Args:
            propagate (bool, optional): _description_. Defaults to True.

        Returns:
            list[list[bool]]: _description_
        """
        res = []
        for c in self.constraints:
            res += [self.check_constraint(c, propagate)]
        return res


    def check_constraint(self, c: Constraint, propagate: bool=True) -> list[bool]:
        """_summary_

        Args:
            c (Constraint): _description_
            propagate (bool, optional): _description_. Defaults to True.

        Returns:
            list[bool]: _description_
        """

        results = []
        # reversed to avoid execption when propagate 
        for i in reversed(range(len(self.traces[c.area]))):
            trace = self.traces[c.area][i]
            res = c.evaluate(trace)
            results += [res]

            if (not res) and propagate:
                self.propagate_to_log(trace)
                self.propagate_to_traces(i, c)
                self.propagate_to_graph(trace)

        return results[::-1]


    def propagate_to_graph(self, trace:Trace) -> None:
        """_summary_

        Args:
            trace (Trace): _description_
        """
        #events + rel
        for eid in trace.eids:
            self.graph.edges.pop(Node(eid,NodeType.event_id), None)
            for v,r in self.graph.edges.items():
                for i,n in enumerate(r):
                    if n.id == eid and n.type == NodeType.event_id:
                        del self.graph.edges[v][i]
        #objects + rel
        for oid in trace.oids:
            self.graph.edges.pop(Node(oid,NodeType.object_id), None)   
            for v,r in self.graph.edges.items():
                for i,n in enumerate(r):
                    if n.id == oid and n.type == NodeType.object_id:
                        del self.graph.edges[v][i]    
         

    def propagate_to_traces(self, i: int, c) -> None:
        """_summary_

        Args:
            i (int): _description_
        """
        del self.traces[c.area][i]
        
        
    def propagate_to_log(self, trace: Trace) -> None:
        """_summary_

        Args:
            trace (Trace): _description_
        """
        #events
        self.log.events.drop(labels = trace.eids, axis='index', inplace =True)
        #objects
        self.log.objects.drop(labels = trace.oids, axis='index', inplace =True)
        #relations
        self.log.e2o_rel.drop(self.log.e2o_rel.loc[self.log.e2o_rel['ocel:eid'].isin(trace.eids)].index, inplace=True)
        self.log.o2o_rel.drop(self.log.o2o_rel.loc[self.log.o2o_rel['ocel:oid1'].isin(trace.oids)].index, inplace=True)
        self.log.o2o_rel.drop(self.log.o2o_rel.loc[self.log.o2o_rel['ocel:oid2'].isin(trace.oids)].index, inplace=True)


""" Filter Module """

# libraries and requirements
from __future__ import annotations
from abc import ABC, abstractmethod
from ast import For
from typing import Any


class Formula(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def evaluate(self, trace:Trace, step:int) -> str:
        """_summary_

        Args:
            trace (_type_): _description_
            step (_type_): _description_

        Returns:
            str: _description_
        """
        pass


class AtomicProposition(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, id:str):
        self.id = id

    def evaluate(self, trace:Trace, step:int) -> str:
        return trace.ltl[self.id][step][1]

    def __str__(self) -> str:
        return str(self.id)


class And(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        return self.a.evaluate(trace,step) and self.b.evaluate(trace,step)

    def __str__(self) -> str:
        return "("+str(self.a)+ " & "+str(self.b)+")"


class Or(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        return self.a.evaluate(trace,step) or self.b.evaluate(trace,step)

    def __str__(self) -> str:
        return "("+str(self.a)+ " | "+str(self.b)+")"


class Not(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula):
        self.a = a

    def evaluate(self, trace:Trace, step:int) -> str:
        return not (self.a.evaluate(trace,step))

    def __str__(self) -> str:
        return "~("+str(self.a)+")"


class Implies(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        return Or(Not(self.a), self.b).evaluate(trace,step)

    def __str__(self) -> str:
        return "("+str(self.a)+" -> "+str(self.b)+")"


class FullImplies(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        return And(Implies(self.a,self.b), Implies(self.b,self.a)).evaluate(trace,step)

    def __str__(self) -> str:
        return "("+str(self.a)+" <-> "+str(self.b)+")"


class Next(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, steps:int=1):
        self.a = a
        self.steps=steps

    def evaluate(self, trace:Trace, step:int) -> str:
        assert step > 0 and len(trace) > step+self.steps

        for s in range(step+1, step+self.steps+1):
            if not(self.a.evaluate(trace,s)):
                return False

        return True

    def __str__(self) -> str:
        return "X{"+str(self.steps)+"}("+str(self.a)+")"


class NextPast(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, steps=1):
        self.a = a
        self.steps=steps

    def evaluate(self, trace:Trace, step:int) -> str:
        assert step > 0 and 0 <= step-self.steps
 
        for s in range(step-1, step-self.steps-1, -1):
            if not(self.a.evaluate(trace,s)):
                return False
        return True

    def __str__(self) -> str:
        return "X_past{"+str(self.steps)+"}("+str(self.a)+")"


class Eventually(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula):
        self.a = a

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(step+1,len(trace),1):
            if self.a.evaluate(trace,s):
                return True
        return False

    def __str__(self) -> str:
        return "F("+str(self.a)+")"



class EventuallyPast(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula):
        self.a = a

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(step-1,-1,-1):
            if self.a.evaluate(trace,s):
                return True
        return False

    def __str__(self) -> str:
        return "F_past("+str(self.a)+")"


class Always(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula):
        self.a = a

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(step+1,len(trace),1):
            if not (self.a.evaluate(trace,s)):
                return False
        return True

    def __str__(self) -> str:
        return "G("+str(self.a)+")"


class AlwaysPast(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula):
        self.a = a

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(step-1,-1,-1):
            if not (self.a.evaluate(trace,s)):
                return False
        return True

    def __str__(self) -> str:
        return "G_past("+str(self.a)+")"



class Until(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(step+1,len(trace),1):
            if (self.b.evaluate(trace,s)):
                ev=True
                for s2 in range(step+1,s,1):
                    if not (self.a.evaluate(trace,s2)):
                        ev = False
                        #break
                if ev:
                    return True
        return False


    def __str__(self) -> str:
        return "("+str(self.a)+" U "+str(self.b)+")"



class Since(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        for s in range(0,step,1):
            if (self.b.evaluate(trace,s)):
                ev=True
                for s2 in range(s+1,step,1):
                    if not (self.a.evaluate(trace,s2)):
                        ev = False
                        #break
                if ev:
                    return True
        return False

    def __str__(self) -> str:
        return "("+str(self.a)+" S "+str(self.b)+")"



class Release(Formula):
    """_summary_

    Args:
        Formula (_type_): _description_
    """

    def __init__(self, a:Formula, b:Formula):
        self.a = a
        self.b = b

    def evaluate(self, trace:Trace, step:int) -> str:
        return Not(Until(Not(self.a),Not(self.b))).evaluate(trace,step)

    def __str__(self) -> str:
        return "("+str(self.a)+" R "+str(self.b)+")"

    

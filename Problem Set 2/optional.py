#!/usr/bin/env python
# Simple Daikon-style invariant checker
# Andreas Zeller, May 2012
# Complete the provided code, using your code from
# first exercise and adding ability to infer assertions
# for variable type, set and relations
# Modify only the classes Range and Invariants,
# if you need additional functions, make sure
# they are inside the classes.

import sys
import math
import random

def square_root(x, eps = 0.00001):
    assert x >= 0
    y = math.sqrt(x)
    assert abs(square(y) - x) <= eps
    return y

def square(x):
    return x * x

def double(x):
    return abs(20 * x) + 10

# The Range class tracks the types and value ranges for a single variable.
class Range:
    def __init__(self):
        self.min = None  # Minimum value seen
        self.max = None  # Maximum value seen
        self.type = None # Type of variable
        self.set = set() # Set of values taken

    # Invoke this for every value
    def track(self, value):
        # YOUR CODE
        if self.min == None:
            self.min = value
            self.max = value
        elif value < self.min:
            self.min = value
        elif value > self.max:
            self.max = value

        self.type = value
        self.set.add(value)

    def __repr__(self):
        (repr(self.type) + " " + repr(self.min) + ".." +
        repr(self.max) + " " + repr(self.set))


# The Invariants class tracks all Ranges for all variables see.
class Invariants:
    def __init__(self):
        # Mapping (Function Name) -> (Event type) -> (Variable Name)
        # e.g. self.vars["sqrt"]["call"]["x"] = Range()
        # holds the range for the argument x when calling sqrt(x)
        self.vars = {}
        self.relations = {}

    def track(self, frame, event, arg):
        if event == "call" or event == "return":
            # YOUR CODE HERE.
            # MAKE SURE TO TRACK ALL VARIABLES AND THEIR VALUES
            fname = frame.f_code.co_name

            for vname, value in frame.f_locals.iteritems():
                if not (fname in self.vars):
                    self.vars[fname] = {event: {vname: Range()}}
                elif not (event in self.vars[fname]):
                    self.vars[fname][event] = {vname: Range()}
                elif not (vname in self.vars[fname][event]):
                    self.vars[fname][event][vname] = Range()

                self.vars[fname][event][vname].track(value)

            if event == "return":
                if not (fname in self.vars):
                    self.vars[fname] = {event: {"ret": Range()}}
                elif not (event in self.vars[fname]):
                    self.vars[fname][event] = {"ret": Range()}
                elif not ("ret" in self.vars[fname][event]):
                    self.vars[fname][event]["ret"] = Range()

                self.vars[fname][event]["ret"].track(arg)

            # Code that creates relationships between variables
            local_vars = frame.f_locals
            if event == "return":
                local_vars["ret"] = arg

            for vname, value in local_vars.iteritems():
                if not (fname in self.relations):
                    self.relations[fname] = {event: {}}
                elif not (event in self.relations[fname]):
                    self.relations[fname][event] = {}

                self.relations[fname][event][vname] = self.get_relations(vname,
                                                        local_vars)

    def get_relations(self, vname, local_vars):
        result = ""
        value = local_vars[vname]

        for vname2, value2 in local_vars.iteritems():
            if vname != vname2:
                if value == value2:
                    result = "    assert " + vname + " == " + vname2
                elif value <= value2:
                    result = "    assert " + vname + " <= " + vname2
                else:
                    result = "    assert " + vname + " >= " + vname2
                result += "\n"

        return result

    def __repr__(self):
        # Return the tracked invariants
        s = ""
        for function, events in self.vars.iteritems():
            for event, vars in events.iteritems():
                s += event + " " + function + ":\n"

                for var, range in vars.iteritems():
                    s += ("    assert isinstance(" + var + ", type(" +
                    repr(range.type) + "))\n")
                    s += "    assert " + var + " in " + repr(range.set) + "\n"
                    s += "    assert "
                    if range.min == range.max:
                        s += var + " == " + repr(range.min)
                    else:
                        s += (repr(range.min) + " <= " + var + " <= " +
                            repr(range.max))
                    s += "\n"
                    # ADD HERE RELATIONS BETWEEN VARIABLES
                    # RELATIONS SHOULD BE ONE OF: ==, <=, >=
                    s += self.relations[function][event][var]
        return s

invariants = Invariants()

def traceit(frame, event, arg):
    invariants.track(frame, event, arg)
    return traceit

sys.settrace(traceit)
# Tester. Increase the range for more precise results when running locally
eps = 0.000001
test_vars = [34.6363, 9.348, -293438.402]
for i in test_vars:
# for i in range(1, 10):
    z = double(i)
sys.settrace(None)
print invariants

# Example sample of a correct output:
"""
return double:
    assert isinstance(x, type(-293438.402))
    assert x in set([9.348, -293438.402, 34.6363])
    assert -293438.402 <= x <= 34.6363
    assert x <= ret
"""

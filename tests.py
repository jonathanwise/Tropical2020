from CombinatorialCurve import *

C = CombCurve("Example 3.5")
v1 = vertex("v1", 0)
v2 = vertex("v2", 0)
v3 = vertex("v3", 1)
e1 = edge("e1", 1.0, v1, v2)
e2 = edge("e2", 1.0, v2, v3)
e3 = edge("e3", 1.0, v1, v3)
e4 = edge("e4", 1.0, v1, v1)
l = leg("l", v1)

C.edges = {e1, e2, e3, e4}
C.legs = {l}

dict = {v1: 0.0, v2: 0.0, v3: 0.0, l: 0.0}

f = StrictPiecewiseLinearFunction(C, dict)

assert C.vertices == {v1, v2, v3}

assert C.degree(v1) == 5
assert C.degree(v2) == 2
assert C.degree(v3) == 2

assert C.genus == 3
assert C.bettiNumber == 2

subdiv = C.getSubdivision(e4, 0.5, 0.5)
assert subdiv.degree(v1) == 5
assert subdiv.degree(v2) == 2
assert subdiv.degree(v3) == 2
assert subdiv.genus == 3
assert subdiv.bettiNumber == 2
assert subdiv.vertexNumber == C.vertexNumber + 1
assert subdiv.edgeNumber == C.edgeNumber + 1


C = CombCurve("Exercise 3.15 part 1")
v1 = vertex("v1", 0)
v2 = vertex("v2", 0)
v3 = vertex("v3", 0)
e1 = edge("e1", 1.0, v1, v2)
e2 = edge("e2", 1.0, v1, v3)
e3 = edge("e3", 1.0, v1, v3)
e4 = edge("e4", 1.0, v2, v3)
e5 = edge("e5", 1.0, v1, v1)
e6 = edge("e6", 1.0, v2, v2)
e7 = edge("e7", 1.0, v3, v3)
C.edges = {e1, e2, e3, e4, e5, e6, e7}
assert C.bettiNumber == 5
assert C.genus == 5



C = CombCurve("Exercise 3.15 parts 2 and 3")
v1 = vertex("v1", 1)
v2 = vertex("v2", 1)
v3 = vertex("v3", 1)
v4 = vertex("v4", 1)
v5 = vertex("v5", 1)
C.edges = {edge("e1", 1.0, v1, v2), edge("e2", 1.0, v2, v3), edge("e3", 1.0, v3, v4), edge("e4", 1.0, v4, v5)}
assert C.bettiNumber == 0
assert C.genus == 5
for v in C.vertices:
    assert v.genus <= 1




print "If you see this, then all previous assertations were true!"
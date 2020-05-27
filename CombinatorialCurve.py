import copy
import numpy as np
from GraphIsoHelper import *


# A vertex has a name and non-negative genus
class vertex(object):
    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    # genus_ should be a non-negative integer
    def __init__(self, name_, genus_):
        # Don't allow negative genus!
        if genus_ < 0:
            raise ValueError("Genus must be non-negative")
        self.name = name_
        self._genus = genus_

    @property
    def genus(self):
        return self._genus

    # Control how the genus property is set
    # genus_ should be a non-negative integer
    @genus.setter
    def genus(self, genus_):
        # Don't allow negative genus!
        if genus_ < 0:
            raise ValueError("Genus must be non-negative.")
        self._genus = genus_


# An edge has a name, non-negative length, and endpoints
class edge(object):
    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    # length_ should be a non-negative double
    # vert1_ should be a vertex
    # vert2_ should be a vertex
    def __init__(self, name_, length_, vert1_, vert2_):
        self.name = name_

        # Don't allow negative lengths!
        if length_ < 0.0:
            raise ValueError("Length must be non-negative.")
        self._length = length_

        # Distinguished endpoints to help identify self loops
        self.vert1 = vert1_
        self.vert2 = vert2_

    @property
    def length(self):
        return self._length

    # Control how the length property is set
    # length_ should be a non-negative double
    @length.setter
    def length(self, length_):
        # Don't allow negative lengths!
        if length_ < 0.0:
            raise ValueError("Length must be non-negative.")
        self._length = length_

    # The set of vertices is a read only property computed upon access
    @property
    def vertices(self):
        return {self.vert1, self.vert2}


# A leg has a name and root
class leg(object):
    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    # root_ should be a vertex
    def __init__(self, name_, root_):
        self.name = name_
        self.root = root_

    # The set of vertices is a read only property computed upon access
    @property
    def vertices(self):
        return {self.root}


# A Combinatorial Tropical Curve has a name, set of edges, and set of legs
class CombCurve(object):
    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    def __init__(self, name_):
        self.name = name_
        self._edges = set()
        self._legs = set()

        # Variables for caching vertices
        self._vertexCacheValid = False
        self._vertexCache = set()

        # Variables for caching genus
        self._genusCacheValid = False
        self._genusCache = 0

        # Variables for caching vertex self loop counts
        self._vertexSelfLoopsCacheValid = False
        self._vertexSelfLoopsCache = {}

        # Variables for caching vertex everything couns
        self._vertexEverythingCacheValid = False
        self._vertexEverythingCache = {}

        # Variables for caching the core
        self._coreCacheValid = False
        self._coreCache = None


    @property
    def edges(self):
        return self._edges

    # Control how edges are set
    # edges_ should be a set of edges
    @edges.setter
    def edges(self, edges_):
        self._edges = edges_
        self._vertexCacheValid = False
        self._genusCacheValid = False
        self._vertexSelfLoopsCacheValid = False
        self._vertexEverythingCacheValid = False
        self._coreCacheValid = False


    @property
    def edgesWithVertices(self):
        return {e for e in self.edges if not (e.vert1 is None or e.vert2 is None)}

    @property
    def legs(self):
        return self._legs

    @property
    def legsWithVertices(self):
        return {nextLeg for nextLeg in self.legs if nextLeg.root is not None}

    # Control how legs are set
    # legs_ should be a set of legs
    @legs.setter
    def legs(self, legs_):
        self._legs = legs_
        self._vertexCacheValid = False
        self._genusCacheValid = False
        self._vertexEverythingCacheValid = False

    # The set of vertices is a read only property computed upon access, unless a valid cache is available
    # It is the collection of vertices that are endpoints of edges or roots of legs
    @property
    def vertices(self):
        if not self._vertexCacheValid:
            # Flatmap self.edges with the function e => e.vertices
            unflattened_vertex_list = [e.vertices for e in self.edges] + [nextLeg.vertices for nextLeg in self.legs]
            flattened_vertex_list = []
            for sublist in unflattened_vertex_list:
                for v in sublist:
                    flattened_vertex_list.append(v)

            self._vertexCache = set(flattened_vertex_list) - {None}
            self._vertexCacheValid = True

        return self._vertexCache

    # The number of vertices is a read only property computed upon access
    # It is the number of vertices
    @property
    def vertexNumber(self):
        return len(self.vertices)

    # The number of edges is a read only property computed upon access
    # It is the number of edges
    @property
    def edgeNumber(self):
        return len(self.edges)

    @property
    def numEdgesWithVertices(self):
        return len(self.edgesWithVertices)

    # The Betti number is a read only property computed upon access
    @property
    def bettiNumber(self):
        return self.numEdgesWithVertices - self.vertexNumber + 1

    # Genus is a read only property computed upon access
    @property
    def genus(self):
        if not self._genusCacheValid:
            self._genusCache = self.bettiNumber + sum([v.genus for v in self.vertices])
            self._genusCacheValid = True
        return self._genusCache

    # Returns the degree of vertex v accounting for legs and self loops
    def degree(self, v):
        return self.numEdgesAttached(v) + self.numLegsAttached(v)

    def numEdgesAttached(self, v):
        return sum(1 for e in self.edges if e.vert1 == v) + sum(1 for e in self.edges if e.vert2 == v)

    def numLegsAttached(self, v):
        return sum(1 for attachedLeg in self.legs if attachedLeg.root == v)

    # Returns a copy of this curve where all vertices, edges, and legs are also copied shallowly
    def getFullyShallowCopy(self, returnCopyInfo=False):
        copyInfo = {}
        vertexCopyDict = {}
        for v in self.vertices:
            vCopy = copy.copy(v)
            vertexCopyDict[v] = vCopy

            if returnCopyInfo:
                copyInfo[v] = vCopy

        edgeCopies = set()
        legCopies = set()
        for nextEdge in self.edges:
            nextEdgeCopy = edge(nextEdge.name, nextEdge.length,
                                vertexCopyDict[nextEdge.vert1], vertexCopyDict[nextEdge.vert2])
            edgeCopies.add(nextEdgeCopy)

            if returnCopyInfo:
                copyInfo[nextEdge] = nextEdgeCopy

        for nextLeg in self.legs:
            nextLegCopy = leg(nextLeg.name, vertexCopyDict[nextLeg.root])
            legCopies.add(nextLegCopy)

            if returnCopyInfo:
                copyInfo[nextLeg] = nextLegCopy

        curveCopy = CombCurve(self.name)
        curveCopy.edges = edgeCopies
        curveCopy.legs = legCopies

        if returnCopyInfo:
            return curveCopy, copyInfo
        else:
            return curveCopy

    # e should be an edge and the length should be a double
    # genus should be a non-negative integer
    def subdivide(self, e, length, genus=0):
        # Don't force a negative length
        assert 0.0 <= length <= e.length

        # Don't split a nonexistent edge
        assert e in self.edges

        v = vertex("(vertex splitting " + e.name + ")", genus)
        e1 = edge("(subdivision 1 of " + e.name + ")", length, e.vert1, v)
        e2 = edge("(subdivision 2 of " + e.name + ")", e.length - length, v, e.vert2)

        self.edges = self.edges - {e}
        self.edges = self.edges | {e1}
        self.edges = self.edges | {e2}

    # e should be an edge and the length should be a double
    # genus should be a non-negative integer
    # returns a new CombCurve with edge e subdivided
    def getSubdivision(self, e, length, genus=0):
        subdivision = copy.copy(self)
        subdivision.subdivide(e, length, genus)
        return subdivision

    # v should be a vector
    # Returns the set of all elements of the form (e, n), where e is an edge, n is 1 or 2,
    # and the n^th endpoint of e is v
    def getEndpointsOfEdges(self, v):
        endpoints = []
        for e in self.edges:
            if e.vert1 == v:
                endpoints += [(e, 1)]
            if e.vert2 == v:
                endpoints += [(e, 2)]
        for nextLeg in self.legs:
            if nextLeg.root == v:
                endpoints += [(nextLeg, 1)]
        return set(endpoints)

    @property
    def vertexEverythingDict(self):
        if not self._vertexEverythingCacheValid:
            self._vertexEverythingCache = {}
            for v in self.vertices:
                numEdgesAttached = self.numEdgesAttached(v)
                numLegsAttached = self.numLegsAttached(v)
                g = v.genus
                key = (numEdgesAttached, numLegsAttached, g)
                if key in self._vertexEverythingCache:
                    self._vertexEverythingCache[key] += 1
                else:
                    self._vertexEverythingCache[key] = 1

            self._vertexEverythingCacheValid = True
        return self._vertexEverythingCache

    def getVerticesByEverything(self):
        vertexDict = {}
        for v in self.vertices:
            numEdgesAttached = self.numEdgesAttached(v)
            numLegsAttached = self.numLegsAttached(v)
            g = v.genus
            key = (numEdgesAttached, numLegsAttached, g)
            if key in vertexDict:
                vertexDict[key].append(v)
            else:
                vertexDict[key] = [v]
        return vertexDict

    def getNumSelfLoops(self):
        return sum(1 for e in self.edges if len(e.vertices) == 1)

    @property
    def vertexSelfLoopDict(self):
        if not self._vertexSelfLoopsCacheValid:
            self._vertexSelfLoopsCache = {}
            for v in self.vertices:
                numLoops = sum(1 for e in self.edges if e.vertices == {v})
                if numLoops in self._vertexSelfLoopsCache:
                    self._vertexSelfLoopsCache[numLoops] += 1
                else:
                    self._vertexSelfLoopsCache[numLoops] = 1
            self._vertexSelfLoopsCacheValid = True
        return self._vertexSelfLoopsCache

    def getPermutations(self, lst):
        return GraphIsoHelper.getPermutations(lst)

    def checkIfBijectionIsIsomorphism(self, other, domainOrderingDict, codomainOrderingDict):
        return GraphIsoHelper.checkIfBijectionIsIsomorphism(self, other, domainOrderingDict, codomainOrderingDict)

    def getBijections(self, permDict):
        return GraphIsoHelper.getBijections(permDict)

    def isBruteForceIsomorphicTo(self, other):
        return GraphIsoHelper.isBruteForceIsomorphicTo(self, other)

    def isIsomorphicTo(self, other):
        return GraphIsoHelper.isIsomorphicTo(self, other)

    def simplifyNames(self):
        orderedVertices = list(self.vertices)
        for i in range(len(orderedVertices)):
            orderedVertices[i].name = "v" + str(i)
        for e in self.edges:
            e.name = "edge: " + e.vert1.name + ", " + e.vert2.name
        for nextLeg in self.legs:
            nextLeg.name = "leg: " + nextLeg.root.name

    def showNumbers(self):
        print("Number of Vertices: ", self.vertexNumber, " Number of Edges: ", self.edgeNumber)

    @staticmethod
    def printCurve(curve):
        print("\n\nVertices:")
        for v in curve.vertices:
            print(v.name, " with genus ", v.genus)
        print("Edges:")
        for e in curve.edges:
            print(e.name)
        print("Legs:")
        for nextLeg in curve.legs:
            print(nextLeg.name)

    # Prints the names of vertices
    def showVertices(self):
        print([v.name for v in self.vertices])

    # Prints the names of edges
    def showEdges(self):
        print([e.name for e in self.edges])

    # Prints the names of legs
    def showLegs(self):
        print([nextLeg.name for nextLeg in self.legs])

    # This function will check if the tropical curve is connected (in the style of Def 3.10)
    @property
    def isConnected(self):

        A = np.zeros((self.vertexNumber, self.vertexNumber))
        _vertices = list(self.vertices)

        for x in self.edges:
            v1 = x.vert1
            v2 = x.vert2

            i = _vertices.index(v1)
            j = _vertices.index(v2)

            # print(i, j)
            # So that the connections made by the edges are symmetric ((v1,v2) = (v2,v1))
            A[i][j] = 1
            A[j][i] = 1

        # So that the while loop works
        go = True
        numbers = []
        newNumbers = [0]

        while go:
            numbers.extend(newNumbers)
            brandNewNumbers = []
            for i in newNumbers:
                for k in range(self.vertexNumber):
                    if A[i][k] == 1:
                        if k not in numbers:
                            brandNewNumbers.append(k)

            newNumbers = []
            newNumbers.extend(brandNewNumbers)
            brandNewNumbers = []
            go = len(newNumbers) > 0

        return len(numbers) == self.vertexNumber



    @property
    def core(self):

        if self._coreCacheValid == False:
            assert self.genus > 0

            core = copy.copy(self)

            genus = core.genus

            core.legs = {}

            assert core.isConnected

            keepChecking = True

            while keepChecking:

                keepChecking = False
                for i in core.vertices:
                    
                    if i.genus == 0 and core.degree(i) < 2:
                        
                        
                        for x in core.edges:
                            if i == x.vert1 or i == x.vert2:
                                keepChecking = True
                                core.edges = core.edges - {x}
                        
            self._coreCache = core
            self._coreCacheValid = True

        return self._coreCache

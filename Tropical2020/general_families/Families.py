from basic_families.PiecewiseLinearFunction import *


class Family(object):
    def __init__(self, basicFamilies, morphisms):

        # Type checking
        if not isinstance(basicFamilies, set):
            raise ValueError("basicFamilies must be a Set[BasicFamily]")
        if not isinstance(morphisms, set):
            raise ValueError("morphisms must be a Set[BasicFamilyMorphism]")

        # Ensure that the morphisms actually belong in this family
        for morphism in morphisms:
            assert morphism.domain in basicFamilies
            assert morphism.codomain in basicFamilies

        self.basicFamilies = basicFamilies
        self.morphisms = morphisms

    # Returns the set of ancestors of the given basic family
    def getAncestors(self, basicFamily):

        # Type checking
        assert isinstance(basicFamily, BasicFamily)

        # Get the morphisms that map into the given basic family
        def isIncoming(morphism):
            return morphism.codomain == basicFamily
        incomingArrows = filter(isIncoming, self.morphisms)

        # Get the set of domains of the morphisms that map into the given basic family
        return {arrow.domain for arrow in incomingArrows}

    # Returns the maximal ancestors of the given basic family
    def getMaximalAncestors(self, basicFamily):

        # Type checking
        assert isinstance(basicFamily, BasicFamily)

        # Get the morphisms that map into the given basic family from a maximal family
        def isIncoming(morphism):
            return morphism.codomain == basicFamily
        incomingArrows = filter(isIncoming, self.maximalCurvesIter())

        # Get the set of domains of the morphisms that map into the given basic family
        return {arrow.domain for arrow in incomingArrows}

    # Returns an iterator of all basic families that are not contractions of any other family
    def maximalCurvesIter(self):

        def isMaximal(basicFam):

            # A basic family is not maximal if it's the codomain of some proper morphism
            for morphism in self.morphisms:
                if morphism.codomain == basicFam and morphism.domain != basicFam:
                    return False

            # If this code is reached, then no proper morphism maps into basicFam, and so it's maximal.
            return True

        return filter(isMaximal, self.basicFamilies)


class PLFFamily(object):
    # domain: Family
    # functions: Dictionary[BasicFamily, SPLF]
    def __init__(self, domain, functions):

        # Type checking
        assert isinstance(domain, Family)
        assert isinstance(functions, dict)

        # Make sure functions actually is an assignment of functions on the family
        assert set(functions.keys()) == domain.basicFamilies, \
            "'functions' should assign something to each basic family."
        for key in functions:
            assert isinstance(functions[key], PiecewiseLinearFunction), \
                "functions[key] should be a piecewise linear function."
            assert functions[key].domain == key, \
                "functions[key] should have key as its domain."

        self.domain = domain
        self.functions = functions

        if not self.isWellDefined():
            raise ValueError("The given functions are not compatible with each other.")

    def morphismPreservesFunctions(self, morphism):

        assert morphism in self.domain.morphisms, "The given morphism should belong to the domain family."

        domainPLF = self.functions[morphism.domain]
        pushforwardPLF = domainPLF.getPushforward(morphism)
        codomainPLF = self.functions[morphism.codomain]

        return pushforwardPLF == codomainPLF

    def isWellDefined(self):
        for morphism in self.domain.morphisms:
            if not self.morphismPreservesFunctions(morphism):
                return False
        return True

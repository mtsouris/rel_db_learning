"""
Created on 2022-06-08

@author: wf
"""

from enum import Enum
import copy


class Notation(str, Enum):
    """
    a notation to be used for stringifcation
    """

    math = "LaTex math symbols"
    utf8 = "UTF-8 Symbols"
    plain = "plaintext ASCII"
    short = "short notation without delimiters using juxtapositions"


class Set(set):
    """
    https://docs.python.org/3/tutorial/datastructures.html#sets
    """

    notation = Notation.plain

    def __init__(self, *args, **kwargs):
        """
        constructor
        """
        super().__init__(*args, **kwargs)

    def __str__(self):
        text = Set.stringify_set(self, notation=Set.notation)
        return text

    @classmethod
    def stringify_set(cls, pSet, notation: Notation):
        """
        return a string representation of the given set using the given delimiter

        Args:
            pSet(set): the set to stringify
            delim(str): the delimiter to use
        """
        elementTexts = []
        for elem in pSet:
            elementTexts.append(str(elem))
        sortedElements = sorted(elementTexts)
        if len(sortedElements) == 0:
            # empty set
            if notation == Notation.math:
                text = r"\emptyset"
            else:
                text = "∅"
        else:
            elementDelim = ","
            if notation == Notation.short:
                elementDelim = ""  # Thin space would be better
            if notation == Notation.short:
                text = ""
            elif notation == Notation.math:
                text = r"\{"
            else:
                text = "{"

            delim = ""
            for element in sortedElements:
                text += f"{delim}{element}"
                delim = elementDelim
            if notation == Notation.short:
                pass
            elif notation == Notation.math:
                text += r"\}"
            else:
                text += "}"
        return text


class FD(object):
    """A functional dependency with left- and right-hand side."""

    notation = Notation.plain

    def __init__(self, left, right):
        """Create FD with left hand side  and right hand side

        Args:
            left(object): set of attributes for the left hand side
            right(object): set of attributes for the right hand side

        """
        self.left = Set(left)
        self.right = Set(right)

    def __str__(self):
        """
        convert me to a string

        Return:
            str: a string representation of myself
        """
        text = FD.stringify_FD(self, FD.notation)
        return text

    @classmethod
    def stringify_FD(cls, fd, notation: Notation):
        """
        Return:
            a string representation of the given Functional Dependency
        """
        setNotation = Notation.short
        leftText = Set.stringify_set(fd.left, notation=setNotation)
        rightText = Set.stringify_set(fd.right, notation=setNotation)
        if notation == Notation.utf8:
            to = "→"
        elif notation == Notation.math:
            to = r" \to "
        else:
            to = "->"
        text = f"{leftText}{to}{rightText}"
        return text


class Attribute:
    """
    an Attribute e.g.
        Example: Attribute('A', 'Wikidata identifier', 'Wikidata-Schlüssel')
    """

    def __init__(self, var_name: str, english_name: str, german_name: str):
        """
        constructor

        Args:
            var_name(str): the Variable name
            english_name(str): the english name
            german_name(str): the german name

        """
        self.var_name = var_name
        self.german_name = german_name
        self.english_name = english_name

    def __str__(self):
        text = f"{self.var_name}≡{self.english_name}≡{self.german_name}"
        return text


class RelSchema(object):
    """A relation schema consists of a set of attributes and a set of FDs.

    Various normal forms exist to describe "good" schemata.  Normalization
    is the process of creating schemata that satisfy certain normal forms.
    The class of synthesis algorithms targets 3NF.
    """

    def __init__(
        self, attributes: Set, fds, name: str = "R", notation: Notation = None
    ):
        """
        Construct relation schema with attributes and FDs.

        Args:
            attributes(list): a list of Attributes
            fds(FunctionalDependencySet): a set of FDs
            name(string): the name of the RelatonSchema
            notation(Notation): the notation to use
        """
        if notation is None:
            notation = Notation.utf8
        self.notation = notation
        self.attributes = attributes
        self.fds = fds
        self.name = name

    def __str__(self):
        text = RelSchema.stringify(self, self.notation)
        return text

    @classmethod
    def stringify(cls, rs, notation):
        """
        return a textual representation of the given relational schema in the given notation
        """
        attrText = Set.stringify_set(rs.attributes, notation)
        fds = copy.deepcopy(rs.fds)
        fds.notation = notation
        fdsText = str(fds)
        rsSet = Set([attrText, fdsText])
        rsSetText = Set.stringify_set(rsSet, notation=notation)
        rsText = f"{rs.name}={rsSetText}"
        return rsText

    def findCandidateKeys(self):
        """
        find candidate keys
        """
        cklist = []
        for foundKeySet in self.fds.find_candidate_keys():
            keySet = Set()
            for foundKey in foundKeySet:
                attr = self.fds.attribute_map[foundKey]
                keySet.update([attr])
            cklist.append(keySet)
        return cklist

"""
Created on 25.05.2022

@author: maxwellgerber

see https://gist.github.com/maxwellgerber/4caae07161ea66123de4d6c374387786

"""

from itertools import combinations, permutations, chain
import numpy
import datetime
from .fdsbase import Attribute, Set, Notation, FD


class FunctionalDependencySet:
    """
    a functional dependency set
    """

    def __init__(
        self,
        attributes: str = "",
        title: str = "",
        description: str = "",
        notation: Notation = None,
        debug: bool = False,
    ):
        """
        constructor

        Args:
            attributes(str): a string of attribute variable names of the scheme
            title(str): a title for this functional Dependency Set
            description(str): a description for this functional Dependency Set
            notation(Notation): the notation to be used
            debug(bool): if True switch debugging on
        """
        self.title = title
        self.description = description
        if notation is None:
            notation = Notation.utf8
        self.notation = notation
        self.debug = debug
        self.isodate = datetime.datetime.now().isoformat()
        # list of FDs of the scheme. An FD is stored as a tuple (x, y), meaning x -> y
        self.dependencies = []

        # set of attributes of the scheme
        self.attributes = Set()
        self.attribute_map = {}

        self.isdecomposed = False

        for attr in attributes:
            self.add_attribute(attr)

    def __iter__(self):
        """
        makes me iterable
        """
        for fd in self.dependencies:
            yield fd

    def __str__(self):
        """
        return my text representation
        """
        text = self.stringify_dependencies()
        return text

    def set_list_as_text_list(self, set_list: list, notation: Notation):
        """
        convert a list of sets to a list of strings using the given delimiter

        Args:
            set_list(list): list of sets
            notation(Notation): the notation to use

        Returns:
            list: of stringified sets
        """
        text_list = []
        for a_set in set_list:
            text_list.append(Set.stringify_set(a_set, notation=notation))
        text_list = sorted(text_list)
        return text_list

    def copy(self):
        fds = FunctionalDependencySet()
        fds.title = self.title
        fds.description = self.description
        fds.notation = self.notation
        fds.debug = self.debug
        fds.attributes = self.attributes.copy()
        fds.attribute_map = self.attribute_map.copy()
        fds.dependencies = self.dependencies.copy()
        fds.isdecomposed = self.isdecomposed
        return fds

    def stringify_dependencies(self, fdsToStringify: list = []):
        """
        stringifies the set of dependencies

        Args:
           fdsToStringify(list): set of fds in case only specific dependencies are needed
        """
        text = "{"
        delim = ""
        if self.notation == Notation.math or self.notation == Notation.plain:
            fdNotation = self.notation
        else:
            fdNotation = Notation.utf8

        if fdsToStringify == []:
            fdsToStringify = self.dependencies
        for left, right in fdsToStringify:
            fd = FD(left, right)
            fdtext = FD.stringify_FD(fd, fdNotation)
            text += f"{delim}{fdtext}"
            delim = ","
        text += "}"
        return text

    def add_attribute(
        self, attr_var: str, attr_english_name: str = None, attr_german_name: str = None
    ):
        """
        add attribute to the attribute set of the scheme

        Args:
            attr_var(string): attribute variable name to be added to the scheme
            attr_english_name(string): the name of the attribute in english
            attr_german_name(string): the name of the attribute in german
        """
        if attr_english_name is None:
            attr_english_name = attr_var
        if attr_german_name is None:
            attr_german_name = attr_english_name
        attr = Attribute(attr_var, attr_english_name, attr_german_name)
        self.add_an_attribute(attr)

    def add_an_attribute(self, attr):
        """
        add the given Attribute
        """
        self.attributes.add(attr.var_name)
        self.attribute_map[attr.var_name] = attr

    def get_attribute(self, var_name):
        return self.attribute_map[var_name]

    def add_dependency(self, pre, post):
        """
        add dependency to the dependency list of the scheme

        Args:
            pre(set): attributes that initiate the FD (left of the arrow)
            post(set): attributes that are determined by the FD (right of the arrow)
        """
        for i in chain(pre, post):
            if i not in self.attributes:
                # exception when an attribute is used that is not in the list of attributes of the dependency
                raise Exception(f"Attribute {i} does not exist")
        self.dependencies.append((set(pre), set(post)))

    def remove_dependency(self, pre, post):
        """
        remove dependency from the dependency list of the scheme

        Args:
            pre(str): attributes that initiate the FD (left of the arrow)
            post(str): attributes that are determined by the FD (right of the arrow)
        """
        for i in chain(pre, post):
            if i not in self.attributes:
                # exception when an attribute is used that is not in the list of attributes of the dependency
                raise Exception(f"Attribute {i} does not exist")
        self.dependencies.remove((set(pre), set(post)))

    def get_attr_closure(self, attr):
        """
        get the close of the given attribute

        Args:
            attr(str): the name of the attribute to calculate the closure for

        Returns:
            set: the closure of the attribute
        """
        # closure set is build up iteratively, until it does not expand anymore
        closure = set(attr)
        # set of previous iteration
        last = set()
        while closure != last:
            last = closure.copy()
            # check all FDs whether their initiators are part of the closure
            # and add closure of the respective FD to the calculating closure
            for dep in self.dependencies:
                left, right = dep
                if left and left.issubset(closure):
                    closure.update(right)
        return closure

    def attribute_combinations(self, attributeSet: Set):
        """
        generator for keys
        """
        for i in range(1, len(attributeSet) + 1):
            for keys in combinations(attributeSet, i):
                yield keys

    def find_candidate_keys(self, verbose: bool = False, genEx: bool = False):
        """
        find candidate keys of the scheme

        Args:
            verbose(bool): if True show the steps
        """
        generatedTasks = []
        ans = []
        # check closures of all attributes and attribute combinations iteratively
        # smaller candidate keys added first
        for keys in self.attribute_combinations(self.attributes):
            closure = self.get_attr_closure(keys)
            k = set(keys)
            if closure == self.attributes:
                # no subset of currently checked key is already in
                if not any([x.issubset(k) for x in ans]):
                    generatedTasks.append(
                        (
                            f"Es ist {k} ein Schlüsselkandidat. Also ist {self.attributes} voll funktional abhängig von {k}.",
                            True,
                        )
                    )
                    generatedTasks.append(
                        (
                            f"Die Attributhülle von {k} ist {self.attributes}. Aus diesem Grund ist {self.attributes} voll funktional abhängig von {k}.",
                            False,
                        )
                    )

                    if verbose:
                        print(f"found candidate keys {k}")
                    ans.append(k)
                else:
                    generatedTasks.append(
                        (
                            f"Es ist {k} ein Superschlüssel, aber kein Schlüsselkandidat.",
                            True,
                        )
                    )
                    generatedTasks.append(
                        (
                            f"Es ist {k} ein Superschlüssel. Also ist {self.attributes} voll funktional abhängig von {k}.",
                            False,
                        )
                    )
            else:
                generatedTasks.append(
                    (f"Es ist {k} weder Superschlüssel noch Schlüsselkandidat.", True)
                )
                if len(k) <= 2:
                    generatedTasks.append((f"Aus {k} leitet man {closure} ab.", True))

        if genEx:
            print(f"=======================================")
            print(
                f"Aussagen zum Finden von Schlüsselkandidaten und Berechnen von Attributhüllen:"
            )
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return ans

    def isFDinBCNF(self, fd):
        """
        test whether the given fd is in BCNF

        Returns:
            bool: True if the left side of the functional dependency is a superkey
        """
        left, right = fd
        # do a super key check for the left side
        leftIsSuperKey = self.isSuperKey(left) or (left >= right)
        return leftIsSuperKey

    def isSuperKey(self, attrSet):
        """
        check wether the given attribute Set is a superkey

        Args:
            attrSet(Set): the set of attributes to check

        Returns:
            bool: True if the attributeSet is a super key
        """
        closure_left = self.get_attr_closure(attrSet)
        return closure_left == self.attributes

    def isIdentical(self, fdsetToCompare):
        """
        tests whether a given second fdset has the same attributes and fds as self
        """
        # check whether attributes are same
        if self.attributes != fdsetToCompare.attributes:
            return False

        # check whether all self dependencies are contained in compareFDSet dependencies
        for selfPre, selfPost in self.dependencies:
            found = False
            for comparePre, comparePost in fdsetToCompare.dependencies:
                if selfPre == comparePre and selfPost == comparePost:
                    found = True
                    break
            if not found:
                return False

        # check whether all compareFDSet dependencies are contained in self dependencies
        for comparePre, comparePost in self.dependencies:
            found = False
            for selfPre, selfPost in fdsetToCompare.dependencies:
                if selfPre == comparePre and selfPost == comparePost:
                    found = True
                    break
            if not found:
                return False

        return True

    def isBCNF(self, verbose: bool = False):
        """
        tests whether i am  in BCNF:
            every left side of every dependency is a superkey
        """
        result = True
        for fd in self.dependencies:
            fdInBCNF = self.isFDinBCNF(fd)
            result = result and fdInBCNF
            if not result:
                if verbose:
                    print(f"fd {fd} is NOT in BCNF")
                return False
            if verbose:
                print(f"fd {fd} is in BCNF")

        return result

    def getNonBCNF(self):
        """
        get first non BCNF dependency from my dependencies
        """
        for fd in self.dependencies:
            if not self.isFDinBCNF(fd):
                return fd
        return None

    def decompose2(self, verbose: bool = False, genEx: bool = False):
        """
        decomposition algorithm according to DBIS-VL
        Source: https://dbis.rwth-aachen.de/dbis-vl/RelDesign#page=82

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """

        # https://en.wikipedia.org/wiki/Linear_A version of Algorithm ...

        generatedTasks = []
        step = 0

        self.isdecomposed = True
        fds = FunctionalDependencySet()
        fds.attributes = self.attributes.copy()
        fds.dependencies = self.dependencies.copy()
        fds.completeFDsetToClosure(verbose=verbose)
        not_bcnf = [fds]
        bcnf = []
        while not_bcnf:
            fds = not_bcnf.pop(0)
            #
            if fds.isBCNF(verbose=verbose):
                generatedTasks.append(
                    (f"Die Abhängigkeitsmenge {fds} ist in BCNF.", True)
                )
                bcnf.append(fds.attributes)
                if verbose:
                    print(f"fdset {fds} is in BCNF")
            else:
                generatedTasks.append(
                    (f"Die Abhängigkeitsmenge {fds} ist in BCNF.", False)
                )
                if verbose:
                    print(f"fdset {fds} is not yet in BCNF")
                new_fds1 = FunctionalDependencySet()
                new_fds2 = FunctionalDependencySet()
                for dep in fds.dependencies:
                    left, right = dep
                    if (
                        (fds.get_attr_closure(left) != fds.attributes)
                        and (left != right)
                        and (len(left.intersection(right)) == 0)
                    ):
                        step += 1
                        generatedTasks.append(
                            (
                                f"In Schritt {step} zerlegen wir entlang der Abhängigkeit {dep}.",
                                True,
                            )
                        )
                        if verbose:
                            print(f"decompose along the dependency {dep}")

                        # create new fdsets along the dependency we decompose with
                        new_fds1.attributes = left | right
                        new_fds2.attributes = fds.attributes - right
                        # find dependencies that belong to the new fdsets
                        new_fds1.dependencies = [
                            fd
                            for fd in fds.dependencies
                            if (fd[0] | fd[1]) <= new_fds1.attributes
                        ]
                        new_fds2.dependencies = [
                            fd
                            for fd in fds.dependencies
                            if (fd[0] | fd[1]) <= new_fds2.attributes
                        ]
                        # new_fds2.dependencies = new_fds2.dependencies + [(fd[0], fd[1].intersection(new_fds2.attributes)) for fd in fds.dependencies if fd[0] <= new_fds2.attributes and len(fd[1].intersection(new_fds2.attributes)) != 0]
                        break
                    else:
                        generatedTasks.append(
                            (f"Wir zerlegen entlang der Abhängigkeit {dep}.", False)
                        )
                not_bcnf.append(new_fds1)
                not_bcnf.append(new_fds2)
                if verbose:
                    print(
                        f"new fdsets with attributes {new_fds1.attributes} and {new_fds2.attributes}"
                    )
        self.tables = bcnf

        generatedTasks.append(
            (f"Die Zerlegung enthält mehr als drei Relationen.", len(self.tables) > 3)
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zur Dekomposition:")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return bcnf

    def decompose(self, verbose: bool = False):
        """
        decomposition algorithm

        Args:
            verbose(bool): if True show steps of the decomposition
        """
        self.isdecomposed = True
        self.tables = [self.attributes]
        for dep in self.dependencies:
            left, right = dep
            for attr_set in self.tables:
                # newset contains the unity of attributes of the FD
                newset = left.symmetric_difference(right)
                # if newset is real subset, extra attributes still exist
                # --> need to break it up
                if newset.issubset(attr_set) and newset != attr_set:
                    if verbose:
                        print(
                            f"splitting {attr_set} into {attr_set.difference(right)} and {newset}"
                        )
                    # split attributes of the FD closure off the attribute set
                    attr_set.difference_update(right)

                    # add new BCNF set to list of attribute sets
                    self.tables.append(newset)
        return self.tables

    def decompose_all(self):
        ## Messy sets and tuples to get rid of duplicates, eew
        tables_possibilities = []

        for ordering in permutations(self.dependencies):
            tbl = [self.attributes.copy()]

            for dep in ordering:
                left, right = dep
                for attr_set in tbl:
                    newset = left.symmetric_difference(right)
                    if newset.issubset(attr_set) and newset != attr_set:
                        attr_set.difference_update(right)
                        tbl.append(newset)

            tbl = [tuple(x) for x in tbl]
            tables_possibilities.append(tuple(tbl))

        return set(tables_possibilities)

    def is_lossy(self):
        """
        check for lossyness

        Returns:
            bool: True if if one of my dependencies is not preserved
        """
        if not self.isdecomposed:
            raise Exception("Can't tell if lossy if the FD hasn't been decomposed yet")
        for dep in self.dependencies:
            if not self.is_preserved(dep):
                return True
        return False

    def is_preserved(self, dep):
        """
        check whether the given dependency is preserved

        Args:
            dep(): the dependency to check

        Returns:
            bool: True if the dependency is preserved
        """
        left, right = dep
        pre = left.symmetric_difference(right)
        for attr_set in self.tables:
            if pre == attr_set:
                return True
        return False

    def calculate_fds_in_subset(self, subset):
        """
        calculate all dependencies in a subset. Also includes dependencies for which
        attribute parts are missing because they are not in the subset. Does not include
        original dependencies that have lost all there attributes in precondition or closure

        """
        subset_dependencies = []
        for dep in self.dependencies:
            new_dep_pre = set()
            new_dep_post = set()
            left, right = dep
            # check whether attributes occur in pre or post of the original FD
            for attr in left:
                if attr in subset:
                    new_dep_pre.add(attr)
            for attr in right:
                if attr in subset:
                    new_dep_post.add(attr)
            # only add new dependency if none of both sides is empty
            if new_dep_pre != set() and new_dep_post != set():
                subset_dependencies.append((new_dep_pre, new_dep_post))
        return subset_dependencies

    def is2NF(self):
        """
        calculates whether the FD set is in 2NF: Every attribute has to depend on the whole CK.
        Check for every attribute whether there is a part of any of the CKs which has the attribute in its closure
        """
        ckeys = self.find_candidate_keys()

        # create array of all real subsets of all ckeys
        allsubsets = []
        for ckey in ckeys:
            for i in range(1, len(ckey)):
                allsubsets.extend([set(c) for c in combinations(ckey, i)])

        # create set of all attributes that are part of a candidate key
        keyattributes = set().union(*ckeys)

        # check every non-ck-attribute
        for attr in self.attributes:
            if attr in keyattributes:
                continue

            for subset in allsubsets:
                subset_closure = self.get_attr_closure(subset)
                if attr in subset_closure:
                    return False
        return True

    def is3NF(self):
        """
        calculates whether the FD set is in 3NF: for non-trivial dependencies X(set)->A(attribute) either X is a superkey or A is part of a candidate key
        """
        ckeys = self.find_candidate_keys()
        # create set of all attributes that are part of a candidate key
        keyattributes = set().union(*ckeys)

        # check 3NF condittion for every dependency
        for left, right in self.dependencies:
            if set(right).issubset(set(left)) or self.isSuperKey(left):
                continue
            for attr in right:
                if attr not in keyattributes:
                    return False
        return True

    def generate_cluster(self, shape: str = "box", indent: str = "  "):
        """
        graphviz digraph subgraph (cluster) generation for this functional dependency set

        Args:
            shape(str): the shape to use - default: box
            indent(str): indentation - default: two spaces
        Return:
            str: graphviz markup
        """
        markup = ""
        # sort dependencies by largest pre
        dependencies = self.dependencies.copy()
        dependencies.sort(key=lambda dep: len(dep[0]), reverse=True)

        # collect attributes that are only on the right side
        only_post = self.attributes.copy()
        # generate clusters
        cluster_markup = ""
        for dep in dependencies:
            pre, post = dep
            only_post -= pre
            cluster_name = "".join(sorted(pre))
            cluster_markup += f"{indent}subgraph cluster_{cluster_name}{{\n"
            cluster_markup += f'{indent} label="{cluster_name}"\n'
            for attrVar in sorted(pre):
                attr = self.attribute_map[attrVar]
                cluster_markup += (
                    f'{indent}{indent}{attrVar} [shape={shape} label="{attr}"]\n'
                )
            cluster_markup += f"{indent}}}\n"

        # generate arrows
        arrow_markup = ""
        for dep in dependencies:
            pre, post = dep
            for attrVar in sorted(post):
                arrow_markup += f"{indent}{sorted(pre)[0]}->{attrVar}\n"

        # create markup for only post attributes
        only_post_markup = ""
        for attrVar in sorted(only_post):
            attr = self.attribute_map[attrVar]
            only_post_markup += f'{indent}{attrVar} [shape={shape} label="{attr}"]\n'

        # concatenate markup
        markup += only_post_markup
        markup += cluster_markup
        markup += arrow_markup
        return markup

    def as_graphviz(self, withCluster: bool = True):
        """

        convert me to a graphviz markup e.g. to try out in

        http://magjac.com/graphviz-visual-editor/
        or
        http://diagrams.bitplan.com

        Return:
            str: the graphviz markup for this functional DependencySet
        """
        markup = f"#generated by {__file__} on {self.isodate}\n"
        markup += "digraph functionalDependencySet{"
        # add title see https://stackoverflow.com/a/6452088/1497139
        markup += f"""
  // title
  labelloc="t";
  label="{self.title}"
"""
        if not withCluster:
            markup += "// Attribute variables \n"
            for attrVar in sorted(self.attributes):
                attr = self.attribute_map[attrVar]
                markup += f"""  {attrVar} [ shape=box label="{attr}"] \n"""
        else:
            markup += self.generate_cluster()
        markup += "}"
        return markup

    def left_reduction(self, verbose: bool = False, genEx: bool = False):
        """
        executes a left reduction on the dependencies from this fdset

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """

        generatedTasks = []
        reductionCounter = 0

        if genEx:
            self.notation = Notation.math

        remaining_deps = self.dependencies.copy()
        while remaining_deps:
            dep = remaining_deps.pop(0)
            pre, post = dep
            wasDepAlreadyReduced = False
            for attr in sorted(pre):
                if post <= self.get_attr_closure(pre - {attr}):
                    generatedTasks.append(
                        (
                            f"Das Attribut {attr} kann aus der Abhängigkeit {dep} reduziert werden.",
                            True,
                        )
                    )
                    if not wasDepAlreadyReduced:
                        generatedTasks.append(
                            (
                                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann nicht reduziert werden, da die Attributhülle von {Set.stringify_set(post, self.notation)} nicht alle Attribute aus {Set.stringify_set(pre, self.notation)} enthält.",
                                False,
                            )
                        )
                        generatedTasks.append(
                            (
                                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann reduziert werden, da die Attributhülle von {Set.stringify_set(post, self.notation)} nicht alle Attribute aus {Set.stringify_set(pre, self.notation)} enthält.",
                                False,
                            )
                        )
                        reductionCounter += 1
                    else:
                        generatedTasks.append(
                            (
                                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} wird mehrmals reduziert.",
                                True,
                            )
                        )
                    if verbose:
                        print(
                            f"removed {attr} from lhs of dependency {dep}, new lhs {(pre - {attr})}"
                        )
                    self.remove_dependency(pre, post)
                    self.add_dependency(pre - {attr}, post)
                    pre = pre - {attr}
                    wasDepAlreadyReduced = True
                else:
                    generatedTasks.append(
                        (
                            f"Das Attribut {attr} kann aus der Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} reduziert werden.",
                            False,
                        )
                    )
            if not wasDepAlreadyReduced:
                generatedTasks.append(
                    (
                        f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann nicht reduziert werden.",
                        True,
                    )
                )
            else:
                generatedTasks.append(
                    (
                        f"Die Linksreduktion beinhaltet die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])}.",
                        True,
                    )
                )

        generatedTasks.append(
            (
                f"Es kann nur eine der ursprünglichen funktionalen Abhängigkeiten reduziert werden.",
                reductionCounter == 1,
            )
        )
        generatedTasks.append(
            (
                f"Es können mehr als zwei der ursprünglichen funktionalen Abhängigkeiten reduziert werden.",
                reductionCounter > 2,
            )
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zur Linksreduktion (Schritt 1a):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

    def isCorrectLeftReduction(self, proposedReduction, verbose: bool = False):
        """
        Checks a given left reduction of self for correctness

        Args:
            proposedReduction(FunctionalDependencySet): The proposed left reduction of self, the original FDSet
            verbose(bool): Optional argument for detailed output
        Return:
            bool: Is the left reduction correct
        """
        if verbose:
            print("CHECKING: Is the proposed left reduction of self correct:\n")
            print("1. Is the amount of dependencies of the solution the same as self:")

        # equal amount of dependencies
        if len(proposedReduction.dependencies) != len(self.dependencies):
            if verbose:
                print(
                    f"FAILURE: The solution had a differing amount of dependencies: \n \t Task: {len(self.dependencies)}\n\tSolution: {len(proposedReduction.dependencies)}"
                )
            return False
        if verbose:
            print(
                f"Both the task and the solution have {len(self.dependencies)} dependencies\n"
            )
            print(
                f"2. Checking whether the solution dependencies could result from a task dependency:"
            )

        # equal right sides of dependencies
        # left sides are subsets of original left sides
        for propDep in proposedReduction.dependencies:
            leftProp, rightProp = propDep
            if not leftProp:
                if verbose:
                    print(
                        f"FAIL: One of the dependencies has an empty left side. This cannot happen."
                    )
                return False
            isCorrect = False
            for oriDep in self.dependencies:
                leftOri, rightOri = oriDep
                if verbose:
                    print(
                        f"\tComparing solution dependency {leftProp} -> {rightProp} with task dependency {leftOri} -> {rightOri}"
                    )
                if rightProp == rightOri and leftProp <= leftOri:
                    isCorrect = True
                    if verbose:
                        print(
                            f"\tThe solution dependency can result from the task dependency"
                        )
                    break
            if not isCorrect:
                if verbose:
                    print(
                        f"FAILURE: The dependency {leftProp} -> {rightProp} can't result from any task dependency"
                    )
                return False
        if verbose:
            print(f"All solution dependencies can result from the task dependencies\n")
            print(
                f"3. Checking whether the closures of all attribute subsets have remained the same:"
            )

        # check whether attribute closures of all attribute subsets are still the same
        if not self.isAllAttributeClosuresSame(proposedReduction, verbose):
            return False
        if verbose:
            print(f"4. Checking whether the proposed reduction is complete:")

        # reduction is complete: reduction of the reduction remains the same
        doubleReduction = proposedReduction.copy()
        doubleReduction.left_reduction()
        if not doubleReduction.isIdentical(proposedReduction):
            if verbose:
                print(f"FAILURE: The proposed reduction is not complete")
            return False
        if verbose:
            print(f"The proposed reduction is complete\n")
            print(f"SUCCESS: The left reduction is correct")

        return True

    def isAllAttributeClosuresSame(self, fdsetToCompare, verbose: bool = False):
        """
        check whether attribute closures of all attribute subsets are still the same
        """
        combs = list(self.attribute_combinations(self.attributes))
        for comb in combs:
            if verbose:
                print(f"\tChecking set of attributes: {set(comb)}")
            if self.get_attr_closure(comb) != fdsetToCompare.get_attr_closure(comb):
                if verbose:
                    print(
                        f"FAILURE: The closure for the subset {set(comb)} changed from {self.get_attr_closure(comb)} to {fdsetToCompare.get_attr_closure(comb)}"
                    )
                return False
        if verbose:
            print(f"All subsets of attributes have the same closure\n")

        return True

    def completeFDsetToClosure(self, verbose: bool = False):
        """
        generates the closure F^+ of an FD set F
        """
        combs = list(self.attribute_combinations(self.attributes))
        for comb in combs:
            if verbose:
                print(f"\tChecking set of attributes: {set(comb)}")
            closure = self.get_attr_closure(comb)
            if verbose:
                print(f"Closure of {set(comb)} is {closure}")
            rhs_combs = list(self.attribute_combinations(closure))
            for rhs_comb in rhs_combs:
                self.dependencies.append((set(comb), set(rhs_comb)))
                if verbose:
                    print(f"adding dependency {set(comb)}, {set(rhs_comb)}")
        return

    def right_reduction(self, verbose: bool = False, genEx: bool = False):
        """
        executes a right reduction on the dependencies from this fdset

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """
        if genEx:
            self.notation = Notation.math

        generatedTasks = []
        reductionCounter = 0
        remaining_deps = self.dependencies.copy()
        while remaining_deps:
            dep = remaining_deps.pop(0)
            pre, post = dep
            wasDepAlreadyReduced = False
            for attr in sorted(post):
                self.remove_dependency(pre, post)
                self.add_dependency(pre, post - {attr})
                if {attr} <= set(self.get_attr_closure(pre)):
                    if not wasDepAlreadyReduced:
                        generatedTasks.append(
                            (
                                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann reduziert werden, da die Attributhülle von {post} nicht alle Attribute aus {pre} enthält.",
                                False,
                            )
                        )
                        generatedTasks.append(
                            (
                                f"Das Attribut {attr} kann aus der Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} reduziert werden.",
                                True,
                            )
                        )
                        generatedTasks.append(
                            (
                                f"Das Attribut {attr} kann aus der Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} reduziert werden, da bei Entfernen von {attr} von der rechten Seite der Abhängigkeit die Attributhülle von {pre} immer noch {attr} enthält.",
                                True,
                            )
                        )
                        generatedTasks.append(
                            (
                                f"Das Attribut {attr} kann aus der Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} reduziert werden, da bei Entfernen von {attr} von der rechten Seite der Abhängigkeit die Attributhülle von {post - {attr}} immer noch {attr} enthält.",
                                True,
                            )
                        )
                        reductionCounter += 1
                    else:
                        generatedTasks.append(
                            (
                                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann mehrmals reduziert werden.",
                                True,
                            )
                        )
                    if verbose:
                        print(
                            f"removed {attr} from rhs of dependency {dep}, new rhs {(post - {attr})}"
                        )
                    post = post - {attr}
                    wasDepAlreadyReduced = True
                else:
                    generatedTasks.append(
                        (
                            f"Das Attribut {attr} kann aus der Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} reduziert werden.",
                            False,
                        )
                    )
                    self.remove_dependency(pre, post - {attr})
                    self.add_dependency(pre, post)
            if wasDepAlreadyReduced:
                generatedTasks.append(
                    (
                        f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} wird insgesamt zu {self.stringify_dependencies(fdsToStringify=[(pre, post)])} reduziert.",
                        True,
                    )
                )
            else:
                generatedTasks.append(
                    (
                        f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])} kann nicht reduziert werden.",
                        True,
                    )
                )

        generatedTasks.append(
            (
                f"Es kann nur eine der ursprünglichen funktionalen Abhängigkeiten reduziert werden.",
                reductionCounter == 1,
            )
        )
        generatedTasks.append(
            (
                f"Es können mehr als zwei der ursprünglichen funktionalen Abhängigkeiten reduziert werden.",
                reductionCounter > 2,
            )
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zur Rechtsreduktion (Schritt 1b):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

    def isCorrectRightReduction(self, proposedReduction, verbose: bool = False):
        """
        Checks a given right reduction of self for correctness

        Args:
            self: an FDSet after left reduction, but before right reduction
            proposedReduction(FunctionalDependencySet): The proposed right reduction of self
            verbose(bool): Optional argument for detailed output
        Return:
            bool: Is the right reduction correct
        """
        if verbose:
            print("CHECKING: Is the proposed right reduction of self correct:\n")
            print("1. Is the amount of dependencies of the solution the same as self:")

        # equal amount of dependencies
        if len(proposedReduction.dependencies) != len(self.dependencies):
            if verbose:
                print(
                    f"FAILURE: The solution had a differing amount of dependencies: \n \t Task: {len(self.dependencies)}\n\tSolution: {len(proposedReduction.dependencies)}"
                )
            return False
        if verbose:
            print(
                f"Both the task and the solution have {len(self.dependencies)} dependencies\n"
            )
            print(
                f"2. Checking whether the solution dependencies could result from a task dependency:"
            )

        # equal left sides of dependencies
        # right sides are subsets of original right sides
        for propDep in proposedReduction.dependencies:
            leftProp, rightProp = propDep
            if not leftProp:
                if verbose:
                    print(
                        f"FAIL: One of the dependencies has an empty left side. This cannot happen."
                    )
                return False
            isCorrect = False
            for oriDep in self.dependencies:
                leftOri, rightOri = oriDep
                if verbose:
                    print(
                        f"\tComparing solution dependency {leftProp} -> {rightProp} with task dependency {leftOri} -> {rightOri}"
                    )
                if leftProp == leftOri and rightProp <= rightOri:
                    isCorrect = True
                    if verbose:
                        print(
                            f"\tThe solution dependency can result from the task dependency"
                        )
                    break
            if not isCorrect:
                if verbose:
                    print(
                        f"FAILURE: The dependency {leftProp} -> {rightProp} can't result from any task dependency"
                    )
                return False
        if verbose:
            print(f"All solution dependencies can result from the task dependencies\n")
            print(
                f"3. Checking whether the closures of all attribute subsets have remained the same:"
            )

        # check whether attribute closures of all attribute subsets are still the same
        if not self.isAllAttributeClosuresSame(proposedReduction, verbose):
            return False
        if verbose:
            print(f"4. Checking whether the proposed reduction is complete:")

        # reduction is complete: reduction of the reduction remains the same
        doubleReduction = proposedReduction.copy()
        doubleReduction.right_reduction()
        if not doubleReduction.isIdentical(proposedReduction):
            if verbose:
                print(f"FAILURE: The proposed reduction is not complete")
            return False
        if verbose:
            print(f"The proposed reduction is complete\n")
            print(f"SUCCESS: The right reduction is correct")

        return True

    def remove_empty_fds(self, verbose: bool = False, genEx: bool = False):
        """
        remove empty fds of form "A → {}" from this fdset

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """
        removeCounter = 0
        deps_copy = self.dependencies.copy()
        for dep in deps_copy:
            pre, post = dep
            if len(post) == 0:
                removeCounter += 1
                if verbose:
                    print(f"removed {dep} because rhs is empty")
                self.remove_dependency(pre, post)

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Entfernen leerer FDs (Schritt 1c):")
            print(
                (
                    f"Es werden zwei Abhängigkeiten entfernt, da sie eine leere rechte Seite haben.",
                    removeCounter == 2,
                )
            )
            print(
                (
                    f"Es werden zwei Abhängigkeiten entfernt, da sie eine leere linke Seite haben.",
                    False,
                )
            )
            print(
                (f"Es werden mehr als zwei Abhängigkeiten entfernt.", removeCounter > 2)
            )
            print(f"=======================================")

    def isCorrectRemovingEmptyFDs(self, proposedSolution, verbose: bool = False):
        """
        Checks a given removing of empty fds of self for correctness

        Args:
            self: an FDSet after removing empty fds
            proposedSolution(FunctionalDependencySet): The proposed solution of removing fds of self
            verbose(bool): Optional argument for detailed output
        Return:
            bool: Is the solution correct
        """
        if verbose:
            print(
                "CHECKING: Is the proposed removal of empty dependencies of self correct:\n"
            )
            print(
                "1. Does the solution have an equal or less amount of dependencies than self:"
            )

        # Equal amount of dependencies
        if len(proposedSolution.dependencies) <= len(self.dependencies):
            if verbose:
                print(
                    f"FAILURE: The solution had more dependencies: \n \t Task: {len(self.dependencies)}\n\tSolution: {len(proposedSolution.dependencies)}"
                )
        if verbose:
            print(
                f"The proposed solution has equal or less dependencies ({len(proposedSolution.dependencies)}) than self ({len(self.dependencies)})\n"
            )
            print(
                f"2. Checking if every complete dependency in self is in the proposed solution:"
            )

        # check if the correct dependencies remain
        for dep in self.dependencies:
            left, right = dep
            if right != Set() and (left, right) not in proposedSolution.dependencies:
                if verbose:
                    print(
                        f"FAILURE: Dependency {left} -> {right} is not in the proposed solution."
                    )
                    return False
            elif verbose:
                print(f"\tThe dependency {left} -> {right} is in the proposed solution")
        if verbose:
            print(f"All complete dependencies of self are in the proposed solution.\n")
            print(f"3. Check if all empty dependencies are removed:")

        fds = self.copy()
        fds.remove_empty_fds()
        if not fds.isIdentical(proposedSolution):
            if verbose:
                print(f"FAILURE: Not all empty dependencies were removed")
            return False

        if verbose:
            print(f"All empty dependencies have been removed.")
            print(f"SUCCESS: The proposed solution is correct.")

        return True

    def combine_fds(self, verbose: bool = False, genEx: bool = False):
        """
        combines fds with equal left sides

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """
        if genEx:
            self.notation = Notation.math

        generatedTasks = []
        combined_dependencies = []
        combineCounter = 0
        deps_copy = self.dependencies.copy()
        while self.dependencies:
            pre, post = self.dependencies.pop(0)
            new_post = post
            deps_copy = self.dependencies.copy()
            for dep in deps_copy:
                left, right = dep
                if left == pre:
                    combineCounter += 1
                    new_post = new_post | right
                    if verbose:
                        print(
                            f"combined dependencies {dep} and {(pre, post)} to new dependency {(pre, new_post)}"
                        )
                    self.remove_dependency(left, right)
                    generatedTasks.append(
                        (
                            f"Die Abhängigkeiten {self.stringify_dependencies(fdsToStringify=[dep])} und {self.stringify_dependencies(fdsToStringify=[(pre, post)])} werden zu {self.stringify_dependencies(fdsToStringify=[(pre, new_post)])} zusammengefasst.",
                            True,
                        )
                    )
                    generatedTasks.append(
                        (
                            f"Die Abhängigkeiten {self.stringify_dependencies(fdsToStringify=[dep])} und {self.stringify_dependencies(fdsToStringify=[(pre, new_post)])} werden zu {self.stringify_dependencies(fdsToStringify=[(pre, post)])} zusammengefasst.",
                            False,
                        )
                    )
            combined_dependencies.append((pre, new_post))
        self.dependencies = combined_dependencies
        generatedTasks.append(
            (
                f"Es werden an zwei oder mehr Stellen Abhängigkeiten zusammengefasst.",
                combineCounter >= 2,
            )
        )

        for dep in self.dependencies:
            pre, post = dep
            generatedTasks.append(
                (
                    f"Die kanonische Überdeckung enthält die funktionale Abhängigkeit {self.stringify_dependencies(fdsToStringify=[dep])}.",
                    True,
                )
            )
            for attr in post:
                generatedTasks.append(
                    (
                        f"Die kanonische Überdeckung enthält die funktionale Abhängigkeit {self.stringify_dependencies(fdsToStringify=[(pre, post - {attr})])}.",
                        False,
                    )
                )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Zusammenfassen von FDs (Schritt 1d):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

    def getFDsByLeftSide(self, left: Set, dependencies: list):
        filtered = list(filter(lambda dependecy: dependecy[0] == left, dependencies))
        return filtered

    def isCorrectCombinationOfDependencies(
        self, proposedSolution, verbose: bool = False
    ):
        """
        Checks a given removing of empty fds of self for correctness

        Args:
            self: an FDSet after combination of dependencies
            proposedSolution(FunctionalDependencySet): The proposed solution of combination of dependencies of self
            verbose(bool): Optional argument for detailed output
        Return:
            bool: Is the solution correct
        """
        if verbose:
            print(
                "CHECKING: Is the proposed combination of dependencies of self correct:\n"
            )
            print(
                "1. Does the solution have an equal or less amount of dependencies than self:"
            )

        # Equal amount of dependencies
        if len(proposedSolution.dependencies) <= len(self.dependencies):
            if verbose:
                print(
                    f"FAILURE: The solution had more dependencies: \n\tTask: {len(self.dependencies)}\n\tSolution: {len(proposedSolution.dependencies)}"
                )
        if verbose:
            print(
                f"The proposed solution has equal or less dependencies ({len(proposedSolution.dependencies)}) than self ({len(self.dependencies)})\n"
            )
            print(
                f"2. Checking if every combined dependency in self is in the proposed solution:"
            )

        # check if the correct dependencies remain
        dependencies = self.dependencies.copy()
        for dep in proposedSolution.dependencies:
            left, originalRight = dep
            right = originalRight.copy()
            leftDeps = self.getFDsByLeftSide(left, dependencies)
            for leftDep in leftDeps:
                if leftDep[1] <= originalRight:
                    dependencies.remove(leftDep)
                    right -= leftDep[1]
                else:
                    if verbose:
                        print(
                            f"FAILURE: Dependecy {left} -> {leftDep[1]} is not part of the combined dependency {left} -> {right}."
                        )
                    return False
                if verbose:
                    print(
                        f"\tThe dependency {left} -> {right} cannot be combined further."
                    )
            if len(right) > 0:
                if verbose:
                    print(
                        f"FAILURE: Right side {dep[1]} contains too many attributes {right}."
                    )
                return False
        if len(dependencies) > 0:
            if verbose:
                print("FAILURE: Some dependencies have not made it into the solution.")
            return False
        if verbose:
            print(f"SUCCESS: The proposed solution is correct.")
        return True

    def canonical_cover(self, verbose: bool = False, genEx: bool = False):
        """
        determines the canonical cover of this fdset

        4 substeps with respective functions

        https://git.rwth-aachen.de/i5/teaching/dbis-vl/-/raw/main/6-RelDesign/6-RelationaleEntwurfstheorie.pdf#page=39

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false
        """
        self.left_reduction(verbose, genEx)
        self.right_reduction(verbose, genEx)
        if verbose:
            print(f"after right reduction:")
            for fd in self.dependencies:
                print(fd)
        self.remove_empty_fds(verbose, genEx)
        self.combine_fds(verbose, genEx)
        if verbose:
            print(f"canonical cover:")
            for fd in self.dependencies:
                print(fd)

    def isCorrectCanonicalCover(self, proposedSolution, verbose: bool = False):
        """
        Checks if a give FunctionalDependencySet is a canonical cover of self

        Args:
            proposedSolution(FunctionalDependencySet): The proposed canoncial cover of self
            verbose(bool): if True shows steps for debugging
        Return:
            bool: Correct?
        """
        if verbose:
            print("CHECKING: Is the proposed canonical cover of self correct:\n")
            print("1. Do self and proposedSolution have the same closures:")
        if not proposedSolution.isAllAttributeClosuresSame(self, verbose=verbose):
            if verbose:
                print(
                    "FAILURE: The closures of self and proposedSolution are different."
                )
        if verbose:
            print("2. Checking if the canonical cover is complete:")

        doubleCover = proposedSolution.copy()
        doubleCover.canonical_cover(verbose=verbose)
        if proposedSolution.isIdentical(doubleCover):
            if verbose:
                print("SUCCESS: The proposedSolution is correct")
            return True

        if verbose:
            print("FAILURE: The proposedSolution is an incomplete canonical cover")
        return False

    def create_new_fdsets(self, verbose: bool = False, genEx: bool = False):
        """
        create fdsets from the dependencies resulting from the canonical cover

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false

        Return:
            list[FunctionalDependencySet]: list of fdsets created from the dependencies resulting from the canonical cover
        """
        if genEx:
            self.notation = Notation.math

        deps = self.dependencies.copy()
        existsDepWithMultipleFDs = False
        generatedTasks = []
        i = 1
        new_fdsets = []
        while deps:
            tmp = deps.pop(0)
            pre, post = tmp
            new_attributes = pre | post
            new_deps = [tmp]
            for dep in deps:
                left, right = dep
                if left | right <= new_attributes:
                    new_deps.append(dep)
            fds = FunctionalDependencySet(new_attributes, "R" + str(i))
            if verbose:
                print(f"creating a new fdset with attributes {new_attributes}")
            generatedTasks.append(
                (
                    f"Es wird eine neue Relation mit Attributmenge {new_attributes} erstellt.",
                    True,
                )
            )
            i += 1
            for dep in new_deps:
                left, right = dep
                fds.add_dependency(left, right)
            if len(fds.dependencies) > 1:
                existsDepWithMultipleFDs = True
                generatedTasks.append(
                    (
                        f"Es gibt eine Abhängigkeit, die in mehreren Relationen enthalten ist.",
                        True,
                    )
                )
            new_fdsets.append(fds)

        if existsDepWithMultipleFDs:
            generatedTasks.append(
                (
                    f"Es gibt eine Abhängigkeit, die in mehreren Relationen enthalten ist.",
                    True,
                )
            )
        else:
            generatedTasks.append(
                (
                    f"Es gibt eine Abhängigkeit, die in mehreren Relationen enthalten ist.",
                    False,
                )
            )

        generatedTasks.append(
            (
                f"Es wird eine neue Relation pro Abhängigkeit in der kanonischen Überdeckung erstellt.",
                True,
            )
        )
        generatedTasks.append(
            (
                f"Es wird eine neue Relation pro Abhängigkeit in der ursprünglichen Menge funktionaler Abhängigkeiten erstellt.",
                False,
            )
        )
        generatedTasks.append(
            (
                f"Es wird für jeden Schlüsselkandidaten eine neue Relation erstellt.",
                False,
            )
        )
        generatedTasks.append(
            (
                f"Es werden insgesamt drei neue Relationen erstellt.",
                len(new_fdsets) == 3,
            )
        )
        generatedTasks.append(
            (
                f"Die Abhängigkeit {self.stringify_dependencies(fdsToStringify=[fds.dependencies[0]])} ist in keiner neuen Relation enthalten.",
                False,
            )
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Hinzufügen von Relationen (Schritt 2):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return new_fdsets

    def isCorrectCreationOfNewFDS(self, fdsets: list, verbose: bool = False):
        """
        Checks if fdsets were correctly created from canonical cover

        Args:
            fdsets(list): List of fds
            verbose(bool): Debugging tool
        Return:
            bool: Correct?
        """
        if verbose:
            print("CHECKING: Is the proposed list of fdsets a correct solution:\n")
            print("1. Are there more new sets than dependencies:")
        if len(fdsets) > len(self.dependencies):
            if verbose:
                print(
                    f"FAILURE: The number of fdsets, {len(fdsets)}, if bigger than the number of dependencies, {len(self.dependencies)}."
                )

        if verbose:
            print("2. Have the dependencies and attributes been correctly transfered:")
        depsCopy = [0] * len(self.dependencies)
        for fds in fdsets:
            for dep in fds.dependencies:
                left, right = dep
                if not left | right <= fds.attributes:
                    if verbose:
                        print(
                            f"FAILURE: The dependency, {left} -> {right}, has more attributes than {fds.attributes}"
                        )
                    return False
                if (left, right) in self.dependencies:
                    i = self.dependencies.index((left, right))
                    depsCopy[i] = 1
                else:
                    if verbose:
                        print(
                            f"FAILURE: The dependency, {left} -> {right}, is not in self.dependencies."
                        )
                    return False
        if numpy.prod(depsCopy) != 1:
            if verbose:
                print(
                    f"FAILURE: {len(depsCopy)} dependencies where not part of the solution."
                )
            return False
        if verbose:
            print("SUCCESS: The creation of fdsets was correct.")
        return True

    def synthesize(self, verbose: bool = False, genEx: bool = False):
        """
        synthesize algorithm

        see https://git.rwth-aachen.de/i5/teaching/dbis-vl/-/raw/main/6-RelDesign/6-RelationaleEntwurfstheorie.pdf#page=76
        and Kemper page 197

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false

        Return:
            list[FunctionalDependencySet]: list of synthesized fdsets deriving from this fdset
        """
        generatedTasks = []

        keys = self.find_candidate_keys(verbose=verbose, genEx=genEx)
        self.canonical_cover(verbose, genEx)
        fdsets = self.create_new_fdsets(verbose, genEx)
        fdsets_before_key_relation = fdsets.copy()
        fdsets_with_key = self.create_optional_key_scheme(keys, fdsets, verbose, genEx)
        reduced_fdsets = self.remove_subset_relations(fdsets_with_key, verbose, genEx)

        generatedTasks.append(
            (
                f"Wir erhalten zum Schluss die gleiche Anzahl an Relationen wie vor Schritt 3.",
                len(fdsets_before_key_relation) == len(reduced_fdsets),
            )
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Endergebnis des Synthesealgorithmus (nach Schritt 4):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return reduced_fdsets

    def create_optional_key_scheme(
        self, keys, fdsets, verbose: bool = False, genEx: bool = False
    ):
        """
        creates a new fdset if key is not subset of any of the existing sets attributes

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false

        Return:
            list[FunctionalDependencySet]: The list of fdsets with relation that has key candidate of original scheme
        """
        generatedTasks = []

        for key in keys:
            for fds in fdsets:
                if set(key) <= fds.attributes:
                    generatedTasks.append(
                        (
                            f"Es braucht keine Schlüsselrelation hinzugefügt werden, da die Attribute von mindestens einem der {len(key) + 1} Schlüsselkandidaten in mindestens einer neuen Relation enthalten sind.",
                            False,
                        )
                    )
                    generatedTasks.append(
                        (
                            f"Wir können eine neue Schlüsselrelation mit der Attributmenge {set(keys[0])} hinzufügen.",
                            False,
                        )
                    )
                    generatedTasks.append(
                        (
                            f"Die Relation mit Attributmenge {fds.attributes} enthält alle Attribute eines Schlüsselkandidaten.",
                            True,
                        )
                    )
                    if genEx:
                        print(f"=======================================")
                        print(
                            f"Aussagen zum Hinzufügen einer Schlüsselrelation (Schritt 3):"
                        )
                        for task in generatedTasks:
                            print(task)
                        print(f"=======================================")
                    return fdsets
        generatedTasks.append(
            (
                f"Es muss eine neue Schlüsselrelation hinzugefügt werden, da keine aktuelle Relation die Attribute eines Schlüsselkandidaten enthält.",
                True,
            )
        )
        generatedTasks.append(
            (
                f"Die hinzuzufügende Schlüsselrelation ist in der Attributmenge eindeutig.",
                not (len(keys) > 1),
            )
        )
        key = set(keys[0])
        generatedTasks.append(
            (
                f"Wir können eine neue Schlüsselrelation mit der Attributmenge {key} hinzufügen.",
                True,
            )
        )
        fds = FunctionalDependencySet(key, "R" + str(len(fdsets) + 1))
        m = len(key) // 2
        # fds.add_dependency(sorted(key)[:m], sorted(key)[m:])
        fds.add_dependency(key, key)
        fdsets.append(fds)

        if verbose:
            print(f"adding a new fdset with attributes {key}")
        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Hinzufügen einer Schlüsselrelation (Schritt 3):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return fdsets

    def remove_subset_relations(
        self, fdsets, verbose: bool = False, genEx: bool = False
    ):
        """
        removes fdsets with attributes that are a subset of another fdset

        Args:
            verbose(bool): if True show steps
            genEx(bool): if True generate exercise tasks in form of sentences that can be either true or false

        Return:
            list[FunctionalDependencySet]: The reduced list of fdsets
        """
        generatedTasks = []
        removeCounter = 0

        if self.debug:
            print(fdsets)
        for fds in fdsets.copy():
            attributes = fds.attributes
            conflict = next(
                (
                    fdset
                    for fdset in fdsets
                    if fds.title != fdset.title and attributes <= fdset.attributes
                ),
                None,
            )
            if conflict is not None:
                fdsets.remove(fds)
                removeCounter += 1
                generatedTasks.append(
                    (
                        f"Die Relation mit Attributmenge {fds.attributes} wird entfernt.",
                        True,
                    )
                )
                if len(fds.dependencies) > 0:
                    generatedTasks.append(
                        (
                            f"Es muss die Relation entfernt werden, die die Abhängigkeit {fds.dependencies[0]} enthält.",
                            True,
                        )
                    )

                removeCounter += 1
                generatedTasks.append(
                    (
                        f"Die Relation mit Attributmenge {fds.attributes} wird entfernt.",
                        True,
                    )
                )
                if len(fds.dependencies) > 0:
                    generatedTasks.append(
                        (
                            f"Es muss die Relation entfernt werden, die die Abhängigkeit {fds.dependencies[0]} enthält.",
                            True,
                        )
                    )
                if verbose:
                    print(f"removing the fdset {fds}")
            else:
                generatedTasks.append(
                    (
                        f"Die Relation mit Attributmenge {fds.attributes} wird entfernt.",
                        False,
                    )
                )

        generatedTasks.append(
            (
                f"Es gibt Relationen, deren Attributmengen Teilmengen voneinander sind.",
                removeCounter > 0,
            )
        )

        if genEx:
            print(f"=======================================")
            print(f"Aussagen zum Entfernen von Relationen (Schritt 4):")
            for task in generatedTasks:
                print(task)
            print(f"=======================================")

        return fdsets

    def hashable_dependencies(self):
        """
        makes the dependencies hashable by converting the sets to frozensets

        Returns:
            list[tuple[frozenset, frozenset]]: The dependencies with frozensets
        """
        return [(frozenset(pre), frozenset(post)) for pre, post in self.dependencies]

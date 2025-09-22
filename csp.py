from typing import Any
from queue import Queue


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        # Initialize queue
        queue = []
        for u, v in self.binary_constraints.keys():
            queue.append((u, v))
            queue.append((v, u))
        # While queue is not empty, do:
        while len(queue) > 0:
        #   (Xi, Xj) <- POP(queue)
            Xi, Xj = queue.pop()
        #   if Revise(csp, Xi, Xj) then
            if self.revise(Xi,Xj):
                if len(self.domains.get(Xi)) == 0:
        #       if size of Di = 0 then return false
                    return False
                else:
        #       for each Xk in Xi.NEIGHBORS - {Xj} do
                    nbrs = self.neighbors(Xi)
                    nbrs.remove(Xj)
                    for Xk in nbrs:
        #           add (Xk, Xi) to queue
                        queue.append((Xk,Xi))
        # return true
        return True
    
    def revise(self, Xi, Xj):
        """
        Revises the domain of Xi to enforce consistency with Xj.

        Removes values from Xi's domain that do not have any compatible value in Xj's domain
        according to the binary constraints.

        Parameters
        ----------
        Xi : str
            The variable whose domain is to be revised.
        Xj : str
            The neighboring variable to check consistency against.

        Returns
        -------
        bool
            True if Xi's domain was revised (values removed), False otherwise.
        """
        # revised <- false
        revised = False
        allowed = self.binary_constraints.get((Xi,Xj)) or self.binary_constraints.get((Xj,Xi))
        if allowed is None:
            return False
        # for each x in Di do
        to_remove = set()
        for x in set(self.domains.get(Xi)):
        # if no value y in Dj allows (x,y) to satisfy the constraint between Xi and Xj, then 
            if not any((x, y) in allowed for y in self.domains.get(Xj)):
                to_remove.add(x)
                    # delete x from Di
        if to_remove:
            self.domains.get(Xi).difference_update(to_remove)
            revised = True
        # return revised
        return revised
    
    def neighbors(self, x: str) -> set[str]:
        """
        Returns the set of neighboring variables for a given variable.

        Parameters
        ----------
        x : str
            The variable whose neighbors are to be found.

        Returns
        -------
        set[str]
            The set of variables that share a binary constraint with x.
        """
        nbrs = set()
        for (a, b) in self.binary_constraints.keys():
            if a == x: nbrs.add(b)
            if b == x: nbrs.add(a)
        return nbrs

    def backtracking_search(self) -> None | dict[str, Any]: 
        """
        Solves the CSP using recursive backtracking search.

        Returns
        -------
        None | dict[str, Any]
            A complete assignment of variables to values if a solution exists,
            otherwise None.
        """
        def _is_complete(assignment: dict[str, Any]) -> bool:
            """
            Checks if the assignment is complete (all variables assigned).

            Parameters
            ----------
            assignment : dict[str, Any]
                Current variable assignments.

            Returns
            -------
            bool
                True if all variables are assigned, False otherwise.
            """
            return all(v in assignment for v in self.variables)

        def _select_unassigned(assignment: dict[str, Any]) -> str:
            """
            Selects an unassigned variable from the CSP.

            Parameters
            ----------
            assignment : dict[str, Any]
                Current variable assignments.

            Returns
            -------
            str
                An unassigned variable.
            """
            for v in self.variables:
                if v not in assignment:
                    return v
            raise RuntimeError("No unassigned variable found")

        def _is_consistent(var: str, val: Any, assignment: dict[str, Any]) -> bool:
            """
            Checks if assigning val to var is consistent with the current assignment.

            Parameters
            ----------
            var : str
                The variable to assign.
            val : Any
                The value to assign.
            assignment : dict[str, Any]
                Current variable assignments.

            Returns
            -------
            bool
                True if the assignment is consistent, False otherwise.
            """
            if val not in self.domains[var]:
                return False
            for n, nval in assignment.items():
                allowed_ab = self.binary_constraints.get((var, n))
                if allowed_ab is not None and (val, nval) not in allowed_ab:
                    return False
                allowed_ba = self.binary_constraints.get((n, var))
                if allowed_ba is not None and (nval, val) not in allowed_ba:
                    return False
            return True

        def backtrack(assignment: dict[str, Any]) -> None | dict[str, Any]:
            """
            Recursive helper for backtracking search.

            Attempts to extend the assignment to a complete solution, backtracking
            when necessary.

            Parameters
            ----------
            assignment : dict[str, Any]
                Current variable assignments.

            Returns
            -------
            None | dict[str, Any]
                A complete assignment if a solution is found, otherwise None.
            """
            if _is_complete(assignment):
                return assignment
            var = _select_unassigned(assignment)
            for val in self.domains[var]:
                if _is_consistent(var, val, assignment):
                    assignment[var] = val
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]
            return None

        return backtrack({})
    
    


def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]

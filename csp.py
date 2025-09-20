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
        # YOUR CODE HERE (and remove the assertion below)
        assert False, "Not implemented"

    def backtracking_search(self) -> None | dict[str, Any]: 
        """Performs backtracking search on the CSP.

        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        def _is_complete(assignment: dict[str, Any]) -> bool:
            return all(v in assignment for v in self.variables)

        def _select_unassigned(assignment: dict[str, Any]) -> str:
            for v in self.variables:
                if v not in assignment:
                    return v
            raise RuntimeError("No unassigned variable found")

        def _is_consistent(var: str, val: Any, assignment: dict[str, Any]) -> bool:
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

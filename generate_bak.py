"""
Version 1.0
- order_domain_values() in use

Version 0.8:
- implement ordered_domain_values()
- repair revise()
- extend monitoring

Version 0.7
Change Log:
- in consistent(): no multiple use of words
"""

import sys

from crossword import *
from random import randint


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()

        # Calls backtrack() on an empty dict
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Create list with words to removed
        candidates = list()

        # Check each word in variable's domain is consistent with unary constraint
        for variable in self.domains:
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    # Add to candidates list
                    candidates.append({variable: word})
        
        # Remove candidates from domains
        for candidate in candidates:
            key = next(iter(candidate))
            value = candidate[key]
            self.domains[key].remove(value)

        # End of function

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        # List with removing candidates
        removing_list = []
        
        # Indices of overlapping
        i_x, i_y = self.crossword.overlaps[x, y]
        
        for word_x in self.domains[x]:

            # Count if condition for arc consistency was met: word_y != word_x
            count = 0

            for word_y in self.domains[y]:
                if word_y[i_y] == word_x[i_x]:
                    count += 1
                    break

            # If condition was not met add word_x to removing list
            if count == 0:
                # creator.domains[x].remove(word_x)
                removing_list.append(word_x)
                revised = True

        # Remove candidated from set domain[x]
        self.domains[x] = self.domains[x] - set(removing_list)

        return revised

        # End of function

    def arcs_initial(self):
        # Empty set for arcs    
        arcs = set()

        # Loop over each variable
        for variable in self.crossword.variables:
            # Loop over each of neighbor of variable
            for neighbor in self.crossword.neighbors(variable):
                arcs.add((variable, neighbor))
        
        return arcs

        # End of function
    
    def ac3(self, arcs=None): # Takes optional argument arcs: list of arcs
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # arc is set of tuples (x, y)
        # list of arcs consists of neighbors of variable 
        # class crossword has function neigbors()

        # Create initial queue with all arcs
        if arcs is None:
            arcs = self.arcs_initial()

        # While set is not empty
        while len(arcs) > 0:
            (X, Y) = arcs.pop()

            if self.revise(X, Y):
                # If empty
                if not self.domains[X]:
                    return False
                else:
                    for Z in (self.crossword.neighbors(X) - {Y}):
                        arcs.add((Z, X))
                        
        return True

        # End of function

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        if len(assignment) == len(self.domains):
            return True
        else:
            return False

        # End of function

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        # Check if word already used
        for value in list(assignment.values()):
            if list(assignment.values()).count(value) > 1:
                print('Not consistent')
                return False

        # take arcs list: tuples in a list
        for (x, y) in self.arcs_initial():

            # Only arcs where both Variables are already assigned
            if x not in assignment or y not in assignment:
                continue

            # Check if length of values match to length variables
            if len(assignment[x]) != x.length or len(assignment[y]) != y.length:
                print('Not consistent')
                return False

            # Check if overlapping strings are same
            # m, n are indices of overlapping letters
            # x, y are neighbor variables from arc
            (m, n) = self.crossword.overlaps[(x, y)]
            if assignment[x][m] != assignment[y][n]:
                print('incorrect overlapping')
                return False

    
        # If nothing inconsistent
        print('consistent')
        return True

        # End of funtion  

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Check for already assigned neighbors
        candidates = set()

        var_neighbors = self.crossword.neighbors(var)

        for neighbor in var_neighbors:

            if neighbor in assignment:

                candidates.add(neighbor)

        # Remove vars that are already in assignment
        var_neighbors -= candidates

        if len(var_neighbors) == 0:
            return self.domains[var]

        else:
            ordered_domain = list()

            # Loop over domain in var
            for word in self.domains[var]:

                # New counter for each word
                n = 0

                for neighbor2 in var_neighbors:

                    # Read overlapping indices
                    (i, j) = self.crossword.overlaps[var, neighbor2]

                    # Loop over words in neighboring variable
                    for word_neighbor in self.domains[neighbor2]:

                        # Of letters do not match, add n + 1
                        if word[i] != word_neighbor[j]:

                            n += 1
                                        
                # Add word to dict with key = n
                ordered_domain.append((word, n))

            # Sort list
            ordered_domain = sorted(ordered_domain, key=lambda value: value[1])

            # Only take values; delete n
            for i in range(len(ordered_domain)):
                ordered_domain[i] = ordered_domain[i][0]

            return ordered_domain
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
    
        # List to store vars not yet in assignment
        remaining_vars = list()

        for var1 in self.domains:
            # var not yet in assignment
            if var1 not in assignment:
                 remaining_vars.append(var1)
        
        if len(remaining_vars) > 0:

            for var2 in remaining_vars:

                    th = float('inf')

                    # If current var has less words, remember var and new count of words
                    if len(self.domains[var2]) < th:
                        th = len(self.domains[var2])
                        var_min = var2
                    
                    # If both variables have same amount of words in domain
                    elif len(self.domains[var2]) == th:

                        # Take new var if higher order
                        if len(self.crossword.neighbors(var2)) > len(self.crossword.neighbors(var_min)):
                            var_min = var2

                        # If tied chose randomly replace with current var
                        elif len(self.crossword.neighbors(var2)) == len(self.crossword.neighbors(var_min)):
                            if (randint(1, 2) & 2) == 0:
                                var_min = var2

            return var_min
        
        return None

        # for variable in self.domains:
        #         if variable not in assignment:
        #             print('Selected unassigned variable: ', variable)
        #             return variable
                
        # return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        """Runs backtracking search to find an assignment."""

        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment
        
        # New variable
        var = self.select_unassigned_variable(assignment)
        # Loop over values from ordered domain list
        for value in self.order_domain_values(var, assignment):
            # print('Testing value: ', value, 'from: ', self.order_domain_values(var, assignment))
            print('Testing value: ', value)
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

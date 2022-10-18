import sys
import copy
import numpy as np
import operator

from crossword import *


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
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #For each variable, check whether the domains match length
        for var in self.domains:

            non_consistent_words = list()

            for word in self.domains[var]:

                if var.length != len(word):
                    non_consistent_words.append(word)
                    
            self.domains[var].difference_update(non_consistent_words)        


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #Overlaps method returns index of overlapping letters in two variables
        overlap = self.crossword.overlaps[x, y]
        modified = False

        #If no overlap clear domain of x
        if overlap == None:
            #nah self.domains[x].clear()
            return False

        non_arc_words = list()
        
        #Compare each word in domain for required overlap to fit constraints
        for word_x in self.domains[x]:

            match = False

            for word_y in self.domains[y]:

                #If correct overlap does not exist, remove from domain x
                if word_x[overlap[0]] == word_y[overlap[1]]:

                    match = True
                    
            if not match:
                non_arc_words.append(word_x)
                modified = True

        self.domains[x].difference_update(non_arc_words)


        #Return true if modified
        if modified:
            return True
        
        else:
            return False


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        #If no argument and arcs = none, then create queue by listing all variable pairs with valid overlap
        if arcs == None:
            
            #Create empty queue list
            queue = list()

            #For each variable, check for overlap with another variable and add this pair as an arc to the queue
            for var_x in self.domains:

                for var_y in self.domains:
                    
                    if var_x == var_y:
                        continue

                    overlap = self.crossword.overlaps[var_x, var_y]

                    if overlap != None:

                        queue.append((var_x, var_y))
                    
        
        #Else take arcs argument as initial queue
        else:

            queue = arcs

        #Apply AC3 algorithm
        while len(queue) != 0:

            var_x, var_y = queue.pop(0)

            #Check if revise modifies the domain of var x
            if self.revise(var_x, var_y):

                #If domain empty, no possible values for variable and cannot be solved
                if self.domains[var_x] == None:

                    return False

                #Identify neighbours of x except y
                #neighbours  = [arc[1] for arc in queue if arc[0] == var_x and arc[1] != var_y]
                neighbours = self.crossword.neighbors(var_x)

                #Add neighbour - x arc to queue for revision later
                for neighbour in neighbours:

                    if neighbour == var_y:
                        continue

                    queue.append((neighbour, var_x))
                
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
            
        #For every variable in crossword, check if assignment dict has value
        for var in self.domains:

            if var not in assignment.keys():
                return False

        #If assigned return true        
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        #For each variable in crossword
        for var in self.domains:

            #Skip if not yet assigned
            if var not in assignment.keys():
                continue
            
            #That assigned values are distinct by comparison to other assigned values
            for var_2 in self.domains:

                if var == var_2 or var_2 not in assignment.keys():
                    continue

                if assignment[var] == assignment[var_2]:
                    return False
                
                #Check no conflict between neighbouring variables
                overlap = self.crossword.overlaps[var, var_2]

                #If no overlap, no possible conflict so continue
                if overlap == None:
                    continue

                if assignment[var][overlap[0]] != assignment[var_2][overlap[1]]:
                    return False

            #Check assigned value fits correct length
            if len(assignment[var]) != var.length:
                return False
                
        return True    



    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        #Create list with empty column for count
        list_domains = [[word, 0] for word in self.domains[var]]

        #Define neighbours for selected variable var
        neighbours = self.crossword.neighbors(var)

        #For each word in domain of selected var
        for item in list_domains:

            count = 0

            #For each neighbour
            for neighbour in neighbours:

                #If that neighbour has already been assigned, then conintue
                if neighbour in assignment.keys():
                    continue

                #If not yet assigned, check if a word in its domain matches the selected word and add count if so to mark constraint
                for word in self.domains[neighbour]:

                    if item[0] == word:

                        count +=1

            item[1] = count

        #Sort list by count
        list_domains = sorted(list_domains, key=lambda x: x[1]) 

        output_list = [item[0] for item in list_domains]

        return output_list




    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        #Create list of unassigned variables with two empty columns for rankings
        list_unassigned = [[None,None,var] for var in self.domains if var not in assignment.keys()]
        for item in list_unassigned:

            item[0] = len(self.domains[item[2]])

            item[1] = len(self.crossword.neighbors(item[2]))
        
        #Sort list by fewest words in domain, then 
        list_unassigned = sorted(list_unassigned, key=lambda x:(x[0], -x[1]))

        return list_unassigned[0][2]        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #If assignment complete, crossword is solved
        if self.assignment_complete(assignment):
            return assignment

        #Select unassigned variable and domain
        var = self.select_unassigned_variable(assignment)
        domain = self.order_domain_values(var, assignment)

        #For each word in domain, check consistency. If consistent assign word to variable and recur to next node
        for word in domain:

            assignment[var] = word

            if self.consistent(assignment):
                
                #Interveave
                arcs = [[neighbour, var] for neighbour in self.crossword.neighbors(var)]
                if self.ac3(arcs):

                    #If inference success, then assign remaining domain to variable
                    for var_x in self.domains:
                        
                        #If not already assigned
                        if var_x not in assignment.keys():
                            
                            #Used to select item from set
                            for e in self.domains[var_x]:
                                
                                assignment[var_x] = e
                                break
                            
                #End
                
                result = self.backtrack(assignment)

                if result != None:

                    return result   

            del assignment[var]

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

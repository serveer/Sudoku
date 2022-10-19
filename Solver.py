############################################################
# CIS 521: Sudoku Homework 
############################################################

student_name = "Jonathan Shaw"

############################################################
# Imports
############################################################


import math
import numpy as np
import copy


############################################################
#Sudoku Solver
############################################################

def sudoku_cells():
    # list of all cells in a Sudoku puzzle as (row, column) pairs
    cells = []
    for r in range(9):
        for c in range(9):
            cells.append((r, c))
    return cells


def sudoku_arcs():
    # list of all arcs between cells in a Sudoku puzzle corresponding to inequality constraints
    arcs = []
    cells = sudoku_cells()
    for cell in cells:
        for compare in cells:
            if compare == cell: #if cell equal compare skip
                continue
            if cell[0] == compare[0] or cell[1] == compare[1]: #if same row or col
                arcs.append((cell, compare))
            elif same_box(cell[0], compare[0]) and same_box(cell[1], compare[1]): # if same block
                if (cell, compare) not in arcs:
                    arcs.append((cell, compare))
    return arcs


def same_box(num1, num2):
    #helper function to determine same block
    fir_3 = [0, 1, 2]
    sec_3 = [3, 4, 5]
    thi_3 = [6, 7, 8]
    if num1 in fir_3 and num2 in fir_3:
        return True
    elif num1 in sec_3 and num2 in sec_3:
        return True
    elif num1 in thi_3 and num2 in thi_3:
        return True
    else:
        return False


def read_board(path):
    # import text file and return as dictionary
    board = {}
    num = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    num = [int(i) for i in num]
    with open(path, 'r') as f:
        for r in range(9):
            row = f.readline()
            for c in range(9):
                if row[c] == '*':
                    board[(r, c)] = set(num)
                else:
                    board[(r, c)] = set([int(row[c])])
        f.close()
    return board


class Sudoku(object):
    #create in-class constants
    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        #print cell possible values
        return self.board[cell]

    def get_board(self):
        # print whole board
        for r in range(9):
            row = []
            for c in range(9):
                # if len(self.board[r,c])==1:
                row.append(self.board[r, c])
            print(row)

    def remove_inconsistent_values(self, cell1, cell2):
        #reduce possible values in each cell if we have a determined inconsistent cell
        if len(self.board[cell2]) == 1:
            num = list(self.board[cell2])[0] # get determined number
            if num in self.board[cell1]: # if num is in cell1
                self.board[cell1].remove(num) # removed number as possibility of cell1 and return True
                return True
        return False

    def find_neigh(self, Xi, Xj):
        #helper function for AC3, find neighbors of Xi, which has appended value
        neighbors = []
        for cell1, cell2 in self.ARCS:
            if cell2 == Xi and cell1 != Xj:
                neighbors.append(cell1)
        return neighbors

    def infer_ac3(self):
        # ac3 solver function
        queue = sudoku_arcs()
        while len(queue) != 0: #end when queue empty
            cell_i, cell_j = queue.pop(0) #pop cell that needs to be looked at
            if self.remove_inconsistent_values(cell_i, cell_j): # Only proceed if value is removed
                if len(self.board[cell_i]) == 0: #return False if no possible value in a cell
                    return False
                elif len(self.board[cell_i]) == 1:
                    for nei in self.find_neigh(cell_i, cell_j):
                        queue.append((nei, cell_i)) #append neighbor pairs if value changes
        return True

    def check_exist(self,num,cell,direction):
        #helper value for ac3 improved, check if value exist within same direction(block,row or col)
        for cell_i in self.CELLS:
            if cell_i==cell: #skip if same
                continue
            if direction=='row':
                if cell[0]==cell_i[0]:
                    if num in self.board[cell_i]:
                        return False
            elif direction=='col':
                if cell[1]==cell_i[1]:
                    if num in self.board[cell_i]:
                        return False
            elif direction=='block':
                if same_box(cell[0], cell_i[0]) and same_box(cell[1], cell_i[1]):
                    if num in self.board[cell_i]:
                        return False
        return True

    def eliminate(self,cell):
        # if certain cell contains a value that is not a possibility for its row/block/col, set cell to value
        directions=['row','col','block']
        if len(self.board[cell])==1: # skip cell with fixed value
            return False
        for num in self.board[cell]:
            for d in directions: # iterate through all directions
                if self.check_exist(num,cell,d):
                    self.board[cell]=set([num])
                    return True
        return False

    def infer_improved(self):
        #improved version of ac3, same logic
        self.infer_ac3()
        queue = sudoku_cells()
        while len(queue) != 0:
            cell = queue.pop(0)
            if self.eliminate(cell):
                self.infer_ac3()
                if len(self.board[cell]) == 0:
                    return False
                elif len(self.board[cell]) == 1:
                    for nei in self.find_neigh(cell, cell):
                        queue.append(nei)
        return True

    def is_complete(self):
        # check if sudoku is complete
        for c in self.CELLS:
            if len(self.board[c])!=1:
                return False
        return True

    def select_cell(self):
        # select a cell to guess based on cell with least possibility, could narrow down further with constraints
        unassigned_cells={}
        for c in self.CELLS:
            if len(self.board[c]) != 1:
                unassigned_cells[c]=self.board[c]
        unassigned_cells={k: v for k, v in sorted(unassigned_cells.items(), key=lambda item: len(item[1]))}
        return list(unassigned_cells.keys())[0]

    def is_consistent(self):
        #check if the current assignment is consistent
        for cell in self.CELLS:
            if len(self.board[cell]) == 0:
                return False
        return True

    def infer_with_guessing(self):
        # main infer method
        self.infer_improved()
        self.board=self.infer_helper()

    def infer_helper(self):
        # uses backtracking to solve puzzle, return solved dict
        if self.is_complete():
            return self.board # return dict if complete
        cell=self.select_cell()
        for value in self.board[cell]: # guess each value to see if possible
            sudoku_ex = copy.deepcopy(self)
            sudoku_ex.board[cell] = set([value]) # guess on copy
            sudoku_ex.infer_improved()
            if sudoku_ex.is_consistent(): # if still consistent continue to guess next
                solution = sudoku_ex.infer_helper()
                if solution is not None:
                    return solution


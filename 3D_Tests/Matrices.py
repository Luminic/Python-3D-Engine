import numpy
import math
import time

"""
Matricies will be in this format
[[a1,a2,a3]
 [b1,b2,b3]
 [c1,c2,c3]]

The Right Handed System is Used

"""


def mat_dot_product(mat1, mat2):
    """
    Multiplies two matrices
    """
    # Makes sure the matricies can be multiplied
    assert len(mat1[0]) == len(mat2), str(len(mat1))+"x"+str(len(mat1[0]))+" and "+str(len(mat2))+"x"+str(len(mat2[0]))+" matrices cannot be multiplied"

    # I avoided nested list comp. because imo its ugly
    result = []
    for row1 in mat1: # For every row in mat1
        result.append([])
        for col2 in zip(*mat2): # For every column in mat2 (works because *zip transposes mat2)
            # Multiplies each element from row1 with the matching element from col2
            # Sums all the products and appends the number to the last (most recently created) row in the matrix
            result[-1].append(sum(row1[i]*col2[i] for i in range(len(row1))))

    return result

def vec_dot_product(vec1, vec2):
    """
    Input:  2 n-dimensional vectors
    """
    return sum([vec1[i]*vec2[i] for i in range(len(vec1))])

def vec_cross_product(vec1, vec2):
    """
    Input:  2 vectors in the form [a, b, c]
    Output: The cross product of those vectors
    """
    return [vec1[1]*vec2[2] - vec1[2]*vec2[1],\
            vec1[2]*vec2[0] - vec1[0]*vec2[2],\
            vec1[0]*vec2[1] - vec1[1]*vec2[0]]

def mat_add(*mats):
    """
    Input:  n matricies of the same size
            -if there is a matrix inputed bigger than the first matrix inputed, nothing will happen (the larger matrix will only get a part of it used)
            -if there is a matrix inputed smaller than the first matrix inputed, an IndexError will be raised
    Output: a matrix of the same size that sums all the matrices
    """
    # Creates the result matrix the same size as the first matrix in mats
    result = [[0]*len(mats[0][0]) for _ in range(len(mats[0]))]
    for i in range(len(mats)):
        for r in range(len(mats[0])):
            for c in range(len(mats[0][0])):
                result[r][c] += mats[i][r][c]

    return result

def mat_scalar_mult(mat, scalar):
    """
    Modifies the inputed matrix *and* returns the result
    """
    t = time.time()
    for i in range(len(mat)):
        mat[i] = [val*scalar for val in mat[i]]
    return mat

def mat_transpose(mat,convert=True):
    # Kind of useless bc zip exists
    if convert: return [list(row) for row in zip(*mat)]
    return zip(*mat)

def identity_mat(size):
    """
    Input:  size is an int that determines the size of the matrix (identity matrices are always square)

    Output: a size x size identity matrix
    """
    result = []
    for i in range(size):
        row = [0]*size
        row[i] = 1
        result.append(row)

    return result

def rot_mat(ang, axis, r=6):
    """
    Input:  ang is in radians
            axis is a single character string with 'x', 'y', or 'z'
            r specifies how many decimal points the resulting matrix should be rounded to

    Output: a rotation matrix
            matrix is rounded to 9 decimal places by default
    """
    if axis == 'x':
        return [[ 1,                      0,                       0                      ],\
                [ 0,                      round( math.cos(ang),r), round(-math.sin(ang),r)],\
                [ 0,                      round( math.sin(ang),r), round( math.cos(ang),r)]]
    elif axis == 'y':
        return [[round( math.cos(ang),r), 0,                       round( math.sin(ang),r)],\
                [0,                       1,                       0                      ],\
                [round(-math.sin(ang),r), 0,                       round (math.cos(ang),r)]]
    elif axis == 'z':
        return [[ round(math.cos(ang),r), round(-math.sin(ang),r), 0                      ],\
                [ round(math.sin(ang),r), round( math.cos(ang),r), 0                      ],\
                [ 0,                   0,                          1                      ]]
    else: raise ValueError("Axis must be a single character string containing either 'x', 'y', or 'z'")

def mat_rot(mat, ang, axis, r=6):
    """
    Input:  mat must be a 1x3 matrix
            ang is in radians
            axis is a single character string with 'x', 'y', or 'z'

    Output: a rotated matrix
    """
    return mat_dot_product(mat, rot_mat(ang, axis, r))

def mat_print(mat):
    """
    Displays matricies nicely
    """
    # NOT MADE TO BE EFFICIENT
    print("matrix", str(len(mat))+"x"+str(len(mat[0])))
    maxlen = 0
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            mat[i][j] = str(mat[i][j])
            l = len(mat[i][j])
            if mat[i][j][0] == '-': l-=1
            if l > maxlen: maxlen = l

    for i in range(len(mat)):
        for j in range(len(mat[i])):
            if mat[i][j][0] != '-': mat[i][j] = " "+mat[i][j]
            mat[i][j] = mat[i][j]+(maxlen-len(mat[i][j])+2)*" "
        print("|"+"|".join(mat[i])+"|")
    print()

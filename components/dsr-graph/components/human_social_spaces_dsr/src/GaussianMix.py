# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# def isEdge(z, x, y, h):
#     if z[y, x] >= h:
#         len_x = z.shape[1] - 1
#         len_y = z.shape[0] - 1
#         if x > 0:
#             if z[y, x - 1] < h:
#                 return True
#             if y > 0 and z[y - 1, x - 1] < h:
#                 return True
#             if y < len_y and z[y + 1, x - 1] < h:
#                 return True
#         if x < len_x:
#             if z[y, x + 1] < h:
#                 return True
#             if y > 0 and z[y - 1, x + 1] < h:
#                 return True
#             if y < len_y and z[y + 1, x + 1] < h:
#                 return True
#         if y > 0 and z[y - 1, x] < h:
#             return True
#         if y < len_y and z[y + 1, x] < h:
#             return True
#     return False


# def filterEdges(z, h):
#     result = np.zeros(z.shape, dtype=np.uint8)
#     for y in range(z.shape[0]):
#         for x in range(z.shape[1]):
#             if isEdge(z, x, y, h):
#                 result[y, x] = 1
#             # print("result:")
#             # print(result, y, x)

#     return result

def isEdge(z, h):
    """
    1) rolls the input signal 'z' by one pixel in all directions, 2) compares each
    resulting value to its neighbor, and 3) returns a boolean array indicating
    which pixels are within a certain distance 'h' of their neighbors.

    Args:
        z (2D array.): 2D array to be analyzed and processed for containing a
            specified minimum value in each of its non-zero elements.
            
            	1/ `z.shape[1]`: The number of rows in the input array is denoted by
            `z.shape[1]`.
            	2/ `z.shape[0]`: The number of columns in the input array is denoted
            by `z.shape[0]`.
            	3/ `<h>`: A scalar value that represents the minimum difference between
            neighboring values to be considered an edge.
            	4/ `np.roll(z, shift=(0, -1), axis=(0, 1))`: Rolls the input array
            `z` by one position in the x-direction and subtracts it from itself.
            This operation is repeated for each element in the array, shifting it
            to the left by one position.
            	5/ `np.roll(z, shift=(-1, 0), axis=(0, 1))`: Rolls the input array
            `z` by one position in the x-direction and subtracts it from itself.
            This operation is repeated for each element in the array, shifting it
            to the left by one position.
            	6/ `np.roll(z, shift=(1, 0), axis=(0, 1))`: Rolls the input array `z`
            by one position in the x-direction and subtracts it from itself. This
            operation is repeated for each element in the array, shifting it to
            the right by one position.
            	7/ `<h>`: The minimum difference between neighboring values to be
            considered an edge is used again.
            
            	Based on these properties and operations, the function returns `True`
            if any of the neighbors of each element in the input array are within
            the specified distance threshold, otherwise it returns `False`.
        h (float): 2D grid of a specific size that is used as a threshold for
            comparison with the current grid to determine if a neighboring cell
            satisfies a given condition.

    Returns:
        int: a boolean array indicating whether each element of the input vector
        `z` is within a given distance `h` from its neighbors.

    """
    len_x, len_y = z.shape[1] - 1, z.shape[0] - 1
    
    # Calcula las diferencias con los vecinos en cada dirección
    left = np.roll(z, shift=(0, -1), axis=(0, 1)) < h
    right = np.roll(z, shift=(0, 1), axis=(0, 1)) < h
    up = np.roll(z, shift=(-1, 0), axis=(0, 1)) < h
    down = np.roll(z, shift=(1, 0), axis=(0, 1)) < h
    
    # Verifica si algún vecino cumple con la condición
    return (z >= h) & (left | right | up | down)

def filterEdges(z, h):
    edge_mask = isEdge(z, h).astype(np.uint8)
    return edge_mask

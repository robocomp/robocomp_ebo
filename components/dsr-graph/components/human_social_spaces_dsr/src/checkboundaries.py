import numpy as np


def checkboundaries(grid, i, j, total_points):
    """
    1/ Generates high-quality documentation for code given.
        2/ Iterates through all points and checks if they have neighbors that
    belong to different clusters, marking them as such.
        3/ If a point has neighbors in multiple lists, merges the lists and removes
    one of them since they belong to the same cluster.

    Args:
        grid (int): 2D grid of points that are used to determine the neighbors of
            a given point.
        i (float): 2D position of the point being analyzed in the grid.
        j (int): 2D coordinate of the point to check for proximity with its neighbors.
        total_points (list): 2D points dataset that the function operates on,
            providing a reference to the points array for the Neighbors and Clusters
            analysis.

    Returns:
        tuple: a boolean value (`same_cluster`) and an integer index (`index`)
        indicating whether a point belongs to two distinct clusters or not.

    """
    index = 0
    same_cluster = False
    neighbors = []

    ##### EN EL ENTORNO TENGO EN CUENTA LOS PIXELES QUE RODEAN AL PUNTO Y ADEMAS LOS QUE RODEAN A ESTOS #####
    #### SINO DA PROBLEMAS PORQUE LOS CONSIDERA DE CLUSTERS DIFERENTES####

    for indicey in range(-2, 3):
        for indicex in range(-2, 3):
            neighbors.append([i + indicex, j + indicey])

    for a in total_points:
        for b in a:
            if (b in neighbors) and (same_cluster is False):
                # print ("b esta en el neighbors")
                same_cluster = True
                index = total_points.index(a)

            if (b in neighbors) and (same_cluster is True):
                aux = total_points.index(a)
                if aux != index:
                    #   print("El neighbors coincide en dos listas")
                    total_points[index].extend(total_points[aux])
                    total_points.pop(aux)
                    break

    ### SI UN PUNTO TIENE ENTORNOS QUE PERTENECEN A DOS LISTAS
    ### CONCATENAMOS LAS DOS LISTAS Y ELIMINAMOS UNA DE ELLAS PORQUE PERTENECEN AL MISMO CLUSTER

    return same_cluster, index

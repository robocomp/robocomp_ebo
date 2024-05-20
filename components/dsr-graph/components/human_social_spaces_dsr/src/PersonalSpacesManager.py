from math import *

import matplotlib.pyplot as plt

plt.plasma()
import numpy as np
import GaussianMix as GM
import checkboundaries as ck
from normal import Normal
from scipy.spatial import ConvexHull
from rich.console import Console
from math import *

console = Console(highlight=False)
from mpl_toolkits.mplot3d import Axes3D

plt.figure()
import time

# plt.ion()


class Person:
    def __init__(self, x=0, y=0, th=0):
        """
        Sets instance variables `x`, `y`, and `th` to values calculated from input
        arguments, and initializes a private variable `_radius`.

        Args:
            x (`Double`.): original value of the variable `x`, which is then divided
                by 1000 to produce the updated value for the object's field `self.x`.
                
                		- `self.x`: The value of `x` is assigned a fractional value by
                dividing it by 1000.
                		- `self.y`: The value of `y` is similarly assigned a fractional
                value by dividing it by 1000.
                		- `self.th`: The value of `th` is unaltered and remains as the
                original value provided in the input.
                		- `_radius`: The value of `_radius` is assigned the value 0.30,
                which is the default value for this attribute.
            y (float): 3D point's y-coordinate, which is used to compute and set
                the point's 3D position.
            th (`double`.): 2D size of the circle, specifically its height, in pixels.
                
                		- `_radius`: This property is set to 0.30 and represents the
                radius of the elliptical shape.

        """
        self.x = x / 1000
        self.y = y / 1000
        self.th = th
        self._radius = 0.30

    def draw(self, sigma_h, sigma_r, sigma_s, rot, draw_personal_space=False):
        # define grid.
        """
        Creates a meshgrid of coordinates, calculates personal space values at
        those points, and then plots the personal space as a surface using Matplotlib.

        Args:
            sigma_h (real number/quantity.): 3D standard deviation of the personal
                space height.
                
                		- `sigma_h`: This is an instance of the class `RandomVariable`,
                representing a Gaussian distribution with unknown mean and variance.
                		- `sigma_r`: The variance of the Gaussian distribution in the
                radial direction.
                		- `sigma_s`: The variance of the Gaussian distribution in the
                tangential direction.
                		- `rot`: The rotation angle of the personal space coordinate
                system relative to the world coordinate system.
                
                	Note that `sigma_h` may have other properties or attributes, such
                as its probability density function or cumulative distribution
                function, depending on its specific implementation and usage.
            sigma_r (float): 3D standard deviation of the personal space's shape,
                which is used to modify the size and shape of the personal space
                when it is visualized using the `plt.contour()` and `plt.gca().add_patch()`
                functions in the code.
            sigma_s (float): 3D standard deviation of the space around the personal
                space, which determines the density and resolution of the personal
                space mesh visualized on the plot.
            rot (float): 3D rotation of the personal space grid relative to the
                body's orientation, which is used to calculate the position of the
                personal space grid in the 3D space.
            draw_personal_space (bool): 3D surface of the personal space of the
                agent, which is plotted using Matplotlib's `plot_surface()` function
                when set to `True`.

        Returns:
            float: a 3D plot of personal space, including a circle representing
            the user's body and an orientation line indicating their heading.

        """
        npts = 50
        x = np.linspace(self.x - 4, self.x + 4, npts)
        y = np.linspace(self.y - 4, self.y + 4, npts)

        X, Y = np.meshgrid(x, y)
        Z = self._calculate_personal_space(X, Y, sigma_h, sigma_r, sigma_s, rot)

        if draw_personal_space:
            plt.clf()
            plt.contour(X, Y, Z, 10)
            plt.axis('equal')
            # Body
            body = plt.Circle((self.x, self.y), radius=self._radius, fill=False)
            plt.gca().add_patch(body)

            # Orientation
            x_aux = self.x + self._radius * cos(pi / 2 - self.th)
            y_aux = self.y + self._radius * sin(pi / 2 - self.th)

            # print(y_aux)
            heading = plt.Line2D((self.x, x_aux), (self.y, y_aux), lw=1, color='k')
            plt.gca().add_line(heading)

            fig = plt.figure()

            ax = fig.add_subplot(111, projection='3d')
            # ax = fig.gca(projection='3d')
            ax.plot_surface(X, Y, Z, cmap='plasma')
            plt.pause(0.00001)

            # plt.axis('equal')

        return Z

    def _calculate_personal_space(self, x, y, sigma_h, sigma_r, sigma_s, rot):
        """
        Takes a rotated, normalized vector and returns a masked version based on
        its signed angle with respect to an arbitrary reference vector.

        Args:
            x (float): 2D coordinates of the pixel being transformed.
            y (ndarray.): 2D point that, when combined with the `x` input parameter
                and other values within the function, determines the output value
                of the function.
                
                		- `y`: The personal space matrix, which is a numpy array of shape
                `(nalpha, nx, ny)` where `nalpha` and `nx` represent the number
                of angles and x-coordinates in the grid, respectively, and `ny`
                represents the number of y-coordinates in the grid.
                		- `self.y`: A reference to the personal space matrix.
                		- `rot`: The rotation angle between the personal space coordinate
                system and the standard base coordinate system.
                		- `pi / 2`: The half of a full circle, used as a mathematical constant.
            sigma_h (float): 90-degree gradient of the sigma function in the Horner
                scheme.
            sigma_r (ndarray (a multi-dimensional array object).): 90-degree
                rotation component of the sigma mask.
                
                		- `np.copy(nalpha)` creates a shallow copy of the `nalpha` array.
                		- `for i in range(nalpha.shape[0]): for j in range(nalpha.shape[1])`:
                This loop iterates over each element of the `nalpha` array, and
                performs computations on the corresponding elements of the `sigma`
                array.
                		- `sigma_r if nalpha[i, j] <= 0 else sigma_h`: The value of
                `sigma_r` is assigned to the `sigma` array at each iteration,
                unless `nalpha[i, j]` is greater than or equal to 0, in which case
                the value of `sigma_h` is assigned instead.
                		- `sin(2 * rot) / 4`: This line computes the sine of twice the
                value of `rot`, divided by 4.
                		- `sin(rot) ** 2 / 2`: This line computes the square of the sine
                function of `rot`, divided by 2.
                		- `cos(rot) ** 2 / 2`: This line computes the square of the
                cosine function of `rot`, divided by 2.
                
                	Therefore, `sigma` is a 2D array containing values representing
                the personal space of each point in the input image, with values
                assigned based on the orientation of the point's coordinate system
                relative to a reference frame defined by the parameters `self.x`,
                `self.y`, and `rot`.
            sigma_s (ndarray with shape (nalpha.shape[0], nalpha.shape[1]).):
                90-degree rotated standard deviation of the output distribution,
                which is used in calculating the final output value of the function.
                
                		- `sigma_s` is a square matrix with shape `(nalpha.shape[0], nalpha.shape[1])`.
                		- It represents the spatial variation of the personal space in
                the two dimensions parallel to the rotation axis.
                		- The elements of `sigma_s` are computed as `sin(2 * rot) / 4`
                times the square of the sine or cosine of the angle of rotation,
                depending on whether the element is in the positive or negative
                quadrant of the axis.
                		- The resulting matrix has non-negative elements, with a maximum
                value of `1`.
                
                	The explanation does not include a summary, as per your requirement.
            rot (float): 90-degree rotation angle around the x-axis, which is
                applied to the signal before computing the autocorrelation.

        Returns:
            np.array: a 2D array representing the personal space of an individual
            based on their body orientation and the location of a target object.
            
            		- `z`: The personal space of the agent, represented as a numpy array
            with shape (nalpha.shape[0], nalpha.shape[1]). It contains values
            between 0 and 1 that represent the likelihood of being in a particular
            location.
            		- `a`, `b`, and `c`: These are constants that are computed during
            the execution of the function, based on the value of `rot`. They are
            used to calculate the personal space of the agent.
            		- `sigma_r`, `sigma_s`, and `sigma`: These are arrays of shape
            (nalpha.shape[0], nalpha.shape[1]) that represent the likelihood of
            being in a particular location and the associated variance. They are
            computed using the values of `nalpha`.
            		- `x` and `y`: The coordinates of the agent, used to compute the
            personal space.

        """
        alpha = np.arctan2(y - self.y, x - self.x) - rot - pi / 2
        nalpha = np.arctan2(np.sin(alpha), np.cos(alpha))

        sigma = np.copy(nalpha)
        for i in range(nalpha.shape[0]):
            for j in range(nalpha.shape[1]):
                sigma[i, j] = sigma_r if nalpha[i, j] <= 0 else sigma_h

        a = cos(rot) ** 2 / 2 * sigma ** 2 + sin(rot) ** 2 / 2 * sigma_s ** 2
        b = sin(2 * rot) / 4 * sigma ** 2 - sin(2 * rot) / 4 * sigma_s ** 2
        c = sin(rot) ** 2 / 2 * sigma ** 2 + cos(rot) ** 2 / 2 * sigma_s ** 2

        z = np.exp(-(a * (x - self.x) ** 2 + 2 * b * (x - self.x) * (y - self.y) + c * (y - self.y) ** 2))

        return z


class PersonalSpacesManager:
    def __init__(self):
        """
        Sets attributes and values for `personal_spaces`, `dict_space_param`,
        `lx_inf`, `lx_sup`, `ly_inf`, and `ly_sup`. It also defines limits of representation.

        """
        self.__personal_spaces = ["intimate", "personal", "social"]
        # sigma_h, sigma_r, sigma_s,  h
        self.__dict_space_param = {"intimate": [2, 1., 1.3, 0.9],
                                   "personal": [2, 1., 1.3, 0.6],  # 0.5
                                   # "social": [3., 1., 1.3, 0.3],  # 0.2
                                   "social": [2, 1., 1.3, 0.3],  # 0.2
                                   }
        ##Limites de la representacion
        self.lx_inf = -50
        self.lx_sup = 50
        self.ly_inf = -50
        self.ly_sup = 50

    def _get_polyline(self, grid, resolution, lx_inf, ly_inf):
        # Encuentra los índices donde grid es mayor que 0
        """
        Takes in a grid and an index as inputs, then recursively calls itself for
        each point that satisfies a condition. It then returns the polyline formed
        by those points.

        Args:
            grid (2D array/matrix, as stated by the code context and comments.):
                2D grid of pixels, and its value is used to determine which pixels
                are above a certain threshold (represented by non-zero values) for
                the purpose of identifying clusters of pixels that are close to
                each other.
                
                	1/ `grid`: A 2D array with shape `(Nx, Ny)` where each element
                `grid[i, j]` represents a pixel on the grid with integer coordinates
                `(i, j)`. The grid may have any value between 0 and 1.
            resolution (int): 2D grid spacing in the transformation process, used
                to convert point lists into a single 2D array for efficient manipulation.
            lx_inf (ndarray or numpy array.): 2D coordinates of the leftmost edge
                of the output convex hull, which is calculated by shifting the
                input points horizontally by a large distance to the left before
                applying the convex hull algorithm.
                
                		- `lx_inf`: This is a list of coordinates representing the infill
                points of a polygon in 2D space. The length of the list should be
                equal to the number of points in the polygon. Each coordinate in
                the list is represented as a 2-element list, where the first element
                represents the x-coordinate and the second element represents the
                y-coordinate.
                		- `resolution`: This is an integer value representing the
                resolution at which the input data is provided. It determines the
                spacing between consecutive points in the `lx_inf` list.
            ly_inf (ndarray.): 3D coordinate of the infinite horizon in the
                translation process.
                
                	1/ `ly_inf`: This is an inflection point in the grid data. It is
                a 2D coordinate representing a point on the boundary of the polygon.
                The value of `ly_inf` is used to determine whether the point lies
                inside or outside the polygon.
                	2/ `resolution`: This is a parameter used to convert the grid
                data into a set of vertices that define a polyline. The resolution
                determines the size of the vertices and can affect the accuracy
                of the polyline representation.
                	3/ `point_list`: This is a list of lists representing the points
                in the polyline. Each sub-list contains two elements, representing
                the x and y coordinates of each point.
                	4/ `hull`: This is a convex hull object that represents the set
                of vertices of the polyline. The hull is computed using the
                `ConvexHull` function from the NumPy library.

        Returns:
            ndarray` (a multi-dimensional NumPy array: a list of points representing
            the convex hull of the grid pixels above a threshold.
            
            	1/ `ret`: A list of 2D points, where each point represents a vertex
            of the polygonal line. The points are in counterclockwise order around
            the boundary of the polygon.
            	2/ Each element in the list is a numpy array containing the coordinates
            of a vertex of the polygon.
            	3/ The arrays are in the correct position and orientation to form a
            closed, non-self-intersecting polygonal line.
            	4/ The resolution parameter used to transform the point coordinates
            is stored in the `resolution` attribute of each vertex.
            	5/ The origin of the coordinate system is at the point `[lx_inf, ly_inf]`.

        """
        j_indices, i_indices = np.nonzero(grid > 0)
        
        total_points = []
        for i, j in zip(i_indices, j_indices):
            same_cluster, pos = ck.checkboundaries(grid, i, j, total_points)
            if same_cluster:
                total_points[pos].append([i, j])
            else:
                points = [[i, j]]
                total_points.append(points)
        
        ret = []
        for point_list in total_points:
            # Realiza la traslación en un solo paso usando NumPy
            point_array = np.array(point_list) * resolution + np.array([lx_inf, ly_inf])
            
            # Calcula el casco convexo
            hull = ConvexHull(point_array)
            ret.append(point_array[hull.vertices])
        
        return ret


    # def _get_polyline(self, grid, resolution, lx_inf, ly_inf):
    #     total_points = []
    #     for j in range(grid.shape[1]):
    #         for i in range(grid.shape[0]):
    #             if grid[j, i] > 0:
    #                 same_cluster, pos = ck.checkboundaries(grid, i, j, total_points)
    #                 if same_cluster is True:
    #                     total_points[pos].append([i, j])
    #                 else:
    #                     points = [[i, j]]
    #                     total_points.append(points)

    #     ret = []
    #     for list in total_points:
    #         # los points en el grid sufren una traslacion, con esto los devolvemos a su posicion original
    #         for points in list:
    #             points[0] = points[0] * resolution + lx_inf
    #             points[1] = points[1] * resolution + ly_inf

    #         points = np.asarray(list)
    #         hull = ConvexHull(points)
    #         ret.append(points[hull.vertices])

    #     return ret

    def get_personal_spaces(self, people_list, represent=False):
        #console.print(' ----- get_personal_spaces -----', style='blue')
        """
        Takes a list of personal spaces, a set of people, and a resolution as
        input, and generates a mesh of the personal spaces using Normal distribution,
        then plots it using matplotlib.

        Args:
            people_list (list): 2D positions of individuals in a personal space,
                which are used to draw and calculate the normal vectors of the
                personal space.
            represent (bool): 3D space of each personal or intimate zone using
                matplotlib to visualize the areas, rather than just returning the
                grid data as before.

        Returns:
            dict: a list of polylines representing personal spaces for each person
            in a list of people.

        """
        plt.clf()
        dict_spaces = dict(intimate=[], personal=[], social=[])
        dict_spaces_mm = dict(intimate=[], personal=[], social=[])
        dict_res = {"intimate" : 0.2, "personal" : 0.3, "social" : 0.3}
        for space in self.__personal_spaces:
            normals = []
            for p in people_list:
                person = Person(p.tx, p.ty, p.ry)
                # person.draw(2,1, 4./3.,pi/2 - person.th, drawPersonalSpace=dibujar) #Valores originales
                person.draw(self.__dict_space_param[space][0], self.__dict_space_param[space][1],
                            self.__dict_space_param[space][2], pi / 2 - person.th, draw_personal_space=represent)
                normals.append(Normal(mu=[[person.x], [person.y]],
                                      sigma=[-person.th - pi / 2.,
                                             self.__dict_space_param[space][0],
                                             self.__dict_space_param[space][1],
                                             self.__dict_space_param[space][2]], elliptical=True))

            #print("Number of gaussians ", len(normals))

            # resolution = 0.22
            resolution = dict_res[space]
            limits = [[self.lx_inf, self.lx_sup], [self.ly_inf, self.ly_sup]]
            _, z = Normal.makeGrid(normals, self.__dict_space_param[space][3], 2, limits=limits, resolution=resolution)

            # _, z = Normal.makeGrid(normals, self.__dict_space_param[space][3], 2, limits=limits, resolution=resolution)
            grid = GM.filterEdges(z, self.__dict_space_param[space][3])
            ordered_points = self._get_polyline(grid, resolution, self.lx_inf, self.ly_inf)
            for pol in ordered_points:
                polyline = []
                polyline_mm = []
                for pnt in pol:
                    polyline.append([pnt[0], pnt[1]])
                    # polyline_mm.append([round(pnt[0] * 1000), round(pnt[1] * 1000)])
                    polyline_mm.append([round(pnt[0] * 1000), round(pnt[1] * 1000)])
                if len(polyline) != 0:
                    dict_spaces[space].append(polyline)
                    dict_spaces_mm[space].append(polyline_mm)

        if represent:
            for soc in dict_spaces["social"]:
                x, y = zip(*soc)
                plt.plot(x, y, color='c', linestyle='None', marker='.')
                plt.pause(0.00001)
            for per in dict_spaces["personal"]:
                x, y = zip(*per)
                plt.plot(x, y, color='m', linestyle='None', marker='.')
                plt.pause(0.00001)

            for inti in dict_spaces["intimate"]:
                x, y = zip(*inti)
                plt.plot(x, y, color='r', linestyle='None', marker='.')
                plt.pause(0.00001)

            plt.axis('equal')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.show()

        return dict_spaces_mm['intimate'], dict_spaces_mm['personal'], dict_spaces_mm['social']

    ##objects
    def calculate_affordance(self, object):
        """
        Takes an object and its shape as input, then returns the appropriate
        affordance value based on the shape of the object.

        Args:
            object (object.): 3D shape of an object that the function is calculating
                the affordance for.
                
                		- `shape`: This attribute provides the shape of the object, which
                can be either `'trapezoid'`, `'circle'`, or `'rectangle'` based
                on the input value.
                		- `calculate_affordance_trapezoidal()`: This function is called
                when `shape` is equal to `'trapezoid'`. It performs a specific
                calculation related to trapezoids and returns the affordance value.
                		- `calculate_affordance_circular()`: This function is called
                when `shape` is equal to `'circle'`. It performs a specific
                calculation related to circles and returns the affordance value.
                		- `calculate_affordance_rectangular()`: This function is called
                when `shape` is equal to `'rectangle'`. It performs a specific
                calculation related to rectangles and returns the affordance value.

        Returns:
            Affordance` object: an object containing the affordances of an object
            based on its shape.
            
            		- If `shape` is `'trapezoidal'`, then the returned affordance is an
            object containing attributes such as `center`, `size`, and `orientation`,
            which represent the position, size, and orientation of the affordance
            in relation to the object.
            		- If `shape` is `'circle'`, then the returned affordance is an object
            containing attributes such as `center`, `radius`, and `angle`, which
            represent the position, radius, and angle of the affordance in relation
            to the object.
            		- If `shape` is `'rectangular'`, then the returned affordance is an
            object containing attributes such as `bounds`, `size`, and `angle`,
            which represent the bounds, size, and angle of the affordance in
            relation to the object.

        """
        shape = object.shape
        if shape == 'trapezoid':
            affordance = self.calculate_affordance_trapezoidal(object)
        elif shape == 'circle':
            affordance = self.calculate_affordance_circular(object)
        elif shape == 'rectangle':
            affordance = self.calculate_affordance_rectangular(object)

        return affordance

    def calculate_affordance_trapezoidal(self, obj):
        """
        Computes an Affine transformation that rotates an object by given angle
        around its center, then translates it along a given vector, to produce a
        new polygon representation of the affordance of the object.

        Args:
            obj (`object`.): 2D object being extruded, providing its coordinates
                and other relevant properties to generate the polygonal representation
                of the object.
                
                		- `ry`: The radius of the circle or arc that defines the affordance.
                		- `inter_angle`: The angle between the center of the circle or
                arc and the reference point for calculating the trapezoidal segments.
                		- `tx`: The x-coordinate of the reference point for calculating
                the trapezoidal segments.
                		- `ty`: The y-coordinate of the reference point for calculating
                the trapezoidal segments.
                		- `inter_space`: The distance between the center of the circle
                or arc and the reference point for calculating the trapezoidal segments.
                		- `width`: The width of the object or shape.
                
                	The function returns an array of polyline objects, which represent
                the segments of the affordance formed by connecting the points
                determined by `ry`, `inter_angle`, `tx`, and `ty`.

        Returns:
            array` of `coordinates` (i.e., `[x, y]` values: a list of four points
            that define a polyline representing the affordance of an object.
            
            	1/ `polyline`: A list of 4 points that define the polyline representing
            the trapezoidal shape. Each point is a tuple consisting of `tx` and
            `ty`, which are the coordinates of the point in the grid coordinate system.
            	2/ The first two points in the list (`[(obj.tx + obj.width / 2),
            obj.ty]` and `[(obj.tx - obj.width / 2), obj.ty)` represent the two
            corners of the trapezoid.
            	3/ The remaining two points in the list (`[...], [(obj.tx + obj.inter_space
            * (cos(pi/2 - right_angle))), (obj.ty + obj.inter_space * (sin(pi/2 -
            right_angle)))]` and `[...], [(obj.tx + obj.inter_space * (cos(pi/2 -
            left_angle))), (obj.ty + obj.inter_space * (sin(pi/2 - left_angle)))]"])`
            represent the two sides of the trapezoid, which are created by drawing
            a line connecting the two corners through the center of the object.
            	4/ `polyline` has a list of 4 points representing the polyline.
            	5/ The coordinates of each point in the `polyline` list are in the
            grid coordinate system, with the `tx` and `ty` values representing the
            x and y coordinates of the point, respectively.

        """
        left_angle = obj.ry + obj.inter_angle / 2
        right_angle = obj.ry - obj.inter_angle / 2
        

        polyline = [[(obj.tx + obj.width / 2), obj.ty],
                    [(obj.tx - obj.width / 2), obj.ty],
                    
                    [(obj.tx + obj.inter_space * (cos(pi/2 - right_angle))),
                     (obj.ty + obj.inter_space * (sin(pi/2 - right_angle)))],

                    [(obj.tx + obj.inter_space * (cos(pi/2 - left_angle))),
                     (obj.ty + obj.inter_space * (sin(pi/2 - left_angle)))]

                    ]

        return polyline

    def calculate_affordance_circular(self, obj):
        """
        Calculates an array of coordinates for a polyline representing the affordances
        of an object, based on the object's dimensions, width, depth, and angle shift.

        Args:
            obj (`Objet` instance.): 2D shape or object whose boundaries are to
                be created as a polyline.
                
                		- `tx`: The x-coordinate of the top-left corner of the shape.
                		- `ty`: The y-coordinate of the top-left corner of the shape.
                		- `depth`: The height of the shape.
                		- `width`: The width of the shape.
                		- `inter_space`: A variable that determines how much space is
                inside the shape, used for shifting angles and coordinates.
                
                	In each iteration of the for-loop, the angle `phi` is incremented
                by `angle_shift`, which is a value computed as `pi*2` divided by
                the number of points in the polyline (`points`). The x-coordinate
                and y-coordinate of each point on the polyline are then calculated
                using the sine and cosine of `phi`, along with the values of
                `obj.tx` and `obj.ty`. The resulting points are appended to the
                `polyline` list.

        Returns:
            list: a list of polygon vertices representing the circular affordance
            of an object.

        """
        polyline = []
        points = 50
        angle_shift = pi*2 / points
        phi = 0

        for i in range(points):
            phi += angle_shift
            polyline.append([obj.tx + ((obj.width/2 + obj.inter_space)*sin(phi)),
                             obj.ty + ((obj.depth/2 + obj.inter_space)*cos(phi))])


        return polyline

    def calculate_affordance_rectangular(self, obj):

        """
        Creates a polyline representation of an affordance region, defined by a
        series of four points in a 2D space. The resulting polyline delineates the
        boundary of the affordance region around an object.

        Args:
            obj (int): 2D object for which a polygon is being generated.

        Returns:
            Array` containing four/five coordinates representing the rectangle's
            boundary: a 4-point Polyline representation of the Affordance area for
            the given Object.
            
            	1/ polyline: This is a four-element array representing the polygon
            that defines the affordance area of the object. The coordinates of the
            vertices of the polygon are provided in the order [tx, ty, tx + width
            / 2, ty, tx + width / 2, ty + depth / 2, etc.]
            	2/ obj: This is an object containing properties related to the object
            being analyzed, such as its transaction, top, bottom, left, and right
            dimensions, as well as its depth.

        """
        polyline = [[obj.tx - obj.width / 2 - obj.inter_space, obj.ty - obj.depth / 2 - obj.inter_space],
                    [obj.tx + obj.width / 2 + obj.inter_space, obj.ty - obj.depth / 2 - obj.inter_space],
                    [obj.tx + obj.width / 2 + obj.inter_space, obj.ty + obj.depth / 2 + obj.inter_space],
                    [obj.tx - obj.width / 2 - obj.inter_space, obj.ty + obj.depth / 2 + obj.inter_space]]
        return polyline

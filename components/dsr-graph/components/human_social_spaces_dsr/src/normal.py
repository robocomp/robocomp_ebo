import numpy as np


class Normal(object):
    _dimensions = 0
    _mu = np.empty(0)
    _sigma = np.empty(0)
    _ellip = False

    two_pi = np.pi + np.pi
    half_pi = np.pi * 0.5

    def __init__(self, mu, sigma, dimensions=None, elliptical=False):

        """
        Sets the dimensions, mu and sigma parameters based on user input or default
        values. It also assigns these values to class variables `dimensions`, `mu`,
        and `sigma`.

        Args:
            mu (`numpy.array`.): 2D mean vector of the data points in the input array.
                
                	1/ `dimensions`: If provided, `dimensions` represents the number
                of dimensions in the input data. This value is used to create the
                necessary dimensions for the density estimate.
                	2/ `_dimensions`: The instance attribute `self._dimensions` stores
                the dimension of the input data.
                	3/ `_mu`: The instance attribute `self._mu` holds a numpy array
                containing the mean values of the input data.
                	4/ `_sigma`: The instance attribute `self._sigma` holds a numpy
                array containing the standard deviation values of the input data.
                	5/ `_ellip`: If dimensions is equal to 2, then the instance
                attribute `self._ellip` holds a boolean value indicating whether
                the density estimate should be an elliptical distribution.
                
                	In summary, these attributes define the structure of the input
                data and are used in subsequent operations to construct the density
                estimate.
            sigma (ndarray, according to the supplied code fragments.): 2D covariance
                matrix of the Gaussian distribution in the provided function.
                
                	1/ `dimensions`: If `dimensions` is provided, it sets the
                dimensionality of the `sigma` array to the value of `dimensions`.
                (passed as argument)
                	2/ `_dimensions`: This attribute is set to the value of `dimensions`
                (as passed in `__init__`) and is used to store the dimensionality
                of the `sigma` array. (assigned as attribute)
                	3/ `_mu`: If ` dimensions `is equal to the length of `mu`, a copy
                of the input array `mu` is created and stored in the `_mu` attribute.
                (`np.array(mu)`)
                	4/ `_sigma`: Similarly, if `dimensions` is equal to the length
                of `sigma`, a copy of the input array `sigma` is created and stored
                in the `_sigma` attribute. (`np.array(sigma)`)
                	5/ `_ellip`: If `dimensions` is equal to 2, an instance of the
                `Elliptical distribution` is created and stored in the `_ellip`
                attribute. (created using `elliptical`)
            dimensions (int): 0-based index of the dimension of the Gaussian mixture
                model, which determines the size of the array required to store
                the mu and sigma values for the function.
            elliptical (array of numerical values.): 2D ellipse shape of the
                Gaussian mixture distribution.
                
                		- `elliptical`: This attribute represents the ellipse properties
                of the generated code documentation. It is a NumPy array with shape
                (2,) or (3,) containing the major and minor axis lengths for an
                ellipse in Cartesian coordinates. The length of this array determines
                the number of dimensions in the ellipse representation. If
                `dimensions` is equal to `len(mu)`, then `elliptical` is defined
                as a NumPy array.

        """
        if dimensions is None:
            dimensions = len(mu)

        self._dimensions = dimensions

        if dimensions == len(mu):
            self._mu = np.array(mu)
            self._sigma = np.array(sigma)

            if dimensions == 2:
                self._ellip = elliptical

    def __str__(self):
        return "Normal ( mu = {0} , sigma = {1} , elliptical = {2} )".format(self._mu.tolist(), self._sigma.tolist(),
                                                                             self._ellip)

    def __repr__(self):
        return str(self)

    @staticmethod
    def _calcExp(grids, mu, const, sigmaI, result):
        """
        Takes input arrays `grids`, `mu`, `const`, `sigmaI`, and `result`. It
        applies a convolution operation to each slice of the grid using the Gaussian
        kernel, updating the output array `result`. The kernel size is calculated
        automatically based on the shapes of the input arrays.

        Args:
            grids (ndarray object.): 2D grid of data to be processed for Bayesian
                inference, and it is used to calculate the likelihood of the
                observations given the parameters of the model.
                
                		- `shape`: The shape of the input array, which can be either
                (n_samples, n_features) or (n_samples,).
                		- `dtype`: The data type of the input array, which is assumed
                to be float64.
                
                	In the case where `len(grids.shape) == 2`, the function iterates
                over each row of the input array, performing a dot product operation
                on each row with a learnable parameter matrix `mu` and a noise
                covariance matrix `sigmaI`. The resulting vector is then added to
                a constant vector `const` using element-wise multiplication.
                
                	In the case where `len(grids.shape) > 2`, the function uses a
                loop to iterate over each column of the input array, performing a
                dot product operation on each column with a learnable parameter
                matrix `mu` and a noise covariance matrix `sigmaI`. The resulting
                vector is then added to a constant vector `const` using element-wise
                multiplication.
            mu (ndarray (a multidimensional array).): μ parameter in the exponential
                function used for the normal distribution calculation.
                
                		- `mu`: The mean value of the normal distribution, passed as an
                argument to the function. It is a scalar or a tensor with the shape
                `(N, 1)` where `N` is the number of elements in the input array.
            const (float): scaling factor used to modulate the output of the
                function for each grid point.
            sigmaI (2D array or matrix.): 2nd moment of the normal distribution
                about the mean `mu`, which is used to calculate the exponentially
                weighted moving average of the output at each iteration in the function.
                
                		- `sigmaI` is an instance of a class that has an attribute called
                `__array__`, which is set to `True`. This indicates that the array
                can be interpreted as a scalar or a dense array.
                		- `sigmaI` has a shape of `(3, 3)`, indicating that it is a 3x3
                covariance matrix.
                		- The attributes of `sigmaI` are: `__array__`, `__class__`,
                `__dict__`, `__getattribute__`, `__hash__`, `__init__`, `__ne__`,
                `__new__`, `__not_equal__`, `__positive__`, `__real__`, `__repr__`,
                `__setattr__`, `__sizeof__`, `__str__`, and `__weakref__.`.
                		- `sigmaI` has a docstring that explains its purpose and usage
                in the `_calcExp` function.
            result (1D array.): 2D grid that will hold the output of the function
                after application of the normal distribution transformation.
                
                		- `result` is a tensor with shape `(n_samples, n_parameters)`
                where `n_samples` is the number of samples and `n_parameters` is
                the number of parameters in the model.
                		- If `len(grids.shape) == 2`, then `result` has a single dimension
                representing the parameter values, while if `len(grids.shape) !=
                2`, `result` has two dimensions representing the sample and parameter
                values respectively.
                		- The elements of `result` represent the estimated expected value
                of the probability distribution for each sample-parameter combination.

        """
        if len(grids.shape) == 2:
            for i in range(grids.shape[-1]):
                sub = grids[:, i][np.newaxis].T - mu
                result[i] += const * np.exp(-0.5 * np.dot(sub.T, np.dot(sigmaI, sub))[0, 0])
        else:
            for i in range(grids.shape[-1]):
                Normal.calcExp(grids[:, i], mu, const, sigmaI, result[i])

    @staticmethod
    def makeGrid(normals, h, dimensions=None, limits=None, resolution=0.1):
        """
        Takes a list of `Normal` objects, dimensions, limits, and resolution as
        input. It generates a 2D grid using the normals' bounds and adds them to
        the grid, returning the grid and the resulting array.

        Args:
            normals (ndarray.): 2D or 3D data points that define the surface of
                the object being rendered, and it is used to generate the meshgrid
                for the given dimensions.
                
                	1/ `len(normals) == 0`: If the length of `normals` is zero, then
                the function returns `None`.
                	2/ `dimensions is None`: If `dimensions` is not provided as an
                input, it will be inferred from the first normal vector in `normals`.
                The `getDimensions()` method of each normal vector is called to
                obtain the dimension.
                	3/ `limits is None`: If `limits` is not provided as an input,
                default limits are created for each normal vector in `normals`.
                Each limit is initialized with the values `np.inf` and `-np.inf`.
                The `getBounds()` method of each normal vector is called to obtain
                the bounding box dimensions.
                	4/ `axes`: A list of arrays containing discrete points along each
                dimension of the grid. Each array has a shape of `(resolution,)`
                where `resolution` is the spacing between points in that dimension.
                	5/ `grids`: An array with shape `(N,)` where `N` is the number
                of dimensions in the grid. Each element `grids[i]` is a 2D array
                containing the coordinate values for that dimension in the grid.
                	6/ `result`: An array with shape `(M,)` where `M` is the number
                of points in the result grid. Each element `result[i]` is the value
                at the specified coordinates in the grid.
                	7/ `normals`: A list of normal vectors, each with its own set of
                properties such as magnitude, direction, and dimensionality.
            h (float): 2D grid resolution and is used to determine the size of the
                bounds in each dimension of the normals array.
            dimensions (ndarray (either scalar or multi-dimensional).): 1D array
                of dimensions of each normal vector in the input `normals` list.
                
                		- If `dimensions` is `None`, it indicates that no information
                about dimensions is available in the given input.
                		- If `dimensions` is a non-empty tuple or list, it contains the
                number of dimensions present in the input. This information can
                be used to determine the shape of the output grid.
                		- The property `getDimensions()` may be used to retrieve the
                number of dimensions present in the input normal vector. It returns
                an integer value indicating the number of dimensions.
            limits (int): 2D bounding box of each normal vector in the input
                `normals` list, and is used to create a multi-dimensional grid
                that covers the entire output space.
            resolution (int): spacings between each point in the generated meshgrid,
                and determines the level of detail in the resulting grid.

        Returns:
            array` or `grid: a tuple containing two arrays: `grids` and `result`.
            
            		- `grids`: A 2D array with shape `(n_dimensions, resolution)`
            containing the grid coordinates for each dimension.
            		- `result`: An array with shape `(n_samples, n_dimensions)` containing
            the final result of the function, which is the output of the normal
            distributions after being added to the grid coordinates.
            
            	The returned value `grids, result` represents a tuple of two arrays:
            `grids` contains the grid coordinates for each dimension, and `result`
            contains the final output of the function. The shape of `grids` is
            `(n_dimensions, resolution)`, where `n_dimensions` is the number of
            dimensions in the input data, and `resolution` is the resolution of
            the grid. The shape of `result` is `(n_samples, n_dimensions)`, where
            `n_samples` is the number of samples generated by the normal distributions,
            and `n_dimensions` is the number of dimensions in the input data.
            
            	The `makeGrid` function first checks if there are any data points
            provided as input (`len(normals) != 0`). If there are no data points,
            it returns `None`. Otherwise, it proceeds to determine the dimensions
            and limits of the grid based on the input normal distributions. It
            then creates an array of grid coordinates for each dimension using
            `np.meshgrid`, and adds the output of each normal distribution to the
            corresponding coordinate in the grid using `np.zeros` and `np.add`.
            The final output is a tuple of two arrays: `grids` and `result`.

        """
        if len(normals) == 0:
            return None  # No hay datos, devuelve None o lo que sea apropiado en tu caso.

        if dimensions is None:
            dimensions = normals[0].getDimensions()

        if limits is None:
            limits = [[np.inf, -np.inf] for _ in range(dimensions)]
            for normal in normals:
                local = normal.getBounds(h)
                limits = [
                    [min(local[i][0], limit[0]), max(local[i][1], limit[1])]
                    for i, limit in enumerate(limits)
                ]

        axes = [np.arange(limit[0], limit[1], resolution) for limit in limits]
        grids = np.array(np.meshgrid(*axes))

        result = np.zeros(grids.shape[1:])
        
        for normal in normals:
            normal.addTo(grids, result)
        
        return grids, result


    # def makeGrid(normals, h, dimensions=None, limits=None, resolution=0.1, grids=None):
    #     if len(normals) > 0:
    #         axes = []
    #         if grids is None:
    #             if dimensions is None:
    #                 dimensions = normals[0].getDimensions()
    #             if limits is None:
    #                 limits = [[np.inf, -np.inf] for _ in range(dimensions)]
    #                 for normal in normals:
    #                     local = normal.getBounds(h)
    #                     for i in range(dimensions):
    #                         if local[i][0] < limits[i][0]:
    #                             limits[i][0] = local[i][0]
    #                         if local[i][1] > limits[i][1]:
    #                             limits[i][1] = local[i][1]
    #             for limit in limits:
    #                 axes.append(np.arange(limit[0], limit[1], resolution))
    #             grids = np.array(np.meshgrid(*axes))
    #         result = np.zeros(grids.shape[1:])
    #         for normal in normals:
    #             normal.addTo(grids, result)
    #         return grids, result

    def move(self):
        """
        Updates the position and orientation of an object based on random noise.
        It adjusts the mass matrix, axis, and orientation.

        """
        self._mu += np.random.uniform(-0.1, 0.1, self._mu.shape)
        self._sigma += np.random.uniform(0.1, 0.11, self._sigma.shape)
        if self._ellip:
            self._sigma[0] = np.arctan2(np.sin(self._sigma[0]), np.cos(self._sigma[0]))
            self._sigma[1] = 2.0
            self._sigma[2] = 1.0
            self._sigma[3] = 4 / 3

    def getBounds(self, h):

        """
        Calculates and returns the bounds of a distribution based on its covariance
        matrix. It takes into account the shape of the distribution, the position
        of the mean, and the dimensions of the space to generate the limits for
        each dimension.

        Args:
            h (float): 4-dimensional covariance matrix's scale factor and is used
                to compute the limits of the normal distribution.

        Returns:
            str: a list of lists, where each sub-list contains the minimum and
            maximum values for each dimension of the Gaussian distribution.

        """
        if self._ellip:

            const = 3 / (0.8 + h)

            r = const / self._sigma[1]
            min_x = max_x = r * np.cos(self._sigma[0] + np.pi) + self._mu[0, 0]
            min_y = max_y = r * np.sin(self._sigma[0] + np.pi) + self._mu[1, 0]

            r = const / self._sigma[2]
            x = r * np.cos(self._sigma[0]) + self._mu[0, 0]
            y = r * np.sin(self._sigma[0]) + self._mu[1, 0]

            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y

            r = const / self._sigma[3]
            x = r * np.cos(self._sigma[0] + Normal.half_pi) + self._mu[0, 0]
            y = r * np.sin(self._sigma[0] + Normal.half_pi) + self._mu[1, 0]

            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y

            x = r * np.cos(self._sigma[0] - Normal.half_pi) + self._mu[0, 0]
            y = r * np.sin(self._sigma[0] - Normal.half_pi) + self._mu[1, 0]

            if x < min_x:
                min_x = x
            elif x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            elif y > max_y:
                max_y = y

            limits = [[min_x, max_x], [min_y, max_y]]
        else:
            const = 2
            limits = [[np.inf, -np.inf] for _ in range(self._dimensions)]
            for i in range(self._dimensions):
                cov = self._sigma[i, i] * const + const / self._sigma[i, i]
                axis = self._mu[i, 0] - cov
                if axis < limits[i][0]:
                    limits[i][0] = axis
                axis = self._mu[i, 0] + cov
                if axis > limits[i][1]:
                    limits[i][1] = axis
        return limits

    def addTo(self, grids, result):
        """
        Calculates the contribution to a normal distribution of an observation at
        a given location and dimension, based on the standard deviation vector and
        the mean vector.

        Args:
            grids (ndarray (N-dimensional array).): 2D or 3D grid of discrete
                points that are used to compute the Gaussian kernel density estimate.
                
                		- `grids[0]` and `grids[1]`: These are the grid points in the
                3D space, where `grids[0]` represents the coordinates of the point
                on the x-axis, `grids[1]` represents the coordinates of the point
                on the y-axis, and `grids[2]` represents the coordinates of the
                point on the z-axis.
                		- `_mu`: A 3x3 matrix representing the mean position of the
                distribution in the 3D space. The matrix has three rows and three
                columns, with each element representing a coordinate in the 3D space.
                		- `self._sigma`: A 3x3 matrix representing the covariance of the
                distribution in the 3D space. The matrix has three rows and three
                columns, with each element representing a square of the standard
                deviation at a particular coordinate in the 3D space.
                		- `_dimensions`: An integer representing the number of dimensions
                in the 3D space, which is either 3 (for a full 3D space) or 2 (for
                a plane in 3D space).
                
                	The `addTo` function then performs the following operations based
                on the input `grids`:
                
                		- For a 3D space: Computes the distance between each grid point
                and the mean position, and squares the result to obtain the squared
                distances. Then, computes the exponent of the distances using the
                covariance matrix and normalizes the result.
                		- For a 2D space: Computes the distance between each grid point
                and the mean position in the x-y plane, squares the result, and
                normalizes the result using the determinant of the covariance
                matrix and the distance between the mean positions in the x- and
                y-axes.
                
                	The resulting expression represents the probability density
                function of the distribution at the input `grids`.
            result (float): 1D or 2D random walker's probability density at a given
                point in space, and it is calculated using the Gaussian mixture
                model based on the grid positions, the mixutal parameters, and the
                dimension of the space.

        """
        if self._ellip:

            dx = grids[0] - self._mu[0, 0]
            dy = grids[1] - self._mu[1, 0]

            alpha = np.arctan2(dy, dx) - (self._sigma[0] - Normal.half_pi)
            alpha = alpha > (Normal.two_pi * np.floor((alpha + np.pi) / Normal.two_pi))
            sigma_sq = np.where(alpha, self._sigma[1] * self._sigma[1], self._sigma[2] * self._sigma[2])

            cos_theta = np.cos(self._sigma[0])
            cos_theta = cos_theta * cos_theta * 0.5
            sin_theta = np.sin(self._sigma[0])
            sin_theta = sin_theta * sin_theta * 0.5
            sin_2theta = np.sin(self._sigma[0] + self._sigma[0]) * 0.25

            sigma_3_sq = self._sigma[3] * self._sigma[3]

            a = cos_theta * sigma_sq + sin_theta * sigma_3_sq
            b = (sin_2theta * (sigma_sq - sigma_3_sq)) * dx * dy
            c = sin_theta * sigma_sq + cos_theta * sigma_3_sq

            result += np.exp(-(a * dx * dx + (b + b) + c * dy * dy))

        elif self._dimensions == 2:
            ox = np.sqrt(self._sigma[0, 0])
            oy = np.sqrt(self._sigma[1, 1])
            rho = self._sigma[0, 1] / (ox * oy)
            rho_sqrt = np.sqrt(1.0 - rho * rho)
            rho_sqrt += rho_sqrt
            dx = (grids[0] - self._mu[0, 0]) / ox
            dy = (grids[1] - self._mu[1, 0]) / oy
            result += (1.0 / (np.pi * ox * oy * rho_sqrt)) * np.exp((-1.0 / rho_sqrt) *
                                                                    ((dx * dx) + (dy * dy) - ((rho + rho) * dx * dy)))
        else:
            Normal._calcExp(grids, self._mu, (1.0 / np.sqrt(((Normal.two_pi) ** self._dimensions) *
                                                            np.linalg.det(self._sigma))), np.linalg.inv(self._sigma),
                            result)

    def getMu(self):
        return self._mu

    def getSigma(self):
        return self._sigma

    def getDimensions(self):
        return self._dimensions

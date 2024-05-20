import unittest
from pydsr import *
import numpy as np

class Test(unittest.TestCase):


    def test_create_attribute_int32(self):

        """
        Tests various types of attributes assigned to the `vehicle_id` attribute
        of a Node with an int32 type, raisingTypeError for incorrect data types.

        """
        a = Node(12, "root", "elmundo")

        #int32
        a.attrs["vehicle_id"] = Attribute(10, 1)
        a.attrs["vehicle_id"].value = 11
        a.attrs["vehicle_id"].value = int(24)
        a.attrs["vehicle_id"].value = int(12.45)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute("10.0", 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute([10.0], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"] = Attribute([10.0, 11.2], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = "string"
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = 10.0
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = [10]
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = [10.0]
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = np.array([1.2, 4.4], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_id"].value = (10,)

    def test_create_attribute_bool(self):
        """
        Tests various ways to create an attribute with a boolean value and checks
        that any attempts to pass non-boolean values raise a `TypeError`.

        """
        a = Node(12, "root", "elmundo")

        #bool
        a.attrs["vehicle_occupancy"] = Attribute(True, 1)
        a.attrs["vehicle_occupancy"].value = False
        a.attrs["vehicle_occupancy"].value = True
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute("10.0", 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute([10.0], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"] = Attribute([10.0, 11.2], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"].value = 1
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"].value = 1.0
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"].value = "True"
        with self.assertRaises(TypeError):
            a.attrs["vehicle_occupancy"].value = [True]

    def test_create_attribute_float(self):
        #We do not check precission loss on Python floats to C++ floats.

        """
        Tests the creation and assignment of floating-point attributes to a Node
        object. It checks that attempting to assign an invalid data type, such as
        a boolean or string, raises a TypeError.

        """
        a = Node(12, "root", "elmundo")

        #float
        a.attrs["vehicle_steer"] = Attribute(1.0, 1)
        a.attrs["vehicle_steer"].value = 1.0
        a.attrs["vehicle_steer"].value = float(12)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute("10.0", 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute([10.0], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"] = Attribute([10.0, 11.2], 1)
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"].value = 1
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"].value = "1.0"
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"].value = [1.0]
        with self.assertRaises(TypeError):
            a.attrs["vehicle_steer"].value = np.array([1.2], dtype=np.float)


    def test_create_attribute_double(self):
        """
        Tests various scenarios for creating an attribute with a double type in
        Python's numpy array. It raises a TypeError for invalid inputs, ensuring
        that only valid attributes are created.

        """
        a = Node(12, "root", "elmundo")

        #double
        a.attrs["test_double_type"] = Attribute(1.0, 1)
        a.attrs["test_double_type"] = Attribute(1.132432543543645646703, 1)
        a.attrs["test_double_type"].value = 1.0
        a.attrs["test_double_type"].value = 1.132432543543645646703
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute("10.0", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute([10.0], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute([10.0, 11.2], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = 1
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = "1.0"
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = np.array([1.2], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = [10.0]
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"] = Attribute(-12, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = -12
        with self.assertRaises(TypeError):
            a.attrs["test_double_type"].value = True


    def test_create_attribute_string(self):
        """
        Tests various attempts to create an attribute value that is not a valid
        string. It does so by providing different types of values, such as numbers,
        lists, dictionaries, and booleans, and asserting that each attempt raises
        a `TypeError`.

        """
        a = Node(12, "root", "elmundo")

        #string
        a.attrs["name"] = Attribute("Prueba", 1)
        a.attrs["name"].value = "Prueba"
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute([10.0], 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["name"] = Attribute([10.0, 11.2], 1)
        with self.assertRaises(TypeError):
            a.attrs["name"].value = 1
        with self.assertRaises(TypeError):
            a.attrs["name"].value = np.array([1.2], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["name"].value = [10.0]
        with self.assertRaises(TypeError):
            a.attrs["name"].value = True

    def test_create_attribute_vec_float(self):

        """
        Tests the creation and modification of an `Attribute` vector with float
        values in a given node. It checks that only valid data types can be assigned
        to the `rt_translation` attribute and raises type errors for incorrect input.

        """
        a = Node(12, "root", "elmundo")
        #vec float
        a.attrs["rt_translation"] = Attribute([10.0], 1)
        a.attrs["rt_translation"] = Attribute([10.0, 11.2], 1)
        a.attrs["rt_translation"] = Attribute(np.array([1.2, 4.4], dtype=np.float), 1)
        a.attrs["rt_translation"].value = [10.0, 11.2]
        a.attrs["rt_translation"].value = np.array([1.2, 4.4], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(np.array([12, 44], dtype=np.uint8), 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"] = Attribute(np.array([12, 44], dtype=np.uint64), 1)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"].value = [10, 11]
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"].value = np.array([1, 4], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"].value = 11.0
        #with self.assertRaises(TypeError):
        #    a.attrs["rt_translation"].value = [10.0, True, 1]
        with self.assertRaises(TypeError):
            a.attrs["rt_translation"].value = [[11.0, 0.0, 1.1]]


    def test_create_attribute_vec_bytes(self):
        """
        Tests various invalid input values for the `Attribute` class, trying to
        assign them to the `cam_image` attribute of a node. It raises a `TypeError`
        in each case, indicating that only numerical or boolean values are allowed.

        """
        a = Node(12, "root", "elmundo")

        #vec bytes
        a.attrs["cam_image"] = Attribute([100], 1)
        a.attrs["cam_image"] = Attribute([100, 112], 1)
        a.attrs["cam_image"] = Attribute(np.array([12, 44], dtype=np.uint8), 1)
        a.attrs["cam_image"].value = [100, 112]
        a.attrs["cam_image"].value = np.array([12, 44], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute([10, "a"], 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"] = Attribute(np.array([12.5, 44.2, 1], dtype=np.float), 1)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = np.array([12456, 41233544], dtype=np.uint32)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = np.array([12456, 41233544], dtype=np.uint64)
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = [12456, 41233544]
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = [1.0, 244.0]
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = [10, 1.0]
        with self.assertRaises(TypeError):
            a.attrs["cam_image"].value = [[11, 0, 1]]

    def test_create_attribute_uint32(self):
        """
        Tests various attributes assigned to an element with uint32 type, and
        raises a TypeError when invalid data types are inputted.

        """
        a = Node(12, "root", "elmundo")

        #uint32
        a.attrs["test_uint32_type"] = Attribute(100, 1)
        a.attrs["test_uint32_type"] = Attribute(1, 1)
        a.attrs["test_uint32_type"] = Attribute(0, 1)
        a.attrs["test_uint32_type"].value = 100
        a.attrs["test_uint32_type"].value = int(100)
        a.attrs["test_uint32_type"].value = int(100.0)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute([10, "a"], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute([10.0, 12.,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute([10, 11], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute(np.array([12.5, 44.2, 1], dtype=np.float), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"] = Attribute(-12, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"].value = 100.0
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"].value = "100"
        with self.assertRaises(TypeError):
            a.attrs["test_uint32_type"].value = True

    def test_create_attribute_uint64(self):
        """
        Tests whether the `Attribute` class can handle different types of inputs
        when setting the value of an attribute in a Node object. It raises a
        `TypeError` for incorrect input types.

        """
        a = Node(12, "root", "elmundo")

        #uint64
        a.attrs["parent"] = Attribute(100, 1)
        a.attrs["parent"] = Attribute(3689348814741910323, 1)
        a.attrs["parent"].value = 100
        a.attrs["parent"].value = 3689348814741910323
        a.attrs["parent"] = Attribute(0, 1)

        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute([10, "a"], 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute([10.0, 12.,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute([10, 11], 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute(np.array([12.5, 44.2, 1], dtype=np.float), 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"] = Attribute(-12, 1)
        with self.assertRaises(TypeError):
            a.attrs["parent"].value = -12
        with self.assertRaises(TypeError):
            a.attrs["parent"].value = True
        with self.assertRaises(TypeError):
            a.attrs["parent"].value = 1.0




    def test_create_attribute_u64_vec(self):
        """
        Tests various invalid inputs for the `Attribute` class's `value` parameter,
        which is expected to be a vector of integers represented as unsigned 64-bit
        integers.

        """
        a = Node(12, "root", "elmundo")

        #u64_vec
        a.attrs["test_uint64_vec_type"] = Attribute([256], 1)
        a.attrs["test_uint64_vec_type"] = Attribute([100], 1)
        a.attrs["test_uint64_vec_type"] = Attribute([100, 112], 1)
        a.attrs["test_uint64_vec_type"] = Attribute(np.array([12, 44], dtype=np.uint64), 1)
        a.attrs["test_uint64_vec_type"].value = [100, 112]
        a.attrs["test_uint64_vec_type"].value = np.array([12, 44], dtype=np.uint64)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute([10, "a"], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"] = Attribute(np.array([12.5, 44.2, 1], dtype=np.float), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"].value = np.array([12456, 41233544], dtype=np.uint32)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"].value = np.array([1245.0, 0.41233544], dtype=np.float)
        #with self.assertRaises(TypeError):
        #    a.attrs["test_uint64_vec_type"].value = np.array([12, 41], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"].value = [1.0, 244.0]
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"].value = [10, 1.0]
        with self.assertRaises(TypeError):
            a.attrs["test_uint64_vec_type"].value = [[11, 0, 1]]


    def test_create_attribute_vec2(self):
        """
        Tests various attribute assignments to a Node's `attrs` dictionary with
        the wrong data types, raising a `TypeError`.

        """
        a = Node(12, "root", "elmundo")


        #vec2
        a.attrs["test_vec2_type"] = Attribute([10.0, 1.0], 1)
        a.attrs["test_vec2_type"] = Attribute([10.0, 11.2], 1)
        a.attrs["test_vec2_type"] = Attribute(np.array([1.2, 4.4], dtype=np.float), 1)
        a.attrs["test_vec2_type"].value = [10.0, 11.2]
        a.attrs["test_vec2_type"].value = np.array([1.2, 4.4], dtype=np.float)
        a.attrs["test_vec2_type"] = Attribute((10.0, 11.1), 1)
        a.attrs["test_vec2_type"].value = (10.0, 11.1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(np.array([12, 44], dtype=np.uint8), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"] = Attribute(np.array([12, 44], dtype=np.uint64), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = [10, 11]
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = np.array([1, 4], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = 11.0
        #with self.assertRaises(TypeError):
        #    a.attrs["test_vec2_type"].value = [10.0, True]
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = [[11.0, 0.0]]
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = np.array([1.2, 4.4, 1.0], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec2_type"].value = np.array([1.2], dtype=np.float)


    def test_create_attribute_vec3(self):
        """
        Tests various attribute types and values to verify their compatibility
        with the `attrs` property of a `Node` object.

        """
        a = Node(12, "root", "elmundo")

        #vec3
        a.attrs["test_vec3_type"] = Attribute([10.0, 1.0, 0.0], 1)
        a.attrs["test_vec3_type"] = Attribute([10.0, 11.2, 0.0], 1)
        a.attrs["test_vec3_type"] = Attribute(np.array([1.2, 4.4, 0.0], dtype=np.float), 1)
        a.attrs["test_vec3_type"].value = [10.0, 11.2, 0.0]
        a.attrs["test_vec3_type"].value = np.array([1.2, 4.4, 0.0], dtype=np.float)
        a.attrs["test_vec3_type"] = Attribute((10.0, 11.1, 11.1), 1)
        a.attrs["test_vec3_type"].value = (10.0, 11.1, 11.1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute([10, 12,22], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(np.array([12, 44, 0], dtype=np.uint8), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"] = Attribute(np.array([12, 44, 0], dtype=np.uint64), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = [10, 11]
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = np.array([1, 4, 3], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = 11.0
        #with self.assertRaises(TypeError):
        #    a.attrs["test_vec3_type"].value = [10.0, True, 1.0]
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = [[11.0, 0.0, 0.0]]
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = np.array([1.2, 4.4, 1.0, 0.0], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = np.array([1.2], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = (10.0, 11.1, 11.1, 1.0)
        with self.assertRaises(TypeError):
            a.attrs["test_vec3_type"].value = (10.0, 11.1)
        #with self.assertRaises(TypeError):
        #     a.attrs["test_vec3_type"].value = (10.0, False, 1.0)

    def test_create_attribute_vec4(self):

        """
        Tests various ways to assign an Attribute object with a numpy array as its
        value, and checks that it raises a `TypeError` when attempting to assign
        invalid data types or values.

        """
        a = Node(12, "root", "elmundo")

        #vec4
        a.attrs["test_vec4_type"] = Attribute([10.0, 1.0, 0.0, 1.0], 1)
        a.attrs["test_vec4_type"] = Attribute([10.0, 11.2, 0.0, 1.0], 1)
        a.attrs["test_vec4_type"] = Attribute(np.array([1.2, 4.4, 1.0, 0.0], dtype=np.float), 1)
        a.attrs["test_vec4_type"].value = [10.0, 11.2, 0.0, 1.0]
        a.attrs["test_vec4_type"].value = np.array([1.2, 4.4, 6.3, 0.0], dtype=np.float)
        a.attrs["test_vec4_type"].value = (10.0, 11.1, 11.0, 11.0)

        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute([10, 12,22, 1], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(np.array([12, 44, 0, 2], dtype=np.uint8), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"] = Attribute(np.array([12, 44, 0, 3], dtype=np.uint64), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = [10, 11]
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = np.array([1, 4, 3, 5], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = 11.0
        #with self.assertRaises(TypeError):
        #    a.attrs["test_vec4_type"].value = [10.0, True, 1.0, 1.0]
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = [[11.0, 0.0, 0.0, 1.0]]
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = np.array([1.2, 4.4, 1.0, 0.0, 0.0], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec4_type"].value = np.array([1.2], dtype=np.float)


    def test_create_attribute_vec6(self):
        """
        Tests various ways to assign and retrieve values for an attribute of type
        `np.darray` in a Node object.

        """
        a = Node(12, "root", "elmundo")

        #vec6
        a.attrs["test_vec6_type"] = Attribute([10.0, 1.0, 0.0, 1.2, 4.4, 0.0], 1)
        a.attrs["test_vec6_type"] = Attribute([10.0, 11.2, 0.0, 1.2, 4.4, 0.0], 1)
        a.attrs["test_vec6_type"] = Attribute(np.array([1.2, 4.4, 0.0, 1.2, 4.4, 0.0], dtype=np.float), 1)
        a.attrs["test_vec6_type"].value = [10.0, 11.2, 0.0, 1.2, 4.4, 0.0]
        a.attrs["test_vec6_type"].value = np.array([1.2, 4.4, 0.0, 1.2, 4.4, 0.0], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(True, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(10.0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(1, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(0, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(1110, 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute([10], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute("[10.0]", 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute([10, 12,22,1, 4, 3], 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(np.array([12, 44, 0,1, 4, 3], dtype=np.uint8), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"] = Attribute(np.array([12, 44, 0,1, 4, 3], dtype=np.uint64), 1)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = [10, 11]
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = np.array([1, 4, 3,1, 4, 3], dtype=np.uint8)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = 11.0
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = (10.0, 11.1)
        #with self.assertRaises(TypeError):
        #    a.attrs["test_vec6_type"].value = [10.0, True, 1.0,11.0, 0.0, 0.0]
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = [[11.0, 0.0, 0.0,11.0, 0.0, 0.0]]
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = np.array([1.2, 4.4, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float)
        with self.assertRaises(TypeError):
            a.attrs["test_vec6_type"].value = np.array([1.2], dtype=np.float)



if __name__ == '__main__':
    #import psutil
    #if psutil.Process(os.getpid()).parent().name() == 'sh':
    #    unittest.main()
    #else:
    #    print("You probably want to execute test with the runTest.sh script.")
    unittest.main()
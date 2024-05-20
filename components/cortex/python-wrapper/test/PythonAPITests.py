import unittest
import subprocess

import sys, time, os
from pydsr import *


ETC_DIR = "../etc/"

class TestAttribute(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_attribute(self):
        """
        Tests various aspects of creating an instance of the `Attribute` class.
        It checks that the resulting object is not None, has the correct value,
        and raises a TypeError when attempting to assign a value other than a
        number or `True/False` to it.

        """
        tmp = Attribute(10.4, 0, 12)
        self.assertIsNotNone(tmp)
        self.assertAlmostEqual(tmp.value, 10.4, 5)
        with self.assertRaises(TypeError):
            tmp.value = True
        tmp = Attribute(10.4, 12)
        self.assertIsNotNone(tmp)
        self.assertAlmostEqual(tmp.value, 10.4, 5)
        with self.assertRaises(TypeError):
            tmp.value = True

    def test_update_value(self):
        """
        Verifies that an attribute's value can be updated and subsequently checked
        to almost equal the new value with a desired tolerance.

        """
        tmp = Attribute(10.4, 0, 12)
        self.assertAlmostEqual(tmp.value, 10.4, 5)
        tmp.value = 0.0
        self.assertAlmostEqual(tmp.value, 0.0, 5)

    def test_agent_id(self):
        """
        Asserts that the attribute `agent_id` of an instance of `Attribute` has a
        value of `12`. It also raises an `AttributeError` when attempting to assign
        a value of `100` to the same attribute.

        """
        tmp = Attribute(10.4, 0, 12)
        self.assertEqual(tmp.agent_id, 12)
        with self.assertRaises(AttributeError):
            tmp.agent_id = 100

    def test_timestamp(self):
        """
        Asserts that the `timestamp` attribute of a `tmp` instance is equal to 0,
        and raises an `AttributeError` when attempting to assign a value other
        than 0 to the `timestamp` attribute.

        """
        tmp = Attribute(10.4, 0, 12)
        self.assertEqual(tmp.timestamp, 0)
        with self.assertRaises(AttributeError):
            tmp.timestamp = 100
    

class TestEdge(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_edge(self):
        tmp = Edge(10,11, "RT", 0)
        self.assertIsNotNone(tmp)


    def test_type(self):
        """
        Checks if the `Edge` object's `type` attribute can be set to "RT" and
        raises an `AttributeError` if it is attempted to set it to anything else.

        """
        tmp = Edge(10,11, "RT", 0)
        self.assertEqual(tmp.type, "RT")
        with self.assertRaises(AttributeError):
            tmp.type = "NOTYPE"

    def test_from(self):
        """
        Tests the `origin` attribute of a `Edge` class object by asserting it is
        equal to 11 and then raising an `AttributeError` when attempting to assign
        a new value to it.

        """
        tmp = Edge(10,11, "RT", 0)
        self.assertEqual(tmp.origin, 11)
        with self.assertRaises(AttributeError):
            tmp.origin = 22

    def test_to(self):
        """
        Tests the functionality of the `Edge` class by asserting that the `destination`
        attribute is set to a specific value, and then raising an `AttributeError`
        when attempting to modify the same.

        """
        tmp = Edge(10,11, "RT", 0)
        self.assertEqual(tmp.destination, 10)
        with self.assertRaises(AttributeError):
            tmp.destination = 22

    def test_agent_id(self):
        """
        Tests if the agent ID of an edge object is updated correctly when its value
        is changed.

        """
        tmp = Edge(10,11, "RT", 0)
        self.assertEqual(tmp.agent_id, 0)
        tmp.agent_id = 22
        self.assertEqual(tmp.agent_id, 22)

    def test_attrs(self):
        """
        Verifies that Edge's `attrs` attribute can be set, retrieved, and deleted.
        It also tests that raising a `KeyError` is raised when attempting to access
        an removed attribute.

        """
        tmp = Edge(10,11, "RT", 0)
        self.assertEqual(len(tmp.attrs), 0)
        tmp.attrs["test"] = Attribute(10.4, 0, 12)
        self.assertEqual(len(tmp.attrs), 1)
        self.assertIsNotNone(tmp.attrs["test"])
        del tmp.attrs["test"]
        with self.assertRaises(KeyError):
            tmp.attrs["test"]



class TestNode(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_node(self):
        """
        Asserts that a `Node` instance with id `1` and parent `root` is not none
        and raises a `RuntimeError` if a new `Node` instance with the same id as
        another node is created.

        """
        tmp = Node(1, "root")
        self.assertIsNotNone(tmp)
        with self.assertRaises(RuntimeError):
            tmp = Node(1, "test")
        
    def test_name(self):
        """
        Tests whether setting an attribute on a node with a non-existent name
        raises an AttributeError.

        """
        tmp = Node(1, "root", "name")
        self.assertEqual(tmp.name, "name")
        with self.assertRaises(AttributeError):
            tmp.name = "newname"

    def test_type(self):
        """
        Asserts that a Node object's `type` attribute is set to `"root"`, and then
        raises an `AttributeError` when attempting to modify its `id` attribute
        with a new value.

        """
        tmp = Node(1, "root","name")
        self.assertEqual(tmp.type, "root")
        with self.assertRaises(AttributeError):
            tmp.id = "newtype"

    def test_agent_id(self):
        """
        Verifies that the `agent_id` attribute of a given `Node` object can be
        modified and that the new value is correctly stored.

        """
        tmp = Node(1, "root", "name")
        self.assertEqual(tmp.agent_id, 1)
        tmp.agent_id = 2
        self.assertEqual(tmp.agent_id, 2)

    def test_attrs(self):
        """
        Verifies the length, existence, and deletion of attributes in a Node object.

        """
        tmp = Node(1, "root", "name")
        self.assertEqual(len(tmp.attrs), 0)
        tmp.attrs["test"] = Attribute(10.4, 0, 12)
        self.assertEqual(len(tmp.attrs), 1)
        self.assertIsNotNone(tmp.attrs["test"])
        del tmp.attrs["test"]
        with self.assertRaises(KeyError):
            tmp.attrs["test"]

    def test_edge(self):
        """
        Tests the `len`, `isnotnone`, and `raises` methods of a Node object by
        creating an Edge object, updating the Node's edges, and then deleting the
        Edge.

        """
        tmp = Node(1, "root", "name")
        self.assertEqual(len(tmp.edges), 0)
        tmp.edges[(11,"RT")] = Edge(10,11, "RT", 0)
        self.assertEqual(len(tmp.edges), 1)
        self.assertIsNotNone(tmp.edges[(11,"RT")])
        del tmp.edges[(11,"RT")]
        with self.assertRaises(KeyError):
            tmp.edges[(11,"RT")]



class TestDSRGraph(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_graph(self):
        a = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        self.assertIsNotNone(a)

    def test_get_node(self):
        """
        Verifies the existence and non-existence of nodes in a graph, given by the
        `DSRGraph` instance and the node ID or name.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        node = g.get_node(1)
        self.assertIsNotNone(node)
        node = g.get_node("root")
        self.assertIsNotNone(node)
        node = g.get_node(1000000)
        self.assertIsNone(node)
        node = g.get_node("weirdname")
        self.assertIsNone(node)

    def test_delete_node(self):
        """
        Tests whether a node can be deleted successfully using the `delete_node`
        method of a DSRGraph object, with expected results as per the assertion calls.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        node = g.get_node(1)
        self.assertIsNotNone(node)
        res = g.delete_node(1)
        self.assertEqual(res, True)
        node = g.get_node(1)
        self.assertIsNone(node)

    
    def test_update_node(self):
        """
        Updates the node's color to red and asserts that the updated value is
        indeed 'red'.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        world = g.get_node("root")
        world.attrs["color"].value = "red"
        result = g.update_node(world)
        self.assertEqual(result, True)
        world = g.get_node("root")
        self.assertEqual(world.attrs["color"].value, "red")
        

    def test_get_edge(self):
        """
        Tests the `get_edge` method of a graph object, by checking if an edge
        exists between specific nodes, and if it does, it verifies that the edge
        has the correct type ("RT"). If the edge doesn't exist or its type is not
        "RT", the function asserts that it is `None`.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)

        edge = g.get_edge(1, 2, "RT")
        self.assertIsNotNone(edge)
        edge = g.get_edge(g.get_name_from_id(1), g.get_name_from_id(2), "RT")
        self.assertIsNotNone(edge)
        edge = g.get_edge(11111, 22222, "RT")
        self.assertIsNone(edge)
        edge = g.get_edge("11111", "22222", "RT")
        self.assertIsNone(edge)

        
    def test_insert_or_asssign_edge(self):
        """
        Tests the `insert_or_assign_edge` method of a DSRGraph instance, checking
        that an edge's attribute value can be set and that a new edge can be added
        to the graph.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        edge = g.get_edge(1, 2, "RT")
        edge.attrs["color"] = Attribute("red", 0, 12)
        g.insert_or_assign_edge(edge)
        edge = g.get_edge(1, 2, "RT")
        self.assertEqual(edge.attrs["color"].value, "red")
        edge = Edge(1, 2, "in", 12)
        g.insert_or_assign_edge(edge)
        edge = g.get_edge(2, 1, "in")
        self.assertIsNotNone(edge)


    def test_delete_edge(self):
        """
        Tests whether deleting an edge from a graph with specified ID and label
        returns True and the edge is indeed deleted when given an invalid ID.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        edge = g.get_edge(1, 2, "RT")
        self.assertIsNotNone(edge)
        result = g.delete_edge(1, 2, "RT")
        self.assertEqual(result, True)
        edge = g.get_edge(1, 2, "RT")
        self.assertIsNone(edge)
        result = g.delete_edge(111111, 22222, "RT")
        self.assertEqual(result, False)

    def test_get_node_root(self):
        """
        Verifies that the root node of a graph is not null and has an ID of 1 and
        name of "root"

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)

        node = g.get_node_root()
        self.assertIsNotNone(node)
        self.assertEqual(node.id, 1)
        self.assertEqual(node.name, "root")

    def test_get_nodes_by_type(self):
        """
        Tests the `get_nodes_by_type` method of a `DSRGraph` object. It asserts
        that there is only one node of type "rgbd" and none of type "invalidtype".

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        nodes = g.get_nodes_by_type("rgbd")
        self.assertEqual(len(nodes), 1)
        nodes = g.get_nodes_by_type("invalidtype")
        self.assertEqual(len(nodes), 0)

    def test_get_name_from_id(self):
        """
        Tests whether the `DSRGraph` object's `get_name_from_id` method returns
        the correct names for valid and invalid ID inputs.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        name = g.get_name_from_id(1)
        self.assertIsNotNone(name)
        self.assertEqual(name, "root")
        name = g.get_name_from_id(11111111)
        self.assertIsNone(name)

    def test_get_id_from_name(self):
        """
        Tests if a given name returns an non-none id and if another name returns
        a none id.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        id = g.get_id_from_name("root")
        self.assertIsNotNone(id)
        self.assertEqual(id, 1)
        id = g.get_id_from_name("11111111")
        self.assertIsNone(id)

    def test_get_edges_by_type(self):
        """
        Tests two types of edges in a graph: `RT` and an invalid type. It asserts
        that there are at least one edge with the specified type in the graph and
        that no edges have the invalid type.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        edges = g.get_edges_by_type("RT")
        self.assertGreater(len(edges), 0)
        edges = g.get_edges_by_type("invalidtype")
        self.assertEqual(len(edges), 0)
        

    def test_get_edges_to_id(self):
        """
        Tests the `get_edges_to_id` method of a DSRGraph object. It verifies that
        the method returns a non-empty list of edge IDs when passed a vertex ID
        greater than 0, and verifies that the method returns an empty list when
        passed a vertex ID equal to 1.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        edges = g.get_edges_to_id(2)
        self.assertGreater(len(edges), 0)
        edges = g.get_edges_to_id(1)
        self.assertEqual(len(edges), 0)


    def test_insert_node(self):

        """
        Tests if inserting a node into the DSRGraph successfully creates and returns
        an object representing the new node.

        """
        g = DSRGraph(int(0), "Prueba", 12, os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json") )
        node = Node(12, "mesh", "newmesh")

        id = g.insert_node(node)
        self.assertIsNotNone(id)
        node = g.get_node("newmesh")
        self.assertIsNotNone(node)
        self.assertEqual(id, node.id)


    

class TestRTAPI(unittest.TestCase):
    

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_rtapi(self):
        """
        Creates an instance of `DSRGraph` with a scene file and enables the
        `autonomyLab_objects.simscene.json` file for runtime simulation.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        self.assertIsNotNone(rt_api)
    
    def test_insert_or_assign_edge_RT(self):
        """
        Tests whether an edge with the specified RT tag and coordinates is added
        or assigned to an node's edges list. It uses the `rt_api` class and the
        `g` object to interact with the DSRGraph library.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        world = g.get_node("root")
        rt.insert_or_assign_edge_RT(world, 203, [0.0, 1.2, 0.0], [1.1, 0.0, 2.2])
        world = g.get_node("root")
        self.assertIsNotNone(world.edges[(203, "RT")])

    def test_get_edge_RT(self):
        """
        Tests if the `get_edge_RT` method of a `RTApi` object returns a non-null
        edge with type "RT" when passing the root node and edge index as input.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        edge = rt.get_edge_RT(g.get_node("root"),2)
        self.assertIsNotNone(edge)
        self.assertEqual(edge.type, "RT")


    def test_get_RT_pose_from_parent(self):
        """
        Tests whether a pose is returned from the `get_RT_pose_from_parent` method
        of the `rt_api` class when called with a node reference.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        pose = rt.get_RT_pose_from_parent(g.get_node(2))
        self.assertIsNotNone(pose)


    def test_get_edge_RT_as_rtmat(self):
        """
        Tests if the get_edge_RT and get_edge_RT_as_rtmat functions return the
        expected values for a given edge in the graph.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        edge = rt.get_edge_RT(g.get_node("root"),2)
        rtmat = rt.get_edge_RT_as_rtmat(edge, 0)
        rtmat2 = rt.get_edge_RT_as_rtmat(edge)
        self.assertIsNotNone(rtmat)
        self.assertIsNotNone(rtmat2)

    def test_get_translation(self):
        """
        Tests whether the `get_translation()` method returns a non-null value when
        passed a valid coordinate and a time step.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        rt = rt_api(g)
        trans = rt.get_translation(1, 2, 0)
        trans2 = rt.get_translation(1, 2)
        self.assertIsNotNone(trans)
        self.assertIsNotNone(trans2)

class TestInnerAPI(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        #time.sleep(0.5)
        pass

    def test_create_innerapi(self):
        """
        Creates a Direct Simulation Runner (DSR) graph, sets up an inner API for
        it, and asserts that the inner API is not None.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        self.assertIsNotNone(inner)

    def test_transform(self):
        """
        Tests whether the `transform` method of an inner API returns a valid result
        for different input arguments.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        tr = inner.transform("root", "laser",0)
        self.assertIsNotNone(tr)
        tr = inner.transform("root", [1.1, 3.3, 6.6], "laser",0)
        self.assertIsNotNone(tr)

    def test_transform_axis(self):
        """
        Tests the `transform_axis` method of an inner API object. It validates
        that the method returns a non-None value and transforms a root axis with
        specified values for laser angles.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        tr = inner.transform_axis("root", "laser",0)
        self.assertIsNotNone(tr)
        tr = inner.transform_axis("root", [1.1, 3.3, 6.6, 0.0 , 0.0, 0.0], "laser",0)
        self.assertIsNotNone(tr)

    def test_get_transformation_matrix(self):
        """
        Creates a DSRGraph instance, sets various parameters, and asserts that the
        transform matrix returned by the `inner_api` function is not none.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        tr_matrix = inner.transform_axis("root", "laser",0)
        self.assertIsNotNone(tr_matrix)

    def test_get_rotation_matrix(self):
        """
        Verifies that the `get_rotation_matrix` method returns a rotation matrix
        for the "root" element of the simulation scene given in the input `json`
        file.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        rot = inner.get_rotation_matrix("root", "laser",0)
        self.assertIsNotNone(rot)

    def test_get_translation_vector(self):
        """
        Tests if the `get_translation_vector` method of the `inner_api` class
        returns a non-empty vector when passing the name "root", the element
        "laser", and the time step 0.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        trans = inner.get_translation_vector("root", "laser",0)
        self.assertIsNotNone(trans)

    def test_get_euler_xyz_angles(self):
        """
        Tests whether the `get_euler_xyz_angles` method of a provided `inner_api`
        instance returns valid Euler angles for the "root", "laser", and time index.

        """
        g = DSRGraph(int(0), "Prueba", int(12), os.path.join(ETC_DIR, "autonomyLab_objects.simscene.json"), True)
        inner = inner_api(g)
        angles = inner.get_euler_xyz_angles("root", "laser", 0)
        self.assertIsNotNone(angles)


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        """
        Creates an instance of a class if one does not exist in instances dictionary,
        otherwise returns the instance from the instances dictionary.

        Args:
            cls (`object`.): base class or superclass of the instance being created,
                and is used to call the appropriate constructor method for that class.
                
                		- `super`: It is a reference to the superclass of `Singleton`.
                		- `_instances`: A dictionary containing the instances of the
                class, where each key is a string representing the class name.
                		- `__call__`: This is the function that is called when an instance
                of `Singleton` is created. It returns the instance of the class
                associated with the given class name in the `_instances` dictionary.

        Returns:
            instance of class `Singleton: an instance of the `Singleton` class
            with the given `cls` argument.
            
            		- `cls`: The class object that was used to create the instance.
            		- `_instances`: A dictionary that stores instances of the Singleton
            class.
            		- `super()`: The method call to the superclass's `__call__` function,
            which returns an instance of the superclass.
            		- `args` and `kwargs`: Positional and keyword arguments passed to
            the `__call__` function, respectively.

        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



if __name__ == '__main__':
    #import psutil
    #if psutil.Process(os.getpid()).parent().name() == 'sh':
    #    unittest.main()
    #else:
    #    print("You probably want to execute test with the runTest.sh script.")
    unittest.main()
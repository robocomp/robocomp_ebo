Python wrapper for the DSR Graph
================================

Initialization
--------------

```python
# import the module
import pydsr

# constants
AGENT_ID = 42                    # unique among agents
DSR_NAME = "example_dsr_graph"   # target DSR graph name

# retrieve the graph and the RT-edge API objects
g      = pydsr.DSRGraph(0, DSR_NAME, AGENT_ID)
rt_api = pydsr.rt_api(g)
```

Methods
-------

# Attribute

_Attribute_(v, t: _int_, agent_id: _int_) → _Attribute_

_Attribute_(v, agent_id: _int_) → _Attribute_
:   Constructor.

_Attribute_.**agent_id**
:   TODO

_Attribute_.**timestamp**
:   TODO

_Attribute_.**value**
:   TODO

# Edge

_Edge_(to: _int_, from: _int_, type: _str_, agent_id: _int_) → _Edge_
:   Constructor.

_Edge_.**type**
:   TODO

_Edge_.**origin**
:   TODO

_Edge_.**destination**
:   TODO

_Edge_.**agent_id**
:   TODO

_Edge_.**attrs**
:   TODO

### DSRGraph

_DSRGraph_.**get_node**(id: _int_) → _Node_

_DSRGraph_.**get_node**(name: _str_) → _Node_
:	Return the node with the id or name passed as parameter. Returns None if the node does not exist.

_DSRGraph_.**delete_node**(id: _int_) → _bool_

_DSRGraph_.**delete_node**(name: _str_) → _bool_
:	Delete the node with the given id. Returns a bool with the result o the operation.

_DSRGraph_.**insert_node**(node: _Node_) → _int_
:	Insert in the graph the new node passed as parameter. Returns the id of the node or None if the Node alredy exist in the map.

_DSRGraph_.**update_node**(node: _Node_) → _bool_
:	Update the node in the graph. Returns a bool indicating whether the operation was successful.

_DSRGraph_.**get_edge**(from: _int_, to: _int_, type: _str_) → _Edge_

_DSRGraph_.**get_edge**(from: _str_, to: _str_, type: _str_) → _Edge_
:	Return the edge with the parameters from, to, and type passed as parameter. Returns None if the edge does not exist.

_DSRGraph_.**insert_or_assign_edge**(edge: _Edge_) → _bool_
:	Insert or updates and edge. Returns a bool indicating whether the operation was successful.

_DSRGraph_.**delete_edge**(from: _int_, to: _int_, type: _str_) → _bool_

_DSRGraph_.**delete_edge**(from: _str_, to: _str_, type: _str_) → _bool_
:	Return the edge with the parameters from, to, and type passed as parameter. Returns a bool indicating whether the operation was successful.

_DSRGraph_.**get_node_root**() → _Node_
:	Return the root node.

_DSRGraph_.**get_nodes_by_type**(type: _str_) → [_Node_]
:	Return all the nodes with a given type.

_DSRGraph_.**get_name_from_id**(id: _int_) → _str_
:	Return the name of a node given its id.

_DSRGraph_.**get_id_from_name**(name: _str_) → _int_
:	Return the id from a node given its name.

_DSRGraph_.**get_edges_by_type**(type: _str_) → [_Edge_]
:	Return all the edges with a given type.

_DSRGraph_.**get_edges_to_id**(id: _int_) → [_Edge_]
:	Return all the edges that point to a node.

_DSRGraph_.**write_to_json_file**(file, skip_attrs: [_str_]) → [_Edge_]
:	Dump the graph to a JSON file, skipping the attributes in skip_attrs.

# InnerEigenAPI

_InnerEigenAPI_.**transform**(orig: _str_, dest: _str_, timestamp: _int_) →

_InnerEigenAPI_.**transform**(orig: _str_, vector, dest: _str_, timestamp: _int_) →
: TODO

_InnerEigenAPI_.**transform**(orig: _str_, dest: _str_, timestamp: _int_) →

_InnerEigenAPI_.**transform**(orig: _str_, vector, dest: _str_, timestamp: _int_) →
: TODO

_InnerEigenAPI_.**get_transformation_matrix**(orig: _str_, dest: _str_, timestamp: _int_) →
: TODO

_InnerEigenAPI_.**get_rotation_matrix**(orig: _str_, dest: _str_, timestamp: _int_) →
: TODO

_InnerEigenAPI_.**get_translation_vector**(orig: _str_, dest: _str_, timestamp: _int_) →
: TODO

_InnerEigenAPI_.**get_euler_xyz_angles**(orig: _str_, dest: _str_, timestamp: _int_) →
: TODO

# Node

_Node_(agent_id: _int_, type: _str_, name: _str_) → _Node_
:   Constructor.

_Node_.**id**
:   TODO

_Node_.**name**
:   TODO

_Node_.**type**
:   TODO

_Node_.**agent_id**
:   TODO

_Node_.**attrs**
:   TODO

_Node_.**edges**
:   TODO

# RT_API

_RT\_API_.**insert_or_assign_edge_RT**(node: _Node_, to: _int_, translation: _[float]_, rotation_euler: _[float]_) →
: TODO

_RT\_API_.**get_edge_RT**(node: _Node_, to: _int_) →
: TODO

_RT\_API_.**get_RT_pose_from_parent**(node: _Node_) →
: TODO

_RT\_API_.**get_edge_RT_as_rtmat**(edge: _Edge_, t: _int_) →
: TODO

_RT\_API_.**get_translation**(id: _int_, to: _int_, timestamp: _int_) →
: TODO

Signals
-------

When the DSR graph is altered, a signal is fired. Handler functions can be _connected_ to these signals so they are called when they are fired. The following signals are exposed through this API:

_signals_.**UPDATE_NODE**
:	**Handler signature:** _int_, _str_ → None

_signals_.**UPDATE_NODE_ATTR**
:	**Handler signature:** _int_, [_str_] → None

_signals_.**UPDATE_EDGE**
:	**Handler signature:** _int_, _int_, _str_ → None

_signals_.**UPDATE_EDGE_ATTR**
:	**Handler signature:** _int_, _int_, [_str_] → None

_signals_.**DELETE_EDGE**
:	**Handler signature:** _int_, _int_, _str_ → None
:	An edge has been deleted.

_signals_.**DELETE_NODE**
:	**Handler signature:** [_int_] → None
:	A node has been deleted.
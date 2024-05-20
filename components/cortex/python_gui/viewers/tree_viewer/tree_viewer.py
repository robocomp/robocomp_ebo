from PySide2.QtCore import Signal
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeViewer(QTreeWidget):
    node_check_state_changed_signal = Signal(int, int, str, QTreeWidgetItem)

    def __init__(self, G):
        """
        Initializes an instance of `TreeViewer`, setting up its internal maps for
        storing tree data and attributes, as well as connecting to a global `G` object.

        Args:
            G (instance/objects of class `G`.): 2D graph layout for the tree viewer.
                
                		- `G`: A serialized Python object, possibly containing attributes
                or objects of various types (e.g., ints, strs, lists, dicts). The
                class `TreeViewer` expects this as its initial value, to be
                deserialized into instance variables.

        """
        super(TreeViewer, self).__init__()
        self.G = G
        self.types_map = {}
        self.tree_map = {}
        self.attributes_map = {}

    def getGraph(self):
        return self.G

    # SLOTS
    def add_or_assign_node_slot(self, node_id, node_type, name=""):
        pass

    def add_or_assign_node_slot(self, node_id, node):
        pass

    def add_or_assign_edge_slot(self, from_node, to_node, node_type):
        pass

    def del_edge_slot(self, from_node, to_node, edge_tag):
        pass

    def del_node_slot(self, node_id):
        pass

    def node_change_slot(self, value, node_id, node_type, parent=None):
        pass

    def category_change_slot(self, value, parent=None):
        pass

    def reload(self, widget):
        pass

    # PRIVATE
    def createGraph(self, ):
        pass

    def create_attribute_widgets(self, parent, node):
        pass

    def create_attribute_widget(self, parent, node, key, value):
        pass

    def update_attribute_widgets(self, node):
        pass

import sys

from PySide2.QtCore import QObject, QTimer, QElapsedTimer, Signal, QSettings, QLineF, QPointF
from PySide2.QtGui import Qt, QBrush, QPainter, QRadialGradient, QGradient, QColor, QPen, QPalette, QTransform
from PySide2.QtWidgets import QWidget, QMenu, QMainWindow, QApplication, QAction, QDockWidget, \
    QFileDialog, QPushButton, QHBoxLayout, QLabel, QSlider, QGraphicsScene, \
    QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsView, QGraphicsSimpleTextItem, QStyle, QToolBar, QLabel, \
    QScrollArea, QVBoxLayout, QSizePolicy, QFrame, QTableWidget, QTableWidgetItem, QGraphicsItem

from GHistoryState import GHistoryState, get_file
from pydsr import Node, Edge, Attribute

import difflib


NODE_COLORS = {
    "root": "red",
    "transform" : "SteelBlue",
    "room" : "Gray",
    "differentialrobot" : "GoldenRod",
    "omnirobot" : "Gray",
    "robot" : "Gray",
    "path_to_target" : "Gray",
    "intention" : "Gray",
    "rgbd" : "Gray",
    "pan_tilt" : "Gray",
    "battery" : "Gray",
    "pose" : "Gray",
    "laser" : "GreenYellow",
    "camera" : "Gray",
    "imu" : "LightSalmon",
    "slam_device" : "Gray",
    "object" : "Gray",
    "affordance_space" : "Gray",
    "person" : "Gray",
    "personal_space" : "Gray",
    "plane" : "Khaki",
    "box" : "Gray",
    "cylinder" : "Gray",
    "ball" : "Gray",
    "mesh" : "LightBlue",
    "face" : "Gray",
    "body" : "Gray",
    "chest" : "Gray",
    "nose" : "Gray",
    "left_eye" : "Gray",
    "right_eye" : "Gray",
    "left_ear" : "Gray",
    "right_ear" : "Gray",
    "left_arm" : "Gray",
    "right_arm" : "Gray",
    "left_shoulder" : "Gray",
    "right_shoulder" : "Gray",
    "left_elbow" : "Gray",
    "right_elbow" : "Gray",
    "left_wrist" : "Gray",
    "right_wrist" : "Gray",
    "left_hand" : "Gray",
    "right_hand" : "Gray",
    "left_hip" : "Gray",
    "right_hip" : "Gray",
    "left_leg" : "Gray",
    "right_leg" : "Gray",
    "left_knee" : "Gray",
    "right_knee" : "Gray",
    "mug" : "Gray",
    "cup" : "Gray",
    "noodles" : "Gray",
    "table" : "Gray",
    "chair" : "Gray",
    "shelve" : "Gray",
    "dish" : "Gray",
    "spoon" : "Gray",
    "testtype" : "Gray",
    "glass" : "Gray",
    "plant" : "Gray",
    "microwave" : "Gray",
    "oven" : "Gray",
    "vase" : "Gray",
    "refrigerator" : "Gray",
    "road" : "Gray",
    "building" : "Gray",
    "vehicle" : "Gray",
    "gps" : "Gray",
    "grid" : "Gray",
    "agent" : "Gray"
}


class GraphNodeWidget(QTableWidget):

    def __init__(self, node_or_edge):
        """
        Sets up the UI components of a `QTableWidget`. It takes in a node or edge
        object and creates a window title based on the node or edge's attributes.
        The function then loops through the attributes and inserts them into the
        widget. Finally, it resizes the widget and displays it.

        Args:
            node_or_edge (`Node` or `Edge`.): 2D geometry object that will be
                displayed in the table widget, which can be either a node or an edge.
                
                		- `node_or_edge` can be an instance of `Node` or `Edge`.
                		- `Objs.id`, `Objs.type`, and `Objs.name` are properties of the
                input object, which are used to construct the widget's name.
                		- `atts` is a dictionary containing key-value pairs of attribute
                names and values associated with the input object. These attributes
                are inserted into the widget using the `__insert_att()` method.

        """
        QTableWidget.__init(self)

        if isinstance(node_or_edge, Node):
            self.name = f"Node: {Obj.id}, {Obj.type}, {Obj.name}"
        else:
            self.name = f"Edge: {Obj.origin}, {Obj.destination}, {Obj.type}"

        self.setWindowTitle(f"{self.name} ")

        for k, v in node_or_edge.atts.items():
            self.__insert_att(k, v)

        self.horizontalHeader().setStretchLastSection(True)
        self.resize_widget()

        self.show()
    def __insert_att(self, key, value):
        """
        Inserts a new row into an array table widget and sets a text item in that
        row based on the provided value, truncating it if necessary to prevent
        excessive length.

        Args:
            key (str): 400 character limit for the value of a table widget item.
            value (float): data that will be displayed as text inside each row in
                the table, which is then formatted and placed within an item in
                the table.

        """
        rc = self.rowCount()
        self.insertRow(rc)
        val_str = str(value.value)
        if len(val_str) > 400:
            val_str= val_str[:400] + " ... "
        item = QTableWidgetItem(val_str)
        item.setFlags(Qt.ItemIsSelectable| Qt.ItemIsEnabled)
        self.setItem(rc, 0, item)

class GraphNode(QObject, QGraphicsEllipseItem):

    def __init__(self, node):
        """
        Sets up a `QGraphicsEllipseItem`, which includes setting its initial
        position, node brush, and various flags for interacting with the item and
        its geometry changes.

        Args:
            node (`QNode` object.): 2D shape that the `QGraphicsEllipseItem` will
                be initialized to, with its position set to (0, 0) and dimensions
                set to 20 by 20 pixels.
                
                		- `node_brush`: This is a QBrush object that represents the brush
                used to paint the node. It has a solid pattern style.
                		- `node`: This is a reference to a node object that represents
                the graphical element being initialized.
                		- `setAcceptHoverEvents(True)`: This sets the item's acceptance
                of hover events to true, which means that the item will receive
                hover events and can respond to them.
                		- `setZValue(-1)`: This sets the item's z-value to -1, which
                makes the item hidden behind its parent items in the scene.
                		- `setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)`:
                This sets the item's cache mode to device coordinate cache, which
                means that the item will use device coordinates to store its cache
                instead of screen coordinates.
                		- `setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | ...)`: This sets
                various flags for the item, indicating whether it is movable,
                selectable, etc. The most significant flags set are `ItemIsMovable`
                and `ItemIsSelectable`, which enable the user to move and select
                the item.
                
                	The `node` property refers to a node object that contains information
                about the graphical element being initialized. It may have various
                properties or attributes, such as position, size, rotation, and
                other graphical attributes that can be accessed and modified through
                methods such as `position`, `size`, `rotation`, etc.

        """
        QObject.__init__(self)
        QGraphicsEllipseItem.__init__(self, 0, 0, 20, 20)
        self.node_brush = QBrush()
        self.node = node
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)
        #self.node_brush.setStyle(Qt.SolidPattern)
        #self.node_brush.setStyle(Qt.SolidPattern)
        #self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | \
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges | \
                      QGraphicsItem.GraphicsItemFlag.ItemUsesExtendedStyleOption | \
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

    def setTag(self, tag):
        """
        Sets the text item's tag to a given value and positions it at the specified
        x-coordinate and y-coordinate relative to its parent item.

        Args:
            tag (`QGraphicsSimpleTextItem`.): 2D graphics item to which the
                `QGraphicsSimpleTextItem` will be added.
                
                		- `tag`: This is the input provided as a string, which has been
                serialized from some other representation.
                		- `self`: This is a reference to the `QGraphicsSimpleTextItem`
                instance that the function is called on.
                		- `setX` and `setY`: These are methods that set the x-coordinate
                and y-coordinate of the text item, respectively.

        """
        self.tag = QGraphicsSimpleTextItem(tag, self)
        self.tag.setX(20)
        self.tag.setY(-10)

    def __setColor(self, color):
        self.node_brush.setColor(color)
        self.setBrush(self.node_brush)

    def setType(self, type):
        #TODO: Add click to show tables.
        """
        Sets a type-dependent color for the current node, using a default value
        of "coral" if no color is found in the `NODE_COLORS` dictionary for the
        given type.

        Args:
            type (str): type of node for which the color is being set, with possible
                values being `Node.Kernel`, `Node.Device`, or `Node.Network`.

        """
        color = NODE_COLORS[type] if NODE_COLORS.get(type) else "coral"
        self.__setColor(color)
        pass

    def mouseDoubleClickEvent(self, event):
        """
        Is called when the mouse double-clicks on an item in the graphics scene.
        The function prints "double click" and, if the right button was clicked,
        creates a new node widget and adds it to the scene.

        Args:
            event (`QMouseEvent`.): mouse event that triggered the function,
                providing information on the button clicked and the position of
                the mouse cursor at the time of the event.
                
                		- `button`: The type of mouse button that triggered the event,
                with values ranging from 0 to 3 (Qt documentation). In this case,
                it is `Qt.RightButton`, indicating a right-click event.

        """
        super().hoverEnterEvent(event)
        print("doble click")
        if event.button() == Qt.RightButton:
            self.node_widget = GraphNodeWidget(self.node)

        QGraphicsEllipseItem.mouseDoubleClickEvent(event)

    def paint(self, painter, option, widget):
        """
        Sets a pen and brush for drawing an ellipse, depending on the node's state.

        Args:
            painter (int): QPainter object that is used to draw the node's graphical
                representation.
            option (int): 3-bit flag indicating the state of the node being painted,
                with possible values of QStyle.State_Sunken or 0 for non-sunken
                nodes, which affects the color of the gradient used to fill the ellipse.
            widget (`Object`.): widget that is being painted and is used to determine
                the brush color and pen style for the paint operation.
                
                		- `setPen`: Sets the pen used for drawing to `Qt.NoPen`.
                		- `setBrush`: Sets the brush used for filling to `self.node_brush`.
                		- `gradient`: Creates a radial gradient with an radius of -3 and
                center at (-3, -3) with two colors: light gray (color(Qt.darkGray).light(200))
                and dark gray (self.node_brush.color()).
                		- `isSelected`: Indicates whether the widget is selected or not.
                
                	In conclusion, the `paint` function describes the properties of
                the input `widget` in the context of drawing an ellipse.

        """
        painter.setPen(Qt.NoPen)
        #painter.setBrush(self.node_brush)

        gradient = QRadialGradient(-3, -3, 20)
        #if option.state &  QStyle.State_Sunken:
        #    gradient.setColorAt(0, QColor(Qt.darkGray).light(200))
        #    gradient.setColorAt(1, QColor(Qt.darkGray))
        #else:

        gradient.setColorAt(0, self.node_brush.color())
        gradient.setColorAt(1, QColor(self.node_brush.color()).light(200))

        painter.setBrush(gradient)
        if self.isSelected():
            painter.setPen(QPen(Qt.green, 0, Qt.DashLine))
        else:
            painter.setPen(QPen(Qt.black, 0))

        painter.drawEllipse(-10, -10, 20, 20)

class GraphEdge(QObject, QGraphicsLineItem):

    def __init__(self, orig, dst, type):
        """
        Initializes a `QGraphicsLineItem` object by setting its color, line width,
        original and destination points, and tag type.

        Args:
            orig (`Object` type.): 2D point where the line will start.
                
                		- `color`: A string attribute indicating the line's color. It
                is assigned the value "black".
                		- `line_width`: An integer attribute representing the line width.
                It is assigned the value 2.
                		- `orig`: A reference to an instance of the `QGraphicsScene`
                class, which represents the origin of the line. Its properties and
                attributes are not explained in this response.
            dst (`Object`.): 2D point where the line should be drawn, and it is
                used to calculate the correct position of the line based on its properties.
                
                		- `dest`: The `QPointD` destination point for the line.
            type (str): 2D shape type of the line, and it is used to set the
                appropriate tag for the line item based on the given value.

        """
        QObject.__init__(self)
        QGraphicsLineItem.__init__(self)
        self.color = "black"
        self.line_width = 2
        self.orig = orig
        self.dst = dst
        self.__setTag(type)
        self.__adjust()

    def __adjust(self):
        """
        Alters the geometry of a line object `line` to move its starting point
        closer to its end point by an equal distance on both sides, constrained
        by the line's length.

        """
        line  = QLineF(self.mapFromItem(self.orig, 0, 0), self.mapFromItem(self.dst, 0, 0))
        len = line.length()

        self.prepareGeometryChange()
        self.tag.setPos(line.center())
        if len > 20.0:
            edgeOffset = QPointF((line.dx() * 10) / len, (line.dy() * 10) / len)
            sourcePoint = QPointF(line.p1() + edgeOffset)
            destPoint = QPointF(line.p2() - edgeOffset)
            self.setLine(QLineF(sourcePoint, destPoint))
        else:
            self.setLine(line)

    def __setTag(self, tag):
        self.tag = QGraphicsSimpleTextItem(tag, self)


class Graph(QGraphicsView):

    def __init__(self):
        """
        Sets up a `Graph` class instance by initializing member variables and
        methods for graphics scene management, caching, viewport updating, and
        mouse tracking.

        """
        super(Graph, self).__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.nodes = {}
        self.edges = {}
        self.visual_nodes = {}
        self.visual_edges = {}
        central_point = QGraphicsEllipseItem(0,0,0,0)
        self.scene.addItem(central_point)
        self.setScene(self.scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)


    def mousePressEvent(self, event):
        """
        Detects and handles mouse clicks within a graphical user interface (GUI).
        When an item is located at the clicked position, the event is passed to
        the corresponding graphics view component for further processing.

        Args:
            event (`QMouseEvent`.): 2D mouse event received by the widget, providing
                information about the position of the mouse cursor at that moment.
                
                		- `pos()`: Returns the position of the event in screen coordinates,
                as a QPoint.
                		- `transform()`: Returns the transformation matrix for the item's
                position in scene coordinates.
                		- `itemAt(QPoint pos)`: Gets the item at the specified position
                in the scene. If the item is not found, returns null.

        """
        item = self.scene.itemAt(self.mapToScene(event.pos()), QTransform())
        if item:
            QGraphicsView.mousePressEvent(event)
        #else:
        #    AbstractGraphicViewer.mousePressEvent(event)

    def __add_or_replace_node(self, Node):

        """
        Adds or replaces a node in a graph based on its ID, by creating or retrieving
        a visual representation of the node from the scene, and linking it to the
        corresponding node object in the nodes dictionary.

        Args:
            Node (`GraphNode` instance.): 3D graph node that is being added or
                updated in the scene.
                
                		- `id`: A unique identifier for the node, which is also used as
                the key in the `nodes` dictionary.
                		- `name`: The name of the node.
                		- `type`: The type of the node (e.g., "group", "node", etc.).
                		- `attrs`: A dictionary containing various attributes of the
                node, such as its position (`pos_x` and `pos_y`)).
                
                	In the function, the following is performed:
                
                	1/ If no existing node with the same ID exists in the `nodes`
                dictionary, a new `GraphNode` instance is created with the given
                `id`, `name`, and `type`. The new instance is added to the
                `self.nodes` dictionary and the `visual_nodes` dictionary using
                the corresponding IDs.
                	2/ If an existing node with the same ID exists in the `nodes`
                dictionary, the existing node's properties are retrieved from the
                dictionary and used to set the node's position (`setPos`).
                
                	In summary, the function handles creation of new nodes and updating
                of existing nodes in the graph based on their IDs.

        """
        gnode = None
        if not self.nodes.get(Node.id):
            gnode = GraphNode(Node)
            gnode.id_in_graph = Node.id
            gnode.setTag(Node.name)
            gnode.setType(Node.type)

            self.nodes[Node.id] = Node
            self.visual_nodes[Node.id] = gnode
            self.scene.addItem(gnode)
            #print("New node", Node.name, Node.id)
        else:
            gnode = self.visual_nodes[Node.id]
            gnode.node = Node
            self.nodes[Node.id] = Node
            #print("Existing node", Node.name, Node.id)

        gnode.setPos(Node.attrs["pos_x"].value, Node.attrs["pos_y"].value)


    def __add_or_replace_edge(self, Edge):

        """
        Updates the graph edges based on the given key and edge data, either adding
        a new edge or replacing an existing one in the scene.

        Args:
            Edge (`GraphEdge`.): 3-tuple of origin, destination, and type for a
                graph edge.
                
                		- `origin`: The id of the origin node.
                		- `destination`: The id of the destination node.
                		- `type`: The type of edge (either `straight` or `curved`).

        """
        gedge = None
        key = (Edge.origin, Edge.destination, Edge.type)
        if not self.visual_nodes.get(Edge.origin) or not self.visual_nodes.get(Edge.destination):
            return

        if not self.edges.get(key):
            gedge = GraphEdge(self.visual_nodes[Edge.origin], self.visual_nodes[Edge.destination], Edge.type)

            self.edges[key] = Edge
            self.visual_edges[key] = gedge
            self.scene.addItem(gedge)
        else:
            gedge = self.visual_edges[key]
            self.edges[key] = Edge

    def set_state(self, nodes, edges):
        #TODO det diff in keys to remove nodes.
        """
        Removes nodes and edges from a scene based on their IDs, updates the scene
        with new nodes and edges, and adds or replaces them in the graph structure
        as needed.

        Args:
            nodes (list): 2D scene's nodes, which are used to store and manipulate
                information about each node in the scene.
            edges (list): 2-element tuples of edge IDs that need to be removed
                from the scene, along with their corresponding visual edges in the
                `visual_edges` dictionary.

        """
        old_node_keys = set(self.nodes.keys())
        ns = set([n[1].id for n in nodes if n[1]])
        node_keys_to_remove = [n for n in old_node_keys if n not in ns]

        old_edge_keys = set(self.edges.keys())
        es = set([(Edge[1].origin, Edge[1].destination, Edge[1].type) for Edge in edges if Edge[1]])
        edge_keys_to_remove = [e for e in old_edge_keys if e not in es]



        for id in node_keys_to_remove:
            del self.nodes[id]
            self.scene.removeItem(self.visual_nodes[id])
            del self.visual_nodes[id]

        for e_key in edge_keys_to_remove:
            del self.edges[e_key]
            self.scene.removeItem(self.visual_edges[e_key])
            del self.visual_edges[e_key]

        for n in nodes:
            if n[1] is not None:
                self.__add_or_replace_node(n[1])


        for e in edges:
            if e[1] is not None:
                self.__add_or_replace_edge(e[1])


class DSRHistoryViewer(QObject):

    def __init__(self, window,):
        """
        Sets up the necessary widgets and menu structures for the `GamePanel`
        class, including setting its timer, elapsed time display, game state (
        Gh), and connection to the window and docking widgets.

        Args:
            window (`QWindow` object.): 2D rectangular area of the primary application
                window within which the widgets are positioned and sized.
                
                		- `self.timer`: A `QTimer` object, used for timing-related tasks.
                		- `self.alive_timer`: An instance of `QElapsed Timer`, used to
                measure elapsed time.
                		- `self.gh`: A reference to the global hash table, which stores
                various game-related data structures.
                		- `self.slider`: A reference to a slider widget, which allows
                the player to adjust certain settings.
                		- `self.window`: The main window of the application, used for
                displaying game content and providing user input.
                		- `self.view_menu`: A `QMenu` object, used to display various
                game views.
                		- `self.file_menu`: A `QMenu` object, used to provide file-related
                options.
                		- `self.forces_menu`: A `QMenu` object, used to display
                forces-related options.
                		- `self.main_widget`: The main widget of the application, which
                contains the game logic and user interface elements.
                		- `self.docks`: A dictionary that maps widgets to their corresponding
                docking locations.
                		- `self.widgets`: A dictionary that maps widgets to their
                respective attributes and properties.
                		- `self.widgets_by_type`: A dictionary that maps widget types
                to their corresponding attribute values.

        """
        super().__init__()
        self.timer = QTimer()
        self.alive_timer = QElapsedTimer()
        self.gh = None
        self.slider = None
        self.window = window
        self.view_menu = QMenu()
        self.file_menu = QMenu()
        self.forces_menu = QMenu()
        self.main_widget = window
        self.docks = {}
        self.widgets = {}
        self.widgets_by_type = {}

        available_geometry = QApplication.desktop().availableGeometry()
        window.move((available_geometry.width() - window.width()) / 2,
                    (available_geometry.height() - window.height()) / 2)
        self.__initialize_file_menu()


    def __del__(self):
        """
        Sets the values of the `size` and `pos` settings groups under the `MainWindow`
        subgroup in the RoboComp DSR settings with the current window size and position.

        """
        settings = QSettings("RoboComp", "DSR")
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.window.size())
        settings.setValue("pos", self.window.pos())
        settings.endGroup()


    def __initialize_file_menu(self):
        """
        Creates a file menu on the GUI's main menu bar and adds an action labeled
        "Load" to the menu. When the Load action is triggered, it calls the
        `__load_file()` method.

        """
        file_menu = self.window.menuBar().addMenu(self.window.tr("&File"))
        load_action = QAction("Load", self)
        file_menu.addAction(load_action)
        # load_action
        load_action.triggered.connect(lambda: self.__load_file())


    def __load_file(self):
        """
        Takes an open file dialogue and loads the content of the file into a graph
        state object, creating widgets and connections to display the graph.

        """
        file_name = QFileDialog.getOpenFileName(None, 'Select file')
        print("------------------\n", str(file_name))
        val = get_file(file_name[0])
        self.gh = GHistoryState(val)
        self.__set_state(0)
        self.__create_slider()
        self.__load_main_widget()
        nodes, edges = self.gh.get_state(0)
        self.graphview.set_state(nodes, edges)
        self.slider.valueChanged.connect(self.__change_slider_value)
        self.__create_right_dock()

        print("File loaded")

    def __set_state(self, idx : int):
        pass

    def __change_slider_value(self):
        """
        Updates labels and adds new nodes or edges to a graph view based on changes
        in a slider's value, using `difflib.unified_diff()` for displaying differences
        between the old and new values.

        """
        val = self.slider.value()
        self.label.setText(str(val))
        nodes, edges = self.gh.get_state(val)
        self.graphview.set_state(nodes, edges)

        (old, new) = self.gh.get_change_state(self.slider.value())

        if hasattr(self, "difflines"):
            for idx, i in enumerate(self.difflines):
                self.container_widget.layout().removeWidget(i)
                i.deleteLater()
            self.difflines = []

        def set_labels(self, Obj):
            """
            Sets the text of a toolbar based on the type of object passed as an
            argument, either a Node or Edge.

            Args:
                Obj (`Node` or an `Edge`.): object for which changes will be
                    displayed in the toolbar.
                    
                    		- If `isinstance(Obj, Node)`, then `Objs` ID, type, and name
                    are displayed in the toolbar2 change label.
                    		- If `isinstance(Obj, Edge)`, then `Objs` origin and destination
                    nodes, as well as its type, are displayed in the toolbar2
                    change label.

            """
            if isinstance(Obj, Node):
                self.toolbar2_change.setText(f"Change Node: {Obj.id}, {Obj.type}, {Obj.name}")
            elif isinstance(Obj, Edge):
                self.toolbar2_change.setText(f"Change Edge: {Obj.origin}, {Obj.destination}, {Obj.type}")
            else:
                self.newLabel.setText("Change")

            #print(self.toolbar2_change.text())


        if not old and new:
            set_labels(self, new)
            self.oldLabel.setStyleSheet("QLabel { background-color : red;}")
            self.newLabel.setStyleSheet("QLabel { background-color : green; }")
            self.oldLabel.setText("")
            self.newLabel.setText(str(new))
        elif old and not new:
            set_labels(self, old)
            self.oldLabel.setStyleSheet("QLabel { background-color : red;}")
            self.newLabel.setStyleSheet("QLabel { background-color : green;}")
            self.oldLabel.setText(str(old))
            self.newLabel.setText("")
        elif old and new:
            diff = difflib.unified_diff(str(old).split("\n"), str(new).split("\n"), lineterm='', n=-1)

            if not hasattr(self, "difflines"):
                self.difflines = []

            diff = list(diff)
            #print('\n'.join(diff), end="")

            self.oldLabel.setStyleSheet("QLabel {background-color : red;}")
            self.newLabel.setStyleSheet("QLabel {background-color : green;}")
            self.oldLabel.setText("")
            self.newLabel.setText("")

            for l in diff[3:]:
                pl = QLabel(l)
                pl.setWordWrap(True)
                pl.setMinimumWidth(0)
                pl.setMaximumWidth(420)

                if l.startswith("+"):
                    pl.setStyleSheet("QLabel {  background-color : green; }")
                elif l.startswith("-"):
                    pl.setStyleSheet("QLabel {  background-color : red; }")
                elif l.startswith("@"):
                    continue
                self.container_widget.layout().addWidget(pl)
                self.difflines.append(pl)

            set_labels(self, new)

            #self.oldLabel.setText(str(old))
            #self.newLabel.setText(str(new))

        else:
            self.oldLabel.setStyleSheet("QLabel { background-color : red;}")
            self.newLabel.setStyleSheet("QLabel { background-color : blue;}")
            self.oldLabel.setText("")
            self.newLabel.setText("")



    def __create_slider(self):
        """
        Creates a toolbar containing a horizontal slider and a label displaying
        its current value, setting the minimum and maximum values based on the
        number of states in the `gh` object.

        """
        self.toolbar = self.window.addToolBar('ToolBar')
        self.toolbar.setMinimumHeight(75)
        self.toolbar.setMovable( False )
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.gh.states - 1)
        self.label = QLabel("0")

        self.toolbar.addWidget(self.slider)
        self.toolbar.addWidget(self.label)

    def __create_right_dock(self):

        """
        Creates a `QDockWidget` object named 'change_d', sets its allowed areas
        to `Qt.AllDockWidgetAreas`, minimum width to `450`, and adds a `QLabel`
        object to the dock widget's container. It also adds a `QLabel` object for
        the "Change" toolbar button.

        """
        self.change_d = QDockWidget()
        self.change_d.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.change_d.setMinimumWidth(450)

        self.sa = QScrollArea()
        self.sa.setBackgroundRole(QPalette.Window)
        self.sa.setFrameShadow(QFrame.Plain)
        self.sa.setFrameShape(QFrame.NoFrame)
        self.sa.setWidgetResizable(True)

        self.container_widget = QWidget(self.sa)
        self.container_widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.container_widget.setLayout(QVBoxLayout(self.container_widget))
        self.sa.setWidget(self.container_widget)
        self.container_widget.layout().setAlignment(Qt.AlignTop)

        self.oldLabel = QLabel("")
        self.newLabel = QLabel("")
        self.oldLabel.setStyleSheet("QLabel { background-color : red; }")
        self.newLabel.setStyleSheet("QLabel { background-color : green; }")
        self.newLabel.setWordWrap(True)
        self.oldLabel.setWordWrap(True)

        self.toolbar2_change = QLabel("Change")

        self.toolbar2_change.setWordWrap(True)
        self.toolbar2_change.setMaximumWidth(420)
        self.oldLabel.setMaximumWidth(420)
        self.newLabel.setMaximumWidth(420)

        self.container_widget.layout().addWidget(self.toolbar2_change)
        self.container_widget.layout().addWidget(self.oldLabel)
        self.container_widget.layout().addWidget(self.newLabel)
        #self.toolbar2.addWidget(self.sa)
        #self.window.addToolBar(Qt.RightToolBarArea, self.toolbar2)

        self.change_d.setWidget(self.sa)
        self.window.addDockWidget(Qt.RightDockWidgetArea, self.change_d)

    def __load_main_widget(self):
        """
        Creates a dock widget to hold the `Graph` widget and adds it to the main
        window.

        """
        self.graphview_d = QDockWidget()
        self.graphview_d.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.graphview = Graph()
        self.graphview_d.setWidget(self.graphview)
        self.window.addDockWidget(Qt.LeftDockWidgetArea, self.graphview_d)
        #self.window.setCentralWidget(self.graphview)

if __name__ == '__main__':
    #sys.path.append('/opt/robocomp/lib')
    app = QApplication(sys.argv)
    from pydsr import *

    main_window = QMainWindow()
    main_window.resize(1280, 720)
    ui = DSRHistoryViewer(main_window)
    main_window.show()
    app.exec_()


from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PySide2.QtGui import QColor, QPen, QBrush

from viewers._abstract_graphic_view import AbstractGraphicViewer

# constants
ROBOT_LENGTH = 400


class QScene2dViewer(AbstractGraphicViewer):
    drawaxis = False
    axis_center = None
    axis_x = None
    axis_y = None
    G = None

    def __init__(self, G):
        """
        Sets up a `QGraphicsRectItem` representing an axis with a pen and brush,
        sets its z-value, and sets the `setDrawAxis` method to `True`.

        Args:
            G (`object`.): 2D graphics context, which is used to draw the axis and
                other graphical elements in the function.
                
                		- `G`: This is an instance of the `QGraphicsScene` class, which
                is used to represent a two-dimensional scene in a graphical user
                interface (GUI). It has various properties and attributes, such
                as `sceneRect`, `scale`, `axis_center`, `axis_x`, `axis_y`, and `set_draw_axis`.
                		- `sceneRect`: This is the bounding rectangle of the `QGraphicsScene`
                instance, which represents the visible area of the scene.
                		- `scale`: This is a property that sets the scale factor for the
                scene, which can be used to resize the scene.
                		- `axis_center`: This is a `QGraphicsRectItem` instance that
                represents the center of the axes in the scene. It has a pen and
                brush, which are used to draw the axes.
                		- `axis_x` and `axis_y`: These are two `QGraphicsRectItem`
                instances that represent the horizontal and vertical axes in the
                scene, respectively. They also have pens and brushes used for drawing.
                		- `set_draw_axis`: This is a boolean property that indicates
                whether the axes should be drawn or not. When set to `True`, the
                axes are drawn; when set to `False`, they are not.
                		- `draw_axis`: This is a method that draws the axes in the scene
                based on their properties and attributes.

        """
        super().__init__()
        self.G = G
#        self.setMinimunSize(400, 400)
        self.scale(1, -1)
        # AXIS
        self.axis_center = QGraphicsRectItem(-100, -100, 200, 200)
        self.axis_center.setPen(QPen(QColor("black")))
        self.axis_center.setBrush(QBrush(QColor("black")))
        self.axis_center.setZValue(5000)
        self.axis_x = QGraphicsRectItem(0, 0, 1000, 30)
        self.axis_x.setPen(QPen(QColor("red")))
        self.axis_x.setBrush(QBrush(QColor("red")))
        self.axis_x.setZValue(5000)
        self.axis_y = QGraphicsRectItem(0, 0, 30, 1000)
        self.axis_y.setPen(QPen(QColor("blue")))
        self.axis_y.setBrush(QBrush(QColor("blue")))
        self.axis_y.setZValue(5000)


        self.set_draw_axis(True)
        self.draw_axis()



    def create_graph(self):
        pass

    def set_draw_axis(self, visible):
        self.drawaxis = visible

    def draw_axis(self):
        """
        Adds or removes axis-related items from the scene, depending on the value
        of `self.drawaxis`.

        """
        if self.drawaxis:
            self.scene.addItem(self.axis_center)
            self.scene.addItem(self.axis_x)
            self.scene.addItem(self.axis_y)
        else:
            self.scene.removeItem(self.axis_center)
            self.scene.removeItem(self.axis_x)
            self.scene.removeItem(self.axis_y)



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

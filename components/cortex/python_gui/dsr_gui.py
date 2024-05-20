import sys

from PySide2.QtCore import QObject, QTimer, QElapsedTimer, Signal, QSettings
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QMenu, QMainWindow, QApplication, QAction, QDockWidget, QFileDialog, QPushButton

from viewers.qscene_2d_viewer.qscene_2d_viewer import QScene2dViewer
from viewers.tree_viewer.tree_viewer import TreeViewer


class View:
    none = -1
    graph = (1 << 0)
    osg = (1 << 1)
    scene = (1 << 2)
    tree = (1 << 3)


class WidgetContainer:
    def __init__(self):
        """
        Initializes an instance of the `Widget` class by setting properties `name`,
        `widget_type`, and `dock`.

        """
        self.name = ""
        self.widget_type = View()
        self.widget = None
        self.dock = None


class DSRViewer(QObject):
    save_graph_signal = Signal()
    close_window_signal = Signal()
    reset_viewer = Signal(QWidget)

    def __init__(self, window, G, options, main=None):
        """
        Initializes an instance of a class, setting up various timers and menus
        for viewing and managing forces, computing processor number, and connecting
        to the timer's `timeout()` signal to compute forces.

        Args:
            window (instance of the QWidget class.): 3D scene window for which the
                script is generating documentation.
                
                		- `window`: A QWidget object representing the main window of the
                application.
                		- `g`: A G object, which is a global variable used for computational
                tasks.
                		- `self`: Referencing the object instance being initialized.
                		- `available_geometry`: A QRect object representing the available
                geometry of the desktop, which is used to position the window.
                		- `main_widget`: A reference to the main widget of the application,
                which is the primary focus of the program.
                		- `docks`: A dictionary of QDockWidget objects, each representing
                a docking area for different parts of the application.
                		- `widgets`: A dictionary of QWidget objects, each representing
                a specific component of the application.
                		- `widgets_by_type`: A dictionary of lists, where each list
                contains QWidget objects of the same type (e.g., buttons, menus,
                etc.).
                
                	The `__init__` function initializes various aspects of the
                application, including setting up the menu bar, adding actions to
                the menu, starting timers, and connecting signals for computing
                updates to the processor number. However, it does not provide a
                summary at the end as instructed.
            G (`QObject`): 2D graphics context, which is used to draw the game's
                graphics and handle events related to the game's rendering.
                
                		- `G`: This is an instance of the `G` class, which represents
                the game grid. It has various attributes, including `n`: the number
                of processors in the grid, `L`: the size of the grid in each
                dimension, and `S`: the size of a single square on the grid.
                
                	In the following code, the `availableGeometry` property of
                QApplication's desktop is used to determine the size of the available
                space on the screen for the window to be placed. The `move` method
                is then called on the window object with arguments
                `(available_geometry.width() - window.width()) / 2`, and
                `(available_geometry.height() - window.height()) / 2`. This moves
                the window to the center of the available space.
                
                	The `__initialize_file_menu`, `__initialize_views`, and `__init`
                methods are not directly mentioned in the code snippet provided,
                but they likely play a role in initializing various elements of
                the application's user interface, such as menus and views.
                
                	The `actionsMenu` is added to the window's menu bar with an action
                named "Restart". This allows the user to quit the application by
                clicking on this action. The `start` method of the `alive_timer`
                is called to start the timer, which will intervalically compute
                forces for the game grid. Similarly, the `start` method of the
                `timer` is called to start a timer that will fire every 500 milliseconds.
            options (object of class QDesignChooserOption.): 2D geometry of the
                window and its associated layout options, which are used to determine
                the position and size of the window and its child widgets during
                the initialization process.
                
                		- `G`: The instance of `G` class, which contains information
                about the grid size and spacing.
                		- `window`: The instance of `QMainWindow` class, which represents
                the main window of the application.
                		- `view_menu`, `file_menu`, and `forces_menu`: These are instances
                of `QMenu` classes, which contain menu items for various options.
                		- `main_widget`: The instance of `QWidget` class, which represents
                the main widget of the application.
                		- `docks`: A dictionary containing information about docking widgets.
                		- `widgets`: A dictionary containing information about all widgets
                in the application.
                		- `widgets_by_type`: A dictionary containing information about
                the types of widgets in the application.
                		- `available_geometry`: An instance of `QSize` class, which
                represents the available geometry of the screen.
            main (object/variable/value.): main widget of the application, which
                is passed to the function as an argument to allow the initialization
                of the window and its menus.
                
                		- `window`: The QMainWindow object that is the primary interface
                for the application.
                		- `view_menu`: A QMenu object that contains the "View" menu items.
                		- `file_menu`: A QMenu object that contains the "File" menu items.
                		- `forces_menu`: A QMenu object that contains the "Forces" menu
                items.
                		- `docks`: A dictionary containing the dock windows of the application.
                		- `widgets`: A dictionary containing the widgets created by the
                user.
                		- `widgets_by_type`: A dictionary that maps the type of each
                widget to its corresponding instance.
                		- `available_geometry`: The available geometry of the screen,
                used to position the window.
                		- `timer`: A QTimer object used for computing the forces in the
                simulation.
                		- `alive_timer`: An QElapsedTimer object used to measure the
                time the application is running.

        """
        super().__init__()
        self.timer = QTimer()
        self.alive_timer = QElapsedTimer()
        self.g = G
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
        viewMenu = window.menuBar().addMenu(window.tr("&View"))
        forcesMenu = window.menuBar().addMenu(window.tr("&Forces"))
        actionsMenu = window.menuBar().addMenu(window.tr("&Actions"))
        restart_action = actionsMenu.addAction("Restart")

        self.__initialize_views(options, main)
        self.alive_timer.start()
        self.timer.start(500)
        # self.init()  #intialize processor number
        # connect(timer, SIGNAL(timeout()), self, SLOT(compute()))

    def __del__(self):
        """
        Saves the window size and position as settings to the QSettings object
        "RoboComp" and "DSR".

        """
        settings = QSettings("RoboComp", "DSR")
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.window.size())
        settings.setValue("pos", self.window.pos())
        settings.endGroup()

    def get_widget_by_type(self, widget_type) -> QWidget:
        """
        Checks if a widget type exists in an internal dictionary and returns the
        corresponding widget if it does, otherwise it returns `None`.

        Args:
            widget_type ('object'.): type of widget for which the function is
                searching in the `self.widgets_by_type` dictionary.
                
                		- If `widget_type` is present in the `self.widgets_by_type`
                dictionary, it returns a `Widget` instance from that dictionary entry.
                		- Otherwise, it returns `None`.

        Returns:
            QWidget: a widget instance if the `widget_type` argument exists in the
            function's dictionary of widgets, otherwise it returns `None`.

        """
        if widget_type in self.widgets_by_type:
            return self.widgets_by_type[widget_type].widget
        return None

    def get_widget_by_name(self, name) -> QWidget:
        """
        Searches through a list of widgets (`self.widgets`) for the specified
        `name`. If found, it returns the corresponding widget, otherwise it returns
        `None`.

        Args:
            name (str): name of a widget in the `self.widgets` dictionary, and if
                it exists in the dictionary, the function returns the widget
                associated with that name; otherwise, the function returns `None`.

        Returns:
            QWidget: the widget associated with the given name, or `None` if no
            such widget exists.

        """
        if name in self.widgets:
            return self.widgets[name].widget
        return None

    def add_custom_widget_to_dock(self, name, custom_view):
        """
        Adds a custom widget to an existing dock, creating and managing associated
        docks and menus as needed.

        Args:
            name (str): name of the widget container, which is assigned to the
                `name` attribute of a new instance of the `WidgetContainer` class.
            custom_view (`View`.): widget to be displayed in the docking area.
                
                		- `type`: This is set to `View.none`, indicating that no view
                is being created.
                		- `name`: This is set to `name`, indicating the name of the
                widget being added to the dock.
                		- `widget`: This is set to `custom_view`, which is a `WidgetContainer`
                object representing the custom view to be added to the dock.

        """
        widget_c = WidgetContainer()
        widget_c.name = name
        widget_c.type = View.none
        widget_c.widget = custom_view
        self.widgets[name] = widget_c
        self.__create_dock_and_menu(name, custom_view)
        # Tabification of current docks
        previous = None
        for dock_name, dock in self.docks.items():
            if previous and previous != dock:
                self.window.tabifyDockWidget(previous, self.docks[name])
                break
            previous = dock
        self.docks[name].raise_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_window_signal.emit()

    # SLOTS
    def save_graph_slot(self, state):
        self.save_graph_signal.emit()

    def restart_app(self, state):
        pass

    def switch_view(self, state, container):
        """
        Updates the visibility of a widget and its dock based on a given state,
        controlling the block signals of the widget to manage its visibility and
        calling a reset viewer signal to restore the widget's original state.

        Args:
            state (bool): visibility state of the widget, with `True` indicating
                it is hidden and `False` indicating it is visible.
            container (object (Python).): widget's container, which is used to
                control the visibility and raising of the widget.
                
                		- `widget`: This property refers to a widget object that is
                displayed in the user interface.
                		- `dock`: This property refers to a docking manager object that
                manages the placement and visibility of widgets in the user interface.
                		- `state`: This property indicates whether the view should be
                shown or hidden. If `state` is True, the view is shown; otherwise,
                it is hidden.

        """
        widget = container.widget
        dock = container.dock
        if state:
            widget.blockSignals(True)
            dock.hide()
        else:
            widget.blockSignals(False)
            self.reset_viewer.emit(widget)
            dock.show()
            dock.raise_()

    def compute(self):
        pass

    def __create_dock_and_menu(self, name, view):
        # TODO: Check if name exists in docks
        """
        Creates a new dock widget and adds it to the window's dock area, while
        also creating an action for switching between views in the menu bar.

        Args:
            name (str): name of a widget that will be created and added to the
                main window.
            view (QObject or QWidget.): bird's eye view widget that will be displayed
                within the docked container.
                
                		- `name`: a string representing the name of the view
                		- `widget`: the widget representing the view
                		- `docks`: a dictionary containing the name of each dock and its
                corresponding dock widget
                		- `window`: a `QMainWindow` object representing the main window
                
                	Inside the `if` block, the dock widget is created by calling the
                `QDockWidget` constructor and passing in the name as an argument.
                The new action is then created by calling the `QAction` constructor
                and setting its properties accordingly. The action's `triggered`
                signal is connected to a lambda function that switches the view
                when triggered.
                
                	Inside the `else` block, the dock widget is created with the
                provided name, and its properties are set. The new action is also
                created and added to the `view_menu`. The dock widget's `dock`
                attribute is set to the widget representing the view. Finally, the
                dock widget is added to the right dock widget area of the main
                window using the `addDockWidget` method.

        """
        if name in self.docks:
            dock_widget = self.docks[name]
            self.window.removeDockWidget(dock_widget)
        else:
            dock_widget = QDockWidget(name)
            new_action = QAction(name, self)
            new_action.setStatusTip("Create a new file")
            new_action.setCheckable(True)
            new_action.setChecked(True)
            new_action.triggered.connect(lambda state: self.switch_view(state, self.widgets[name]))
            self.view_menu.addAction(new_action)
            self.docks[name] = dock_widget
            self.widgets[name].dock = dock_widget
        dock_widget.setWidget(view)
        dock_widget.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.window.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        dock_widget.raise_()

    def __initialize_views(self, options, central):
        # Create docks view and main widget
        """
        Initializes docks, creates a main widget, and connects signals between
        graph and tree widgets based on user preferences.

        Args:
            options (int): bitwise operation performed on the `widget_type` variable,
                indicating which widget types are included or excluded from being
                created and associated with the `self.window`.
            central (`View.graph`.): 3D viewer or graph widget that should be
                placed as the central widget of the main window, and it is used
                to set the central widget of the main window when the function is
                called.
                
                		- If `central == View.none`, it means that no central widget was
                specified in the initialization code.
                		- If `central` is a non-empty string in the list of valid options
                (`valid_options`), it represents a specific widget type, and the
                function creates and sets the central widget to that type.
                		- The `central` property can also be set to any valid widget
                type from the list, indicating which widget to display as the main
                widget.

        """
        valid_options = [(View.graph, "Graph"), (View.tree, "Tree"), (View.osg, "3D"), (View.scene, "2D")]

        # Creation of docks and mainwidget
        for widget_type, widget_name in valid_options:
            if widget_type == central and central != View.none:
                viewer = self.__create_widget(widget_type)
                self.window.setCentralWidget(viewer)
                widget_c = WidgetContainer()
                widget_c.widget = viewer
                widget_c.name = widget_name
                widget_c.type = widget_type
                self.widgets[widget_name] = widget_c
                self.widgets_by_type[widget_type] = widget_c
                self.main_widget = viewer
            elif options & widget_type:
                viewer = self.__create_widget(widget_type)
                widget_c = WidgetContainer()
                widget_c.widget = viewer
                widget_c.name = widget_name
                widget_c.type = widget_type
                self.widgets[widget_name] = widget_c
                self.widgets_by_type[widget_type] = widget_c
                self.__create_dock_and_menu(widget_name, viewer)
        if View.graph in self.widgets_by_type:
            new_action = QAction("Animation", self)
            new_action.setStatusTip("Toggle animation")
            new_action.setCheckable(True)
            new_action.setChecked(False)
            self.forces_menu.addAction(new_action)
            new_action.triggered.connect(lambda: self.widgets_by_type[View.graph].widget.toggle_animation(True))

        # Tabification of current docks
        previous = None
        for dock_name, dock_widget in self.docks.items():
            if previous:
                self.window.tabifyDockWidget(previous, dock_widget)
            previous = dock_widget

        # Connection of tree to graph signals
        if "Tree" in self.docks:
            if self.main_widget:
                graph_widget = self.main_widget
                if graph_widget:
                    tree_widget = self.docks["Tree"].widget()
                    tree_widget.node_check_state_changed_signal.connect(
                        lambda node_id: graph_widget.hide_show_node_SLOT(node_id, 2)
                    )
        if len(self.docks) > 0 or central != None:
            self.window.show()
        else:
            self.window.showMinimized()

    def __initialize_file_menu(self):
        """
        Adds a file menu to the user interface and adds three actions: "Save,"
        "RGBD," and "Laser." When the "Save" action is triggered, the function
        calls the `__save_json_file` function with the "Save" and "RGBD" actions
        as arguments.

        """
        file_menu = self.window.menuBar().addMenu(self.window.tr("&File"))
        file_submenu = file_menu.addMenu("Save")
        save_action = QAction("Save", self)
        file_submenu.addAction(save_action)
        rgbd = QAction("RGBD", self)
        rgbd.setCheckable(True)
        rgbd.setChecked(False)
        file_submenu.addAction(rgbd)
        laser = QAction("Laser", self)
        laser.setCheckable(True)
        laser.setChecked(False)
        file_submenu.addAction(laser)
        # save_action
        save_action.triggered.connect(lambda: self.__save_json_file(rgbd, laser))

    def __save_json_file(self, rgbd, laser):
        """
        Saves a JSON file containing the contents of an RGBD and Laser sensor data
        to a specified location using `QFileDialog`. It skips writing certain
        sensors if they are not checked in the user interface.

        Args:
            rgbd (bool): 3D Reconstruction component and is skipped when saving
                the JSON file if the corresponding checkbox is not checked.
            laser (bool): laser data to be included in the JSON file being created.

        """
        file_name = QFileDialog.getSaveFileName(None, "Save file",
                                                "/home/robocomp/robocomp/components/dsr-graph/etc",
                                                "JSON Files (*.json)",
                                                None,
                                                QFileDialog.Option.DontUseNativeDialog)
        skip_content = []
        if not rgbd.isChecked():
            skip_content.push_back("rgbd")
        if not laser.isChecked():
            skip_content.push_back("laser")
        self.g.write_to_json_file(file_name.toStdString(), skip_content)
        print("File saved")

    def __create_widget(self, widget_type):
        """
        Takes a `g` argument and determines the type of viewer to create based on
        the value of the `widget_type` argument. It then creates the appropriate
        viewer object and returns it.

        Args:
            widget_type (int): 3D visualization type for which the corresponding
                viewer instance is to be created, with values for `View.graph`,
                `View.osg`, `View.tree`, `View.scene`, and `View.none`.

        Returns:
            osg::State &` or an equivalent view instance depending on the input
            argument value assigned to `widget_type: a view instance corresponding
            to the specified `widget_type`.
            
            		- `None`: This is the value returned when the `widget_type` parameter
            does not match any of the possible widget types.
            		- `GraphViewer`: This class is derived from QGraphicItem and provides
            a 2D graph viewer for visualizing graphs. It takes the graph object
            as an argument in its constructor.
            		- `OSG3dViewer`: This class is derived from QObject and provides a
            3D viewer for visualizing OSG files. It takes the graph object and a
            scale factor as arguments in its constructor.
            		- `TreeViewer`: This class is derived from QTreeView and provides a
            tree-like structure for visualizing graphs. It takes the graph object
            as an argument in its constructor.
            		- `QScene2dViewer`: This class is derived from QScenery and provides
            a 2D viewer for visualizing graphs. It takes the graph object as an
            argument in its constructor.
            		- `None`: This value is returned when no valid widget type match is
            found.

        """
        widget_view = None
        if widget_type == View.graph:
            widget_view = GraphViewer(self.g)
        elif widget_type == View.osg:
            widget_view = OSG3dViewer(self.g, 1, 1)
        elif widget_type == View.tree:
            widget_view = TreeViewer(self.g)
        elif widget_type == View.scene:
            widget_view = QScene2dViewer(self.g)
        elif widget_type == View.none:
            widget_view = None
        # self.reset_viewer.connect(self.reload)
        return widget_view


if __name__ == '__main__':
    sys.path.append('/opt/robocomp/lib')
    app = QApplication(sys.argv)
    from pydsr import *

    g = DSRGraph(0, "pythonAgent", 111)
    node = g.get_node("root")
    main_window = QMainWindow()
    print(node)
    current_opts = View.tree
    ui = DSRViewer(main_window, g, current_opts)
    custom_widget = QPushButton("Custom Widget")
    ui.add_custom_widget_to_dock("Custom", custom_widget)
    print("Setup")
    main_window.show()
    app.exec_()

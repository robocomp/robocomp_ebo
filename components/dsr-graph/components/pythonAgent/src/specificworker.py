#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2020 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

#from PySide2.QtCore import QTimer
#from PySide2.QtWidgets import QApplication
from genericworker import *


from pydsr import *

# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

def update_node_att(id: int, attribute_names: [str]):
    print("UPDATE NODE ATT: ", id, " ", attribute_names)

def update_node(id: int, type: str):
    print("UPDATE NODE: ", id," ",  type)

def delete_node(id: int):
    print("DELETE NODE: ", id)

def update_edge(fr: int, to: int, type : str):
    print("UPDATE EDGE: ", fr," ", to," ", type)

def update_edge_att(fr: int, to: int, attribute_names : [str]):
    print("UPDATE EDGE ATT: ", fr," ", to," ", attribute_names)

def delete_edge(fr: int, to: int, type : str):
    print("DELETE EDGE: ", fr," ", to," ", type)



class SpecificWorker(GenericWorker):

    def signal_node_att(self, id: int, attribute_names: [str]):
        print("UPDATE NODE ATT: ", id, " ", attribute_names)
        print(self.g.get_node(id))

    def __init__(self, proxy_map, startup_check=False):
        """
        Establishes a DSRGraph object, connects it to signals for updating node
        and edge attributes and firing events, and starts a timer for periodical
        computation.

        Args:
            proxy_map (`object`.): mapping of proxy functions to original functions,
                which is used to intercept and handle signal events in the graph.
                
                		- ` proxy_map`: The input to the `__init__` function is a
                dictionary containing various keys, each representing an agent or
                node property.
                		- `0`: The key `0` represents the ID of the DSR graph.
            startup_check (bool): execution of an additional check during the
                initialization of the object, which can be used to perform additional
                tasks before the main processing loop starts.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        #test_fn(self.dsrgetid_proxy)

        self.g = DSRGraph(0, "pythonAgent", 111)

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, update_node_att)
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.signal_node_att)
            signals.connect(self.g, signals.UPDATE_NODE, update_node)
            signals.connect(self.g, signals.DELETE_NODE, delete_node)
            signals.connect(self.g, signals.UPDATE_EDGE, update_edge)
            signals.connect(self.g, signals.UPDATE_EDGE_ATTR, update_edge_att)
            signals.connect(self.g, signals.DELETE_EDGE, delete_edge)

            print("signals connected")

        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        print('SpecificWorker destructor')
        #self.g.__exit__()

    def setParams(self, params):
        #try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        #except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        """
        Computes something based on the input it receives, returning a truthy value
        upon successful completion.

        Returns:
            Optional[True: a boolean value indicating whether the given node is a
            "laser" node.
            
            		- `True`: The function returns `True` indicating that the operation
            was successful.

        """
        print('SpecificWorker.compute...')

        #a = Node(123, "laser", "laserprueba")
        #node = self.g.get_node("world")

        #print(node)

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)





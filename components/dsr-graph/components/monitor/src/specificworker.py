#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2021 by YOUR NAME HERE
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

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *
import json


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        """
        Initializes an instance of `SpecificWorker` by setting various attributes
        and connecting signals to handle updates, deletions, and other graph-related
        events.

        Args:
            proxy_map (dict): map of agent ID to proxy ID, which allows the agent
                to communicate with other agents through their proxies.
            startup_check (`object`.): initialization code that should be executed
                if the object is being created during program startup.
                
                		- `startup_check`: This is a boolean attribute that determines
                whether the `startup_check` function should be executed when the
                instance is initialized. It can be set to either `True` or `False`.

        """
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 69
        self.g = DSRGraph(0, "monitor", self.agent_id)
        self.plan = None
        self.plan_node_id = None

        try:
            signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        """
        Performs updates to the innermodel using the QMat library, specifically
        setting the speed base for a robot and updating transform values for a
        head rotational pose.

        Returns:
            bool: a vector containing the rotation and translation values for the
            robot's head.

        """
        print('SpecificWorker.compute...')
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)






    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')
        pass

    def update_node(self, id: int, type: str):
        """
        Updates a node's information in a plan by retrieving the current intention
        from the graph, loading the intention into a JSON object, and saving it
        as the plan.

        Args:
            id (int): ID of the node to be updated, which is used to identify the
                node in the graph and store its updated plan information.
            type (str): type of update being performed on the node, with possible
                values being `'intention'`.

        """
        console.print(f"UPDATE NODE: {id} {type}", style='green')
        if type == 'intention':
            node = self.g.get_node('current_intention')
            self.plan = json.loads(node.attrs['current_intention'].value)
            self.plan_node_id = id
            print("Plan info inserted")
            print(f"Node ID: {self.plan_node_id}")
            print(f"Plan: {self.plan}")

    def delete_node(self, id: int):
        """
        Removes plan information associated with a given node ID.

        Args:
            id (int): node's unique identifier for removal from the plan.

        """
        console.print(f"DELETE NODE:: {id} ", style='green')
        if id == self.plan_node_id:
            self.plan = None
            self.plan_node_id = None
            print("Plan info removed")

    def update_edge(self, fr: int, to: int, type: str):
        console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')
        pass

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')
        pass

    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')
        pass

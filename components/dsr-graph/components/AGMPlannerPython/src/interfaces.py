import os
import pathlib
import time
import traceback
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()


Ice.loadSlice("-I ./src/ --all ./src/AGGLPlanner.ice")
import RoboCompAGGLPlanner


import agglplannerI



class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes an instance of the `IceConnector` class, setting its attributes
        to `ice_connector`, `mprx`, and `topic_manager`.

        Args:
            ice_connector (object reference (of an unspecified class).): IceConnector
                class, which is used to connect to an external ice framework instance.
                
                		- `self.ice_connector`: This is an instance of `ICEConnector`,
                which contains information about how to connect to an ice house.
            topic_manager (`object`.): Topic Manager for which the IceConnector
                is being created.
                
                		- `mprx`: a dictionary that stores all the published topics from
                the topic map, with keys being the topic names and values being
                lists of Pub-Sub messages.
                		- `ice_connector`: a reference to the IceConnector class.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic or retrieves an existing one based on its name, and
        then returns a publisher proxy for that topic.

        Args:
            topic_name (str): name of a topic for which a publisher is being created.
            ice_proxy (icedrive::~IceStorm::ObjectReference.): icy published adapter
                for a topic, which is created and cached in the function for
                subsequent use.
                
                		- `ice_oneway()` - This is an Ice::OneWay instance which provides
                a one-way proxy to the published interface.
                		- `uncheckedCast(pub)` - This is an Ice::Proxy instance that is
                created by casting the Ice::OneWay instance to the Ice::Proxy
                interface using the `uncheckedCast` method, without performing any
                type checking.
                		- `mprx` - This is a dictionary of Ice::Proxy instances for each
                topic, where each key is the topic name and the value is the
                corresponding proxy.

        Returns:
            Ice.Publisher: an ICE proxy object representing the published topic.
            
            		- `pub`: A `Ice.InputStream` object representing the topic publisher.
            		- `proxy`: An `ice_proxy.uncheckedCast` object representing the topic
            proxy.
            		- `mprx`: A dictionary containing the created topic proxies. The key
            is the topic name, and the value is the topic proxy.

        """
        topic = False
        try:
            topic = self.topic_manager.retrieve(topic_name)
        except:
            pass
        while not topic:
            try:
                topic = self.topic_manager.retrieve(topic_name)
            except IceStorm.NoSuchTopic:
                try:
                    topic = self.topic_manager.create(topic_name)
                except:
                    print(f'Another client created the {topic_name} topic? ...')
        pub = topic.getPublisher().ice_oneway()
        proxy = ice_proxy.uncheckedCast(pub)
        self.mprx[topic_name] = proxy
        return proxy

    def get_proxies_map(self):
        return self.mprx


class Requires:
    def __init__(self, ice_connector):
        self.ice_connector = ice_connector
        self.mprx={}

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Generates a proxy for an object (CameraSimple) and sets the resulting proxy
        as the value of a specified property name in a dict (`self.mprx`). It
        checks if the property exists on the object and throws an exception if it
        doesn't. If the property exists, it returns a tuple of true and the proxy.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (icy proxy reference.): iced proxy object that is unchecked
                cast to an arbitrary proxy object during the getter method call.
                
                		- `uncheckedCast`: This attribute is a reference to the
                `uncheckedCast` method of the `ice_proxy` class. It is used to
                convert a raw `InputStream` into an Ice::Connection object. (Type:
                Method)
                		- `mprx`: This attribute is a dictionary containing properties
                of the remote object, keyed by their names. (Type: Dictionary)

        Returns:
            ice.proxy.IceProxy: a tuple of two values: `True` and the successfully
            created proxy object.
            
            		- `True, proxy`: If the function succeeds in creating a proxy for
            the given property, `True` is returned as the first element of the
            tuple. The `proxy` element is a Ice.ObjectPrx representing the remote
            object.
            		- `False, None`: If the function fails to create a proxy due to an
            error or exception, `False` is returned as the first element of the
            tuple. The second element is `None`, indicating that the proxy could
            not be created.

        """
        try:
            proxy_string = self.ice_connector.getProperties().getProperty(property_name)
            try:
                base_prx = self.ice_connector.stringToProxy(proxy_string)
                proxy = ice_proxy.uncheckedCast(base_prx)
                self.mprx[property_name] = proxy
                return True, proxy
            except Ice.Exception:
                print('Cannot connect to the remote object (CameraSimple)', proxy_string)
                # traceback.print_exc()
                return False, None
        except Ice.Exception as e:
            console.print_exception(e)
            console.log(f'Cannot get {property_name} property.')
            return False, None


class Subscribes:
    def __init__(self, ice_connector, topic_manager, default_handler):
        self.ice_connector = ice_connector
        self.topic_manager = topic_manager

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an adapter and a publisher proxy, subscribes to a topic, and
        activates the adapter to establish communication between the application
        and the topic.

        Args:
            property_name (str): name of the topic that is to be created and
                subscribed to, and it is used to create and manage the topic within
                the application.
            interface_handler (`Ice.InvocationHandler` instance.): handler that
                will handle messages sent to the topic created by the function,
                which can be an instance of an object derived from the
                `iceman.transport.TopicPublisher` class.
                
                		- `property_name`: The name of the property that contains the
                interface handler.
                		- `ice_connector`: An instance of `Ice.ConnectionManager`.
                		- `topic_manager`: An instance of `Ice.TopicManager`.
                		- `qos`: A dictionary of QoS parameters.
                
                	Note: The input `interface_handler` may be a complex object with
                various properties and attributes, depending on the specific implementation.

        Returns:
            ice.adapter.Adapter` object: an activated ICE adapter with a created
            topic and subscription to the topic.
            
            		- `adapter`: A PyQt5 `QObject` instance representing the ice adapter.
            		- `handler`: A PyQt5 `QObject` instance representing the interface
            handler.
            		- `proxy`: A PyQt5 `QObject` instance representing the proxy object
            created by adding the interface handler to the adapter using `ice_oneway()`.
            		- `topic_name`: A string representing the name of the topic being
            subscribed to.
            		- `subscribe_done`: A boolean value indicating whether the topic
            subscription was successfully done or not.
            		- `qos`: An instance of the `QOS` class representing the QoS parameters
            for the topic subscription.
            		- `adapter.activate()`: This method activates the adapter, allowing
            it to receive and process messages.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        handler = interface_handler
        proxy = adapter.addWithUUID(handler).ice_oneway()
        topic_name = property_name.replace('Topic','')
        subscribe_done = False
        while not subscribe_done:
            try:
                topic = self.topic_manager.retrieve(topic_name)
                subscribe_done = True
            except Ice.Exception as e:
                console.log("Error. Topic does not exist (creating)", style="blue")
                time.sleep(1)
                try:
                    topic = self.topic_manager.create(topic_name)
                    subscribe_done = True
                except:
                    console.log(f"Error. Topic {Text(topic_name, style='red')} could not be created. Exiting")
                    status = 0
        qos = {}
        topic.subscribeAndGetPublisher(qos, proxy)
        adapter.activate()
        return adapter


class Implements:
    def __init__(self, ice_connector, default_handler):
        self.ice_connector = ice_connector
        self.agglplanner = self.create_adapter("AGGLPlanner", agglplannerI.AGGLPlannerI(default_handler))

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an object adapter with the given name and adds an interface handler
        to it, then activates the adapter.

        Args:
            property_name (str): name of the property to which the interface handler
                should be added.
            interface_handler (` Identity` value.): 3GPP interface object to which
                the provided property name corresponds, and is added to the adapter
                created by the `self.ice_connector.createObjectAdapter()` method.
                
                		- `self.ice_connector`: This is an instance of the `ICertificate`
                class, which represents a certificate and its associated information.
                		- `property_name`: This is the name of the property that the
                adapter is created for.
                		- `stringToIdentity()`: This is a method of the `ice_connector`
                object that converts a string to an identity. It takes a lowercase
                string as input and returns an identity object representing the string.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Sets up Ice configurations and properties, creates a Topic Manager and
        Requires, Publishes, Implements and Subscribes based on the given Ice
        connector information.

        Args:
            ice_config_file (str): Ice configuration file that is used to initialize
                the Ice library and set up the connection to the RCNode.

        """
        self.ice_config_file = ice_config_file
        self.ice_connector = Ice.initialize(self.ice_config_file)
        needs_rcnode = False
        self.topic_manager = self.init_topic_manager() if needs_rcnode else None

        self.status = 0
        self.parameters = {}
        for i in self.ice_connector.getProperties():
            self.parameters[str(i)] = str(self.ice_connector.getProperties().getProperty(i))
        self.requires = Requires(self.ice_connector)
        self.publishes = Publishes(self.ice_connector, self.topic_manager)
        self.implements = None
        self.subscribes = None



    def init_topic_manager(self):
        # Topic Manager
        """
        Retrieves the proxy for the Topic Manager and casts it to an
        IceStorm.TopicManagerPrx object.

        Returns:
            IceStorm.TopicManagerPrx: an IceStorm.TopicManagerPrx object.
            
            		- `proxy`: The proxy object is generated using the
            `self.ice_connector.getProperties().getProperty("TopicManager.Proxy")`
            method and represents the Topic Manager's Proxy object.
            		- `obj`: The `obj` variable is set to the result of calling the
            `self.ice_connector.stringToProxy(proxy)` method, which converts the
            `proxy` string to a Proxy object.
            		- `IceStorm.TopicManagerPrx`: The returned value is checked against
            an instance of `IceStorm.TopicManagerPrx` using the `checkedCast()`
            method to ensure that it is a valid Topic Manager reference.

        """
        proxy = self.ice_connector.getProperties().getProperty("TopicManager.Proxy")
        obj = self.ice_connector.stringToProxy(proxy)
        try:
            return IceStorm.TopicManagerPrx.checkedCast(obj)
        except Ice.ConnectionRefusedException as e:
            console.log(Text('Cannot connect to rcnode! This must be running to use pub/sub.', 'red'))
            exit(-1)

    def set_default_hanlder(self, handler):
        self.implements = Implements(self.ice_connector, handler)
        self.subscribes = Subscribes(self.ice_connector, self.topic_manager, handler)

    def get_proxies_map(self):
        """
        Updates a `result` dictionary with proxy maps for requires and publishes.

        Returns:
            object (denoted by : a dictionary of proxy settings for both requires
            and publishes.
            
            		- `result`: The final output value resulting from the updates applied
            by `get_proxies_map`. This is a dictionary with keys representing proxy
            hosts and values representing their respective ports.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





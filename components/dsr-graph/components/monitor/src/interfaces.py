import os
import pathlib
import time
import traceback
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()







class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes an instance of the `ice_connector` class, setting its
        `self.ice_connector` attribute to a reference to an instance of the
        `ice_connector` class, and its `self.mprx` dictionary and `self.topic_manager`
        attribute to their default values.

        Args:
            ice_connector (`iceConnector`.): ices connection to be generated for
                the provided `topics`.
                
                		- `ice_connector`: The object returned by `ice_connector()` which
                represents an ICE connector.
                		- `mprx`: A dictionary containing metadata about the topic.
            topic_manager (`TopicManager`.): managed topic instance that is being
                initialized for further use by the class, providing access to the
                underlying ice::managed_ptr for efficient manipulation and management
                of the topic.
                
                		- `self.mprx`: An empty dictionary representing the topic manager's
                map of property renamings.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic and its publisher, or retrieves an existing topic and
        its publisher based on the given name, returning the publisher as an
        ice_oneway proxy.

        Args:
            topic_name (ice_identity reference.): name of a topic that the function
                is trying to retrieve or create.
                
                		- `topic_name`: The name of the topic to be created.
                		- `topic_manager`: An instance of the `TopicManager` class, which
                manages topics in the system.
                		- `getPublisher()`: A method that retrieves the publisher interface
                for the specified topic.
                		- `ice_oneway()`: An Ice build-in one-way communication mechanism
                that allows clients to send messages to a server without waiting
                for responses.
                		- `uncheckedCast()`: An Ice casting mechanism that allows casting
                of an object without checking its type, which is used in this case
                to convert the `getPublisher()` return value to a proxy.
                
                	In conclusion, the `create_topic` function creates a new topic
                and returns its publisher proxy for communication with the server.
            ice_proxy (`IceProxy`.): icy published adapter that is cast into an
                unchecked IcePython proxy for a topic's publisher.
                
                		- `uncheckedCast(pub)`: This method is used to convert an
                ice::Publisher into a Python object of type `Proxy`. The method
                name `uncheckedCast()` suggests that it does not perform any
                validation or checking of the input, and therefore should only be
                called with trusted inputs.
                		- `ice_oneway()`: This is a static method of the `ice` module
                that returns an ice::OneWay servant. It is used to create a one-way
                communication channel from the client to the server.

        Returns:
            IcePy proxy object, specifically the `ice_proxy.uncheckedCast(pub)`
            result: an Ice::Publisher proxy object linked to the specified topic.
            
            		- `pub`: The publisher for the topic, which is an Ice::Oneway stream.
            		- `proxy`: An ice_proxy object that proxies the `pub` stream to clients.
            		- `self.mprx`: A dictionary storing proxies for all topics created
            by the client.
            
            	The function creates a new topic if one does not already exist with
            the given name, and then returns a proxy for the publisher of the
            topic. The `pub` stream is an Ice::Oneway stream, which means that it
            allows for one-way communication from the server to the client without
            expecting any response. The `proxy` object serves as a bridge between
            clients and the `pub` stream, allowing clients to access the stream
            while the server remains unaware of their presence.

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
        Creates an IcePy proxy for a remote object (CameraSimple) based on a
        property name provided by the user and returns True or False indicating success/failure.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (`uncheckedCast<ice_proxy::Transport::Ex>` .): icy proxy
                object that will be returned if the remote object (CameraSimple)
                can be connected to and retrieved.
                
                		- `uncheckedCast`: This attribute returns the Ice proxy instance
                obtained by converting the `base_prx` string representation to a
                proxy using the `Ice.stringToProxy()` method.
                		- `mprx`: A dictionary containing properties of the remote object,
                where each property is accessed using its corresponding property
                name as key.

        Returns:
            : `proxy` which is an `ice.Invocation` instance: a tuple containing
            the successfully created proxy or an error message if any.
            
            		- `True`, `proxy`: If the creation of the proxy was successful, this
            tuple contains `True` as the first element and the created proxy as
            the second element. Otherwise, it contains `False` and `None`.
            		- `property_name`: The name of the property being accessed on the
            remote object.
            		- `base_prx`: The base Proxy object created from the
            `ice_connector.stringToProxy()` method.
            		- `proxy`: The final Proxy object, which is either `base_prx` or an
            unchecked cast to the desired Proxy type (`ice_proxy.uncheckedCast()`).

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
        Creates an Ice client adapter and adds a proxy to handle an incoming one-way
        association request. It retrieves or creates a topic based on the provided
        property name, subscribes to the topic, and returns the activated adapter.

        Args:
            property_name (str): name of a topic that needs to be subscribed to,
                and is used to create a new adapter object and set the topic name
                for the subscription.
            interface_handler (int): handler that will handle the published messages
                from the created topic.

        Returns:
            Ice::Adapter: an instance of an ICE adapter object that subscribe to
            a topic and returns a proxy for one-way communication.
            
            		- `adapter`: The created Ice::Adapter instance, which is used to
            handle connections and invocations.
            		- `handler`: The InterfaceHandler that represents the interface
            defined in the `property_name`.
            		- `proxy`: The Ice::OneWay instance that proxies the handler's
            operations onto the specified Topic.
            		- `topic_name`: The name of the Topic associated with the Interface,
            which is used to identify and subscribe to the Topic.
            		- `subscribe_done`: A boolean value indicating whether the Topic has
            been successfully subscribed to or not.
            		- `qos`: An empty dictionary that will be populated with QoS settings
            when the adapter is activated.
            
            	The function performs various actions, including:
            
            		- Creating an Ice::Connector instance for the specified property name.
            		- Creating an InterfaceHandler instance for the defined interface.
            		- Proxying the InterfaceHandler's operations onto a Topic using Ice::OneWay.
            		- Subscribing to the Topic and populating the QoS dictionary with
            appropriate settings.
            		- Activating the adapter instance.

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

    def create_adapter(self, property_name, interface_handler):
        """
        Creates a new object adapter based on a property name and adds an interface
        handler to it. It then activates the adapter.

        Args:
            property_name (str): identity to which the `interface_handler` will
                be added.
            interface_handler (`identity`.): interface to be adapted.
                
                		- `self.ice_connector`: A reference to an IceConector object.
                (Explained below)
                		- `property_name`: A string indicating the property name to be
                handled by the adapter. (Provided as input)
                		- `stringToIdentity()`: A method provided by IceConnector that
                converts a string to an identity. (Used in the createObjectAdapter
                function)

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an Ice object, gets the needed RC node information, creates a
        topic manager and sets related parameters and properties based on the
        provided configuration file.

        Args:
            ice_config_file (str): configuration file for the Intermediate
                Representation (Ice) connector, which is used to initialize the
                Ice connector and set its properties based on the contents of the
                configuration file.

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
        Gets the Proxy property from an Ice Connector object and casts it to a
        TopicManagerPrx interface, attempting to connect to a rcnode service for
        publication and subscription purposes.

        Returns:
            IceStorm.TopicManagerPrx: an `IceStorm.TopicManagerPrx` object, which
            represents a proxy for the Topic Manager interface.
            
            		- `obj`: This is the IceStorm.TopicManagerPrx object, which represents
            the Topic Manager interface.
            		- `proxy`: This is the string value of the Proxy property of the
            IceConnector, which specifies the URL of the Topic Manager proxy server.

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
        Updates an object (`result`) with the union of two other objects' proxies
        maps obtained from the `requires` and `publishes` attributes, respectively.

        Returns:
            dict: a dictionary containing key-value pairs representing the proxies
            associated with the given code.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





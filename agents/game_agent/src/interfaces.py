import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()







class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes instance variables `ice_connector` and `topic_manager`, as
        well as a dictionary `mprx`.

        Args:
            ice_connector (object.): iced TEE (Trusted Execution Environment)
                connector, which is used to provide access to the TEE-based
                components and services within the system.
                
                	1/ `ice_connector`: The variable `ice_connector` holds an instance
                of an IceConnector class.
                	2/ `mprx`: A dictionary representing the metadata provider registry
                for this component.
                	3/ `topic_manager`: An object of the TopicManager class, responsible
                for handling topics in the system.
            topic_manager (object.): 3rd-party application's Topic Manager instance
                that manages the communication between the application and the
                Icehouse connectors.
                
                		- `mprx`: A dictionary containing the multiproperties of the
                manager, with each key being the name of a property and the value
                being a dictionary of its type and value.
                		- `ice_connector`: An instance of the `ICEConnector` class, which
                provides methods for working with the Interoperability Connection
                for Everyone (ICE) protocol.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic and assigns an ice publisher to it, creating an ice
        proxy for publication.

        Args:
            topic_name (str): name of a topic for which the function is retrieving
                or creating a publisher proxy.
            ice_proxy (`ice_proxy`.): icy-proxy instance that converts the Python
                publisher into an Ice IX publisher, allowing for communication
                between different language implementations.
                
                		- `uncheckedCast`: This method returns an instance of type
                `ice_proxy` without performing any runtime type checking. It is
                used to convert the publisher reference into a proxy reference
                that can be stored in the `mprx` dictionary.
                		- `getPublisher`: This property retrieves the `publisher` reference
                associated with the `ice_proxy` instance. It is a frozen Publisher
                reference, which means it cannot be modified or deleted once created.

        Returns:
            int: an ICE proxy for publishing messages to a specified topic.

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
        Takes a given property name and attempts to create an Ice Proxy for it by
        calling the `getProperties().getProperty()` method on an existing
        `Ice.Instancer` object. If successful, it creates a new instance of the
        remote class, sets its `mprx` attribute with the obtained proxy, and returns
        `(True, proxy)`.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (Ice.Identity (specifically, Ice.Identity instance)): icy
                proxy object that is used to convert the remote object's property
                value into a Python object, which is then assigned to the `mprx`
                dictionary.
                
                		- `uncheckedCast`: This attribute is a reference to the unchecked
                casting method provided by Ice.
                		- `stringToProxy`: This method is used to convert a string
                representation of a proxy to an actual `ice_proxy` object.
                		- `getProperties`: This method retrieves the properties of the
                current instance of the `ice_connector`.
                		- `getProperty`: This method retrieves a specific property from
                the current instance of the `ice_connector`.
                		- `property_name`: This variable is set to the name of the
                property to be retrieved, and it is passed as an argument to the
                `getProperty` method.

        Returns:
            bool: a tuple of two values: (True, the created proxy).

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
        Creates a new ICE (Intermediate Representation) adapter using the
        `ice_connector` object and adds a handler to the adapter. It then retrieves
        or creates a topic based on the given property name, subscribes to the
        topic, and returns the activated adapter.

        Args:
            property_name (str): name of the topic to be created and subscribed to.
            interface_handler (`object`.): handle for the interface that will be
                proxied through the adapter, and is used to create a proxy object
                that implements the desired interface.
                
                		- `self.ice_connector`: A reference to the IceConnector instance.
                		- `property_name`: The name of the property that contains the
                interface handle.
                		- `handler`: The interface handle deserialized from the input
                JSON data.
                		- `proxy`: An object returned by `adapter.addWithUUID()` and
                passed as a parameter to `ice_oneway()`.
                		- `topic_name`: The name of the topic for which the proxy is
                created, extracted from the input property name.
                		- `subscribe_done`: A boolean flag indicating whether the topic
                already exists or not.
                		- `time.sleep()`: A function used to wait for a specific amount
                of time before attempting to subscribe to the topic again if an
                exception occurs during subscription.
                		- `self.topic_manager`: A reference to the TopicManager instance,
                which manages topics and their subscribers.
                		- `create()`: A method called when the adapter is activated,
                used to create a new topic if it does not already exist.
                		- `retrieve()`: A method used to retrieve an existing topic by
                name from the TopicManager.

        Returns:
            instance of `iceoryk.adapter.IAdapter: an active Adaptator object.
            
            		- `adapter`: This is an instance of `ice.connector.ObjectAdapter`,
            which is created to manage communication between the client and server
            through the specified property name.
            		- `handler`: This is an instance of `interface_handler`, which is
            responsible for handling interface requests on behalf of the client.
            		- `proxy`: This is an instance of `ice.oneway`, which acts as a
            bridge between the client and server, allowing the client to communicate
            with the server through the handler.
            		- `topic_name`: This is the name of the topic for which the adapter
            is created. It is obtained by replacing the `Topic` prefix from the
            given property name.
            		- `subscribe_done`: This variable is used to control the loop that
            tries to subscribe to the topic. It is set to `True` once the topic
            has been successfully subscribed to, and `False` otherwise.
            		- `qos`: This is a dictionary object containing QoS (Quality of
            Service) settings for the topic subscription. It is returned by the
            `topic.subscribeAndGetPublisher()` method.
            		- `adapter.activate()`: This is a method called to activate the
            adapter, allowing it to communicate with the server.

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
        Creates a new adapter object and adds an interface handler to it, and
        activates the adapter using the `activate()` method.

        Args:
            property_name (str): name of a property that the function is creating
                an adapter for, which is used to set the identity of the interface
                handler in the adapter.
            interface_handler (identity.): interface to be handled by the `Adapter`,
                and it is passed to the `add()` method to add the interface to the
                adapter's list of handles.
                
                		- `self.ice_connector`: The Ice Connector used for creating and
                managing object adapters.
                		- `property_name`: The name of the property being adapted.
                		- `stringToIdentity`: A function used to convert a string
                representation of an identity into an identity value.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initialize ice config file and returns the topic manager object.

        Args:
            ice_config_file (file path or name.): icy configuration file that
                contains the settings and details required to establish communication
                between the client and the server.
                
                		- `ice_connector`: A `IceConnector` object that contains information
                about the ice server and its capabilities.
                		- `topic_manager`: An instance of `TopicManager`, which manages
                the topics exposed by the ice server. If `needs_rcnode` is `True`,
                this property is None, indicating that the topic manager has not
                been initialized.
                		- `requires`: A list of `Requires` instances that describe the
                capabilities required by the ice server to handle a particular topic.
                		- `publishes`: A list of `Publishes` instances that describe the
                topics exposed by the ice server and their corresponding data types.
                		- `implements`: A list of `Implements` instances that describe
                the interfaces implemented by the ice server.
                		- `subscribes`: A list of `Subscribes` instances that describe
                the interfaces subscribed to by the ice server.

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
        Retrieves the Proxy value from the `ice_connector` instance, converts it
        to an `TopicManagerPrx` object using the `stringToProxy` method, and returns
        the checked cast result. If the connection is refused, an error message
        is printed to the console and the program exits with a negative status code.

        Returns:
            IceStorm TopicManagerPrx: an `IceStorm.TopicManagerPrx` proxy object.
            
            		- `proxy`: A string representing the proxy to use for connecting to
            the topic manager.
            		- `obj`: An object of type `IceStorm.TopicManagerPrx`, which is
            returned after casting the input `proxy` string to a proxy object using
            `IceStorm.TopicManagerPrx.checkedCast()`.

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
        Updates the `result` object with the proxies maps from `requires` and `publishes`.

        Returns:
            dict: a dictionary of proxies maps for both required and published services.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





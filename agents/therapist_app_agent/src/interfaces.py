import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()







class Publishes:
    """
    Manages communication between clients and topics using IceStorm, a Publish-Subscribe
    messaging system. It creates and retrieves topics, establishes connections
    with them, and returns a map of proxies for accessing these topics.

    Attributes:
        ice_connector (IceConnector): Initialized during object creation through
            the constructor method `__init__`. It represents a connection to the
            ICE (Internet Communications Engine) service, which facilitates
            communication between distributed objects.
        mprx (Dict[str,Any]): Used to store proxies for topics as key-value pairs
            where keys are topic names and values are corresponding proxies obtained
            from IceStorm's topic manager.
        topic_manager (IceStormTopicManager): Used to manage topics, including
            retrieving and creating them. It allows accessing and controlling topic
            operations such as publishing and subscribing.

    """
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes an object with two attributes: `ice_connector` and `topic_manager`,
        as well as an empty dictionary `mprx`. This sets up the object's state for
        further usage.

        Args:
            ice_connector (object): Expected to be an instance of some class,
                likely related to ICE (Interoperable Communications Engine), which
                allows for communication between processes or applications.
            topic_manager (object): Assigned to an instance variable named
                `self.topic_manager`. It represents an object responsible for
                managing topics, possibly related to the Ice Connector and its usage.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Retrieves, creates or checks for an existing IceStorm topic with the given
        name. If the topic exists, it gets its publisher and sets up an oneway
        proxy to this publisher using the provided ice_proxy.

        Args:
            topic_name (str): Used as an identifier to retrieve or create a topic
                using the `self.topic_manager`. It is expected to be the name of
                a valid IceStorm topic.
            ice_proxy (Ice.ObjectProxy): Used to unchecked cast the returned
                publisher's proxy to an ObjectProxy for further use.

        Returns:
            proxy: A reference to an object that implements the interface specified
            by `ice_proxy`. This proxy allows clients to send requests to the topic
            publisher without blocking for a response.

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
    """
    Creates a map of proxies for Ice (Internet Communications Engine) properties
    and provides methods to get and create these proxies. It uses an `ice_connector`
    object to retrieve property values and convert them into proxies.

    Attributes:
        ice_connector (IceConnection): Initialized in the constructor. It serves
            as a bridge to interact with Ice objects by providing methods for
            getting properties, converting strings to proxies, and unchecked casting
            proxies.
        mprx (Dict[str,object]): Initialized as an empty dictionary. It stores
            proxies for properties retrieved from the ICE connector. The keys are
            property names and values are corresponding proxies.

    """
    def __init__(self, ice_connector):
        """
        Initializes an instance with an Ice connector and an empty dictionary
        `mprx`, which presumably stores some data or configuration related to the
        Ice connection.

        Args:
            ice_connector (object): Assigned to an instance variable with the same
                name. The purpose or definition of this parameter is not provided,
                but it likely represents an object that facilitates communication
                between different components.

        """
        self.ice_connector = ice_connector
        self.mprx={}

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Creates and registers an Ice proxy object for a given property name from
        an Ice connector. It tries to get the property, convert it to a proxy,
        cast it to the expected type using uncheckedCast, and store it in a dictionary.

        Args:
            property_name (str): Used to specify the name of a property that needs
                to be retrieved from the Ice connector and converted into a proxy
                object.
            ice_proxy (Ice.ObjectProxy): Used to uncheck-cast the base proxy
                obtained from the property returned by
                `self.ice_connector.getProperties().getProperty(property_name)`
                into an instance of the specific object class.

        Returns:
            Tuple[bool,None|Proxy]: 2-element tuple where first element is a boolean
            indicating success (True) or failure (False) and second element is
            either None if the proxy creation failed or actual Proxy object if successful.

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
    """
    Creates an Ice object adapter and subscribes it to a topic managed by the
    `topic_manager`. It retrieves or creates the topic if necessary, and sets up
    the subscription with a given handler. The subscription is activated after
    successful creation.

    Attributes:
        ice_connector (object): Initialized through the constructor (`__init__`)
            by passing an `Ice.Connector` object, which represents a connection
            to the Ice grid.
        topic_manager (object): Presumably responsible for managing Ice Topic
            objects. It provides methods to retrieve, create and manipulate topics.
            The exact implementation details are not provided.

    """
    def __init__(self, ice_connector, topic_manager, default_handler):
        """
        Initializes objects of Ice Connector, Topic Manager, and Default Handler
        as instance variables when an object of the class is created. These objects
        are used for subscribing to topics and handling events in the class.

        Args:
            ice_connector (object): Likely an instance of an Ice Connector class,
                responsible for establishing connections to other Ice components
                or clients.
            topic_manager (object): Assigned to an instance variable with the same
                name. It appears to be responsible for managing topics, likely in
                the context of message-oriented middleware or distributed systems.
            default_handler (object): Likely used as a default handler for events
                that do not have an assigned handler. It is stored in the instance
                of the class as an attribute.

        """
        self.ice_connector = ice_connector
        self.topic_manager = topic_manager

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an object adapter from an ice_connector, subscribes to a topic
        using the interface_handler and returns the created adapter. It handles
        errors while creating or retrieving topics and ensures the adapter is
        activated after subscription.

        Args:
            property_name (str): Used to create an object adapter with a specific
                name from Ice's ObjectAdapter class. The name of the topic, after
                removing 'Topic' prefix, is also set as `topic_name`.
            interface_handler (Ice.Object): Passed to the add method of the created
                object adapter. It represents the actual implementation of an
                interface provided by the object that will be proxied through the
                adapter.

        Returns:
            ObjectAdapter: Created using `self.ice_connector.createObjectAdapter(property_name)`.

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
    """
    Creates an object adapter from a property name and interface handler, adds the
    handler to the adapter with a specified identity, and activates the adapter.
    It is used for implementing interfaces on objects using ICE (Internet
    Communications Engine).

    Attributes:
        ice_connector (object): Initialized during the constructor call with a
            specific value, which is expected to be of type `Ice.Connection`. This
            attribute provides functionality for creating Ice objects adapters.

    """
    def __init__(self, ice_connector, default_handler):
        self.ice_connector = ice_connector

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an object adapter using a specified property name and interface
        handler, adds the interface handler to the adapter with a specific identity
        based on the property name, and activates the adapter.

        Args:
            property_name (str): Used to create an object adapter with the specified
                name using the ice_connector.createObjectAdapter method. The
                property name is converted to lowercase before being used as the
                identity for the adapter.
            interface_handler (Any): Required. It represents an instance of the
                interface that needs to be adapted.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    """
    Initializes an Ice configuration file and establishes connections to a Topic
    Manager and other components. It manages proxies, publishes topics, subscribes
    to topics, and provides methods for setting default handlers and destroying
    the connection.

    Attributes:
        ice_config_file (str): Initialized during object creation, representing
            the path to a configuration file for ICE (Internet Communications
            Engine). It is used to initialize the ICE connector and topic manager.
        ice_connector (Iceobject): Initialized with the result of a call to
            `Ice.initialize(self.ice_config_file)` in the constructor.
        topic_manager (IceStormTopicManagerPrx|None): Initialized by calling the
            `init_topic_manager` method if a specific property "TopicManager.Proxy"
            exists in the ice config file, or None otherwise.
        init_topic_manager (methodTopicManagerPrx): Used to initialize a topic manager.
        status (int): 0 by default, indicating its initial state. The purpose or
            meaning of this attribute is unclear from the provided code snippet.
        parameters (Dict[str,str]): Initialized by iterating through the properties
            provided by the Ice connector in the constructor. It stores the property
            names as keys and their corresponding values as values.
        requires (Requires): Initialized with a call to its constructor, passing
            the `self.ice_connector` as an argument. It appears to be used for
            managing proxies related to required interfaces.
        publishes (Publishes|None): Initialized with an instance of class Publishes
            when the InterfaceManager object is created. It handles publishing to
            topics using IceStorm.
        implements (Implements|None): Set to a new instance of Implements when
            `set_default_handler` method is called. It represents the interface
            that this object implements.
        subscribes (Subscribes|None): Initialized by calling the `set_default_handler`
            method, which initializes it with a Subscribes object for subscribing
            to topics managed by IceStorm's Topic Manager.

    """
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an instance by setting its properties, connecting to Ice, and
        creating instances of other classes based on the configuration file provided.

        Args:
            ice_config_file (str): Used to initialize Ice, which is an open-source,
                cross-platform middleware infrastructure for building distributed
                systems. It specifies the configuration file for the Ice application.

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
        Initializes and checks the connection to a TopicManager proxy from an
        IceStorm service. If the connection fails, it logs an error message and
        exits with a status code -1.

        Returns:
            IceStormTopicManagerPrx: A proxy object that represents a Topic Manager,
            an interface to manage topics for publishing and subscribing messages.

        """
        proxy = self.ice_connector.getProperties().getProperty("TopicManager.Proxy")
        obj = self.ice_connector.stringToProxy(proxy)
        try:
            return IceStorm.TopicManagerPrx.checkedCast(obj)
        except Ice.ConnectionRefusedException as e:
            console.log(Text('Cannot connect to rcnode! This must be running to use pub/sub.', 'red'))
            exit(-1)

    def set_default_hanlder(self, handler):
        """
        Sets up two objects: Implements and Subscribes. The Implements object
        initializes with the ICE connector and a handler, while the Subscribes
        object is initialized with the ICE connector, topic manager, and the same
        handler.

        Args:
            handler (Any): Used to set default handlers for implementing interfaces.
                It is passed to the constructors of `Implements` and `Subscribes`
                classes to associate it with instances of these classes.

        """
        self.implements = Implements(self.ice_connector, handler)
        self.subscribes = Subscribes(self.ice_connector, self.topic_manager, handler)

    def get_proxies_map(self):
        """
        Aggregates two proxy maps: one from `self.requires` and another from
        `self.publishes`, then returns the merged map.

        Returns:
            Dict[Any,Any]: A mapping object that returns a proxy map by combining
            the results of calling `get_proxies_map` on `self.requires` and `self.publishes`.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        """
        Destroys an ICE (Interactive Connectivity Establishment) connector object
        if it exists, effectively releasing any system resources associated with
        it and terminating its functionality.

        """
        if self.ice_connector:
            self.ice_connector.destroy()





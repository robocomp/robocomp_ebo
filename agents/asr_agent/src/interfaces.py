import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()


Ice.loadSlice("-I ./src/ --all ./src/ASR.ice")
import RoboCompASR

class audioVector(list):
    def __init__(self, iterable=list()):
        super(audioVector, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, int)
        super(audioVector, self).append(item)

    def extend(self, iterable):
        """
        Takes an iterable and checks that each item is an instance of `int`. Then
        it calls the superclass's `extend` method with the same iterable.

        Args:
            iterable (int): list of integers to be checked for type and then
                appended to the object's extension via `super().extend()`.

        """
        for item in iterable:
            assert isinstance(item, int)
        super(audioVector, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, int)
        super(audioVector, self).insert(index, item)

setattr(RoboCompASR, "audioVector", audioVector)




class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Sets properties and an instance variable for a class.

        Args:
            ice_connector (`ICEConnector` object.): ices connector, which is used
                to establish connections between components and services within
                the given system.
                
                		- `self.ice_connector`: This attribute holds the `IceConnector`
                instance that serves as an interface between the application and
                the ice service. It is a subclass of `types.Optional[IceConnector]`.
                		- `self.mprx`: This attribute stores the `MultiPoint RobertsXPrototiles`
                instance, which represents the XML configuration file for the ice
                service. Its type is `optional[MultiPoint RobertsXPrototiles]`.
                		- `self.topic_manager`: This attribute refers to an instance of
                the `TopicManager` class, which manages the topics associated with
                the ice service. Its type is `optional[TopicManager]`.
            topic_manager (`TopicManager` object.): TopicManager object that manages
                the topics associated with the IceConnector instance being initialized.
                
                		- `mprx`: A dictionary containing the message proxies for each
                topic in the manager.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic or retrieves an existing one based on its name, and
        returns a publisher object for it.

        Args:
            topic_name (ice_id.): name of the topic to be retrieved or created in
                the function.
                
                		- `topic_name`: A string that represents the name of the topic
                to be created.
                
                	The `try-except` block inside the `create_topic` function is used
                to handle errors and exceptions that may occur while retrieving
                or creating a topic. The `iceStorm.NoSuchTopic` exception indicates
                that another client has already created the topic with the given
                name, while the other exceptions are handled by attempting to
                create a new topic if possible.
                
                	The `pub = topic.getPublisher().ice_oneway()` line retrieves the
                publisher object of the topic, which is an IceStorm.Publisher
                interface. This object provides one-way communication with the
                topic, and its `ice_oneway()` method creates a proxy that can be
                used to interact with the topic.
                
                	The `proxy = ice_proxy.uncheckedCast(pub)` line casts the publisher
                object to an IceStorm.Publisher proxy, which can be used to send
                messages to the topic. The `uncheckedCast` method is used to bypass
                type checks and casting errors that may occur when interacting
                with the proxy.
                
                	Finally, the `self.mprx[topic_name] = proxy` line assigns the
                proxy object to a dictionary keyed by the topic name, allowing it
                to be retrieved later for use in message communication.
            ice_proxy (icedriver.OneWayPublisher reference.): icy published object
                as an unchecked IceProxy, which allows it to be directly returned
                as a Python proxy without additional validation or castings.
                
                		- `uncheckedCast(pub)`: This method returns an `ice_proxy` object,
                which represents a proxy for a publisher (`pub`). The `ice_proxy`
                class is part of the Ice programming framework and provides a
                mechanism for communicating between different language implementations
                of Ice.
                		- `ice_oneway()`: This method creates a new instance of the
                `ice::oneway` servant, which is a proxy that allows one-way
                communication (i.e., sending data without receiving any data in
                response). The resulting `ice_oneway` object is stored in the
                `self.mprx` dictionary, along with the `pub` publisher it represents.

        Returns:
            ice.proxy.ObjectAdapter: an IcePronox object representing a topic for
            which a publisher cannot be created.
            
            		- `pub`: The publisher instance that was created for the specified
            topic name. It is an ice::oneway_cast object and can be used to send
            messages to the topic.
            		- `proxy`: The proxy instance that was created for the specified
            topic name. It is an ice::unchecked_cast object and can be used to
            receive messages from the topic.
            
            	Note that the `create_topic` function returns a proxy object, which
            is a placeholder for the actual publisher or subscriber instances that
            will be created when the client connects to the topic. The returned
            proxy object provides an interface to the topic without actually
            creating the necessary instances.

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
        """
        Sets up instance variables `ice_connector`, `mprx`, and `ASR` as a proxy
        object, providing access to the RoboCompASR ASR component through the
        `ASRPrx` interface.

        Args:
            ice_connector (IceConnector object.): IceConnector interface, which
                is used to provide access to the RoboComp framework's Ice services.
                
                	1/ `self.ice_connector`: This is a Python Ice Client connector
                object that can be used to communicate with RoboCompASR components
                using the Interprocess Communication (IPC) protocol.
                	2/ `self.mprx`: This is a dictionary-like container for the
                RoboCompASR's MultiProxy interface, which enables communication
                between different ASR components running in different processes.
                The contents of this container are not specified in the input.

        """
        self.ice_connector = ice_connector
        self.mprx={}

        self.ASR = self.create_proxy("ASRProxy", RoboCompASR.ASRPrx)

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Generates high-quality documentation for code given to it and creates a
        proxy for an object, using the Ice framework library. It takes a property
        name as input and returns a Boolean value indicating whether the proxy was
        successfully created, along with the proxy itself.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (`ice.Proxy` object.): icy proxy object that is returned by
                the `uncheckedCast()` method when converting a string representation
                of a remote object to a Python object.
                
                		- `uncheckedCast`: This is a method of the `Ice.ObjectProxy`
                class that converts an object proxy into another type of proxy.
                It is used to convert the `base_prx` into an instance of `CameraSimple`.
                		- `stringToProxy`: This is a method of the `Ice.ObjectPrx` class
                that converts a string representation of an object proxy into a
                real object proxy. It is used to convert the `proxy_string` into
                an actual object proxy.
                		- `mprx`: This is a dictionary that maps property names to their
                corresponding proxies. It is updated in the function with the value
                of `proxy`.

        Returns:
            IcePy.Proxy` object: a tuple of two values: `True`, which indicates
            success, and the proxy object for the requested property.
            
            		- `True, proxy`: The return value of the `create_proxy` function
            when a successful connection is established to the remote object. The
            `True` value indicates that the operation was successful, and the
            `proxy` value represents the proxy instance created to interact with
            the remote object.
            		- `False, None`: The return value of the `create_proxy` function
            when an error occurs during the connection process. The `False` value
            indicates that the operation was not successful, and the `None` value
            represents the error message or exception that occurred during the operation.

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
        Creates an Ice object adapter for a given property name and adds an ice
        oneway handler to subscribe to a topic with the specified name.

        Args:
            property_name (str): name of a property that will be used to create a
                topic in the topic manager.
            interface_handler (Ice.ObjectReference.): icy handler to which the
                adapter's oneway proxy should be added.
                
                		- `self.ice_connector`: This is an instance of the `IceConnector`
                class, which provides a mechanism for interacting with the Interop
                Communicator (IAC).
                		- `property_name`: This is a string that represents the name of
                the property that is being used to create the adapter.
                		- `topic_name`: This is a string that represents the name of the
                topic that is being created in the function. It is generated by
                replacing the `Topic` prefix with an empty string.
                		- `handler`: This is an instance of the `InterfaceHandler` class,
                which provides a way to interact with the IAC-based communication
                system.
                		- `subscribe_done`: This is a boolean variable that indicates
                whether the topic has already been subscribed to successfully or
                not. It is initialized to `False`.
                		- `qos`: This is an instance of the `QoS` class, which represents
                the quality of service (QoS) settings for the topic. It is generated
                by default when the topic is created.
                
                	In summary, `interface_handler` contains properties and attributes
                related to the IAC-based communication system, such as the Interop
                Communicator and the QoS settings for a topic.

        Returns:
            ice.Adapter` object: an activated Ice adapter with a published topic
            and subscription QoS parameters.
            
            		- `adapter`: The adapter object created to adapt the Ice protocol
            to the specified topic name.
            		- `handler`: The interface handler associated with the adapter.
            		- `proxy`: The proxy object created to enable one-way communication
            between the client and server.
            		- `topic_name`: The name of the topic adapted by the adapter.
            		- `qos`: An optional QoS (Quality of Service) dictionary that specifies
            the required quality of service for the subscription.
            		- `subscribe_done`: A boolean value indicating whether the topic
            exists or not, set to `True` if the topic is created successfully and
            `False` otherwise.
            
            	In addition to these properties, the `create_adapter` function takes
            several positional arguments, including `property_name`, which specifies
            the name of the property that holds the topic name to adapt. The
            function also takes an optional ` Ice.Exception` argument for handling
            exceptions related to topic creation.

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
        Creates a new adaptor and adds an interface handler to it using the `add`
        method. It also activates the adapter using the `activate` method.

        Args:
            property_name (str): property name that the `createObjectAdapter`
                method will create an adapter for.
            interface_handler (str): icedriver interface that is added to the
                adapter created by the `createObjectAdapter()` method.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Sets up the necessary objects and data structures to interact with an Ice
        transport layer, including a `TopicManager`, a `Requires` object, a
        `Publishes` object, and initializes the `self.parameters` dictionary.

        Args:
            ice_config_file (str): icy-config file containing information about
                the ICE connection, which is used to initialize and configure the
                Ice connector instance in the function.

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
        Takes a string containing the proxy settings for the Topic Manager and
        converts it into an IceStorm.TopicManagerPrx object, which is then checked
        against Ice.ConnectionRefusedException to verify if the connection is
        successful. If there's any problem with the connection, the function prints
        an error message and exits with a negative value.

        Returns:
            IceStorm.TopicManagerPrx: an IceStorm.TopicManagerPrx object, which
            represents a topic manager proxy.
            
            		- `TopicManagerPrx`: This is an interface provided by IceStorm to
            interact with the Topic Manager. It can be used to create and manage
            topics, as well as subscribe and unsubscribe from them.
            		- `Ice.ConnectionRefusedException`: This exception is thrown if the
            connection to the Topic Manager is refused. This can occur if the Topic
            Manager is not running or if there are network connectivity issues.

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
        Updates a result object with the proxies map from both `requires` and `publishes`.

        Returns:
            object named `result`, which can be further manipulated or transformed
            as needed: a dictionary containing proxy information for both required
            and published services.
            
            	The result object is initialized as an empty dictionary (`{}`).
            
            	The method `update()` is called on the result object, which takes two
            arguments: the first is the output of the `requires.get_proxies_map()`
            function, and the second is the output of the `publishes.get_proxies_map()`
            function. These functions return a dictionary with the proxies information
            for each module or component in the system, keyed by their respective
            names. By calling `update()` on the result object with these two
            arguments, any values in the dictionaries that correspond to the same
            name are merged into a single dictionary.
            
            	The `get_proxies_map` function thus consolidates the proxies information
            for all modules and components in the system into a single dictionary
            that can be used to retrieve the necessary proxies configuration for
            any component or module in the system.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()







class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Sets instance attributes for an `ICEConnector` object and a `TopicManager`
        object, preparing the system to handle IoT device data topics.

        Args:
            ice_connector (object/instance.): iced connector object that is used
                to establish and manage communication connections with external
                clients through the Interceptor Client Interface (ICI) protocol.
                
                	1/ `ice_connector`: This is the initialized IceConnector instance.
                Its exact properties and attributes can be obtained by referencing
                its documentation or examining its source code.
            topic_manager (object of class `TopicManager`.): TopicManager class
                instance that manages the topics and services of the system,
                providing access to their respective states and methods for
                controlling and querying them.
                
                		- `topic_manager`: This is an instance of the `TopicManager`
                class. It contains various attributes and methods related to
                handling and processing IoT messages.
                		- `__self__`: This is a reference to the current object, which
                is a `Self` instance in this case.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic and returns its publisher as an IcePublisher proxy,
        or returns an existing publisher if a matching topic already exists.

        Args:
            topic_name (str): name of a topic that is retrieved or created by the
                function, and is used to retrieve or create a publisher object for
                the topic.
            ice_proxy (`Ice::Object` or its derived classes.): iced-client publisher
                as an unchecked ICE proxy, allowing it to be used as the topic
                publisher in the function.
                
                		- `uncheckedCast(pub)`: This is a method that converts the
                `IceStorm.TopicPublisher` object to an unchecked cast `Ice.Object`
                proxy. This conversion is done without checking for compatibility
                issues, which means it can lead to potential data loss or errors
                if the input is not of the expected type.
                		- `getPublisher()`: This method returns the `IceStorm.TopicPublisher`
                object that is associated with the topic name passed as an argument.
                The publisher is the component responsible for delivering messages
                to a topic.

        Returns:
            IceProxy object: an Ice Proxy object for a specified topic.
            
            		- `pub`: A reference to the publisher object, which can be used to
            send messages to the topic.
            		- `proxy`: An ice proxy object that represents the publisher object
            and provides a way for other clients to access it.
            		- `topic_name`: The name of the topic that was created.
            
            	The `create_topic` function creates a new topic with the given name
            if it does not already exist. If the topic already exists, the function
            returns a proxy object that represents the existing publisher. The
            function also sets the `mprx` dictionary with the newly created topic
            and its publisher.

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
        1) retrieves a property name from the Ice.Connector instance self.ice_connector
        using the `getProperties().getProperty()` method; 2) converts the property
        value from a string to an ICE Proxy object through `self.ice_connector.stringToProxy()`,
        and then 3) stores the resulting Proxy in the mprx dictionary for future
        access.

        Args:
            property_name ("PropertyName" in this function.): name of the property
                to retrieve from the remote object.
                
                		- `self.ice_connector.getProperties().getProperty(property_name)`:
                This method retrieves the value of a property with the specified
                name from the Ice container. The property name is passed as an
                argument to this method.
                		- `base_prx = self.ice_connector.stringToProxy(proxy_string)`:
                This method converts a string representing a proxy into an
                Ice.EntityPrx object. The string parameter is passed from the
                previous line, and it contains the serialized proxy data.
                		- `proxy = ice_proxy.uncheckedCast(base_prx)`: This method casts
                the returned Ice.EntityPrx object to an instance of the `ice_proxy`
                module's `UncheckedCastPrx` class. This allows the property to be
                accessed directly as a Python proxy object.
                		- `self.mprx[property_name] = proxy`: This line assigns the newly
                created proxy object to the `mprx` dictionary with the key being
                the name of the property.
                
                	The function returns two values: `True, proxy`. The first value
                indicates that the operation was successful, while the second value
                is the created proxy object.
            ice_proxy (icedefault(Proxy).): Ice Proxy object that will be used to
                unmarshal the remote object's property value.
                
                		- `uncheckedCast`: This attribute is used to uncheck the casting
                of the base proxy to the desired proxy type. It is a Python method
                that converts the base proxy into the target proxy type without
                raising an exception if the cast fails.
                		- `stringToProxy`: This method creates a proxy from a string
                representation of a remote object. The method takes the string
                representation of the remote object and returns a `BasePrx` object,
                which can be further converted to a specific type of proxy using
                the `uncheckedCast` method.

        Returns:
            None: a tuple of two values: a boolean indicator of whether the proxy
            was successfully created, and the created proxy object.

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
        Creates an adapter object that can subscribe to a message topic using a
        specified property name. It retrieves the topic name from the given property
        name, creates the topic if it does not exist, subscribes to the topic with
        a quality of service (QoS) object, and activates the adapter.

        Args:
            property_name (str): name of the topic that should be subscribed to.
            interface_handler (int): icy handle for the interface that the function
                is handling, which is used to interact with the remote object.

        Returns:
            instance of an ICE adaptor with a specified name and handler, activated
            to receive messages from a specified topic: an Ice ADAPTER object.
            
            		- `adapter`: A reference to an object adapter instance created by
            the `self.ice_connector.createObjectAdapter()` method.
            		- `handler`: An interface handler instance passed as a parameter to
            the `addWithUUID()` method of the adapter.
            		- `proxy`: An ICE oneway proxy instance created by the `adapter.addWithUUID()`
            method, which proxies requests from the client to the server.
            		- `topic_name`: The name of the topic being subscribed to, derived
            from the `property_name` parameter passed in the function call.
            		- `subscribe_done`: A boolean value indicating whether the topic has
            been successfully subscribed to or not. It is set to `True` if the
            subscription was successful, and `False` otherwise.
            		- `qos`: A dictionary of QoS settings for the topic subscription,
            which are used to configure the delivery of messages from the server
            to the client.
            		- `adapter.activate()`: This method activates the adapter, allowing
            it to receive and process messages from the server.

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
        Creates a new object adapter using the `self.ice_connector.createObjectAdapter()`
        method, adds an interface handler to the adapter using the `add()` method,
        and activates the adapter using the `activate()` method.

        Args:
            property_name (`identity`.): property name of an object that is used
                to create and add an adapter to the object's interface, and to
                activate the adapter.
                
                		- `property_name`: The name of the property to create an adapter
                for.
                		- `interface_handler`: The interface handler associated with the
                property.
                		- `ice_connector`: A reference to the ICE connector object that
                manages communication between objects.
                		- `stringToIdentity`: A method used to convert a string to an
                identity value, which is an unique identifier used to identify
                objects in the system.
            interface_handler (str): Java class that will handle requests and
                events for the interface associated with the property name passed
                to the `createObjectAdapter()` method.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Sets up Ice documentation by initializing the Ice framework using an input
        configuration file, creates a `Requires` and `Publishes` instances, and
        defines the implements, subscribes and status members according to the
        received Ice message.

        Args:
            ice_config_file (file path.): file that contains configuration details
                for the Interceptors, Configure, and Topics modules.
                
                	1/ `self.ice_config_file`: This is a file object that contains
                the configuration information for the Ice framework. It is passed
                as an argument to the `__init__` function and is used to initialize
                the Ice framework.
                	2/ `self.ice_connector`: This is an instance of the `Ice.initialize()`
                method, which is called to initialize the Ice framework with the
                configuration file specified in `self.ice_config_file`. The
                `Ice.initialize()` method returns a `Connector` object, which is
                stored in `self.ice_connector`.
                	3/ `needs_rcnode`: This is a boolean variable that indicates
                whether the topic manager should be initialized with an RCN node.
                If set to `True`, the `init_topic_manager()` function will be
                called to initialize the topic manager. Otherwise, the
                `init_topic_manager()` function is skipped and `None` is stored
                in `self.topic_manager`.
                	4/ `self.topic_manager`: This is an instance of the `TopicManager`
                class, which is optional. If `needs_rcnode` is `True`, then this
                variable will be initialized with an RCN node. Otherwise, it will
                be set to `None`. The `TopicManager` class is responsible for
                managing the topics associated with the Ice framework.
                	5/ `self.parameters`: This is a dictionary that contains the
                properties of the Ice configuration file. For each property, the
                key is a string representing the property name, and the value is
                the value of the property. The properties are obtained from the
                `Ice.getProperties()` method and are stored in this dictionary.
                	6/ `self.requires`: This is an instance of the `Requires` class,
                which represents the requires relationships between the topics
                associated with the Ice framework. It is populated with the
                requirements from the configuration file using the `Ice.getProperties()`
                method.
                	7/ `self.publishes`: This is an instance of the `Publishes` class,
                which represents the publishes relationships between the topics
                associated with the Ice framework. It is populated with the publishes
                information from the configuration file using the `Ice.getProperties()`
                method, and the topic manager is updated with the appropriate
                publishes information.
                	8/ `self.implements`: This is a boolean variable that indicates
                whether the Ice framework implements any topics. If set to `True`,
                then the `implements` property is not empty and contains the
                implemented topics. Otherwise, it is set to `None`.
                	9/ `self.subscribes`: This is a boolean variable that indicates
                whether the Ice framework subscribes to any topics. If set to
                `True`, then the `subscribes` property is not empty and contains
                the subscribed topics. Otherwise, it is set to `None`.

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
        Obtains a Proxy object from the TopicManager.Proxy property and converts
        it to an IceStorm.TopicManagerPrx instance using the `stringToProxy` method.
        It then attempts to check-cast the resulting object to an IceStorm.TopicManagerPrx
        instance, which if successful returns the topic manager.

        Returns:
            IceStorm.TopicManagerPrx object: an IceStorm TopicManager Proxy object.
            
            		- `IceStorm.TopicManagerPrx`: This is the Proxy object representing
            the Topic Manager interface. It is obtained through the `checkedCast()`
            method to ensure the correct type is returned.

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
        Updates the `result` dictionary with the proxies maps obtained from the
        `requires` and `publishes` attributes, respectively.

        Returns:
            object: a dictionary that combines the proxies maps of the `requires`
            and `publishes` attributes.
            
            	The `result` variable is initialized as an empty dictionary (`{}`).
            	The function then updates the `result` dictionary with the contents
            of the `requires` and `publishes` dictionaries' `get_proxies_map()`
            methods. This means that the values in `result` now contain information
            about the proxies required or published by various components in the
            system.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





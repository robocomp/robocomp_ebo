import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()


Ice.loadSlice("-I ./src/ --all ./src/LLM.ice")
import RoboCompLLM


import llmI



class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Sets `self.ice_connector` to a reference to an IceConnector object and
        initializes `self.mprx` and `self.topic_manager`.

        Args:
            ice_connector (object.): icy interface connector for the function,
                allowing for the manipulation of the topic manager and MPRX objects.
                
                	1/ `self.ice_connector`: The `ice_connector` object is stored in
                the instance variable `self.ice_connector`. Its properties can be
                accessed using the dot notation.
                	2/ `self.mprx`: An empty dictionary called `self.mprx` is defined.
                It stores no values yet and will likely hold data related to the
                topic manager in future methods.
                	3/ `self.topic_manager`: The instance of the `TopicManager` class,
                denoted by `self.topic_manager`, is created and stored as an
                attribute of the current object instance.
            topic_manager (object.): iceservices manager that can be used to manage
                topics in the system.
                
                		- `self.mprx`: A dictionary containing the managed producers'
                references for publishing messages to various topics.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic or retrieves an existing one based on its name, and
        returns the publisher's proxy for use with the rest of the code.

        Args:
            topic_name (str): name of a topic that the function is designed to
                retrieve or create.
            ice_proxy (`object` or `IceProxy` object.): iced Python proxy for a
                publisher, which is used to convert the Python publisher into an
                ice-compliant publisher.
                
                		- `uncheckedCast`: This is an Ice proxy, which can be used to
                call method(s) on the object without checking for method invocation
                errors.
                		- `getPublisher`: This returns the publisher associated with the
                topic.

        Returns:
            ice.proxy.ObjectPrx: a published IcePrx object reference for the
            specified topic name.
            
            		- `pub`: The publisher interface of the created topic. It is an
            Ice::ObjectPrx instance and provides one-way communication support.
            		- `proxy`: The proxy instance of the publisher interface, which is
            an unchecked cast result of `ice_proxy.uncheckedCast`. This serves as
            a reference to the published object through the topic.
            		- `mprx`: A dict-like variable that stores references to all the
            published objects, with each key being the name of the topic and the
            value being a proxy instance of the corresponding publisher interface.

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
        Generates high-quality documentation for given code by: (1) retrieving a
        property value from an IceoryptConnector object, (2) creating a Proxy
        object from the retrieved value, and (3) assigning the Proxy to a dictionary
        for later use.

        Args:
            property_name (str): name of the property to retrieve from the remote
                object.
            ice_proxy (`IceProxy` object.): icedoprocessed proxy object returned
                by the `stringToProxy()` method of the Ice connector.
                
                		- `uncheckedCast`: This is an unchecked cast operation that
                converts the `base_prx` object into a proxy object.
                		- `mprx`: A dictionary-like object where the property names are
                mapped to their corresponding proxy objects.
                		- `self`: Referencing the `CameraSimple` class instance.

        Returns:
            Optional[Any: a tuple containing either a valid proxy object or an
            error message.
            
            		- `True, proxy`: The function returns `True` if the creation of the
            proxy was successful, and the `proxy` variable contains the created
            proxy object. Otherwise, it returns `False` and sets the `proxy`
            variable to `None`.
            		- `proxy`: The variable `proxy` is set to the created proxy object
            when the function succeeds, or to `None` when the function fails. The
            type of `proxy` is `ice_proxy.UncheckedCastable`, which is an subclass
            of `IceProxy`.
            		- `property_name`: This variable is passed as an argument to the
            function and represents the property name for which a proxy is being
            created.

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
        Creates an ICE (Intermediate Code Execution) adapter and a PROXY handler
        for a specified property name. It also subscribes to a topic with a specific
        QoS (Quality of Service) policy and activates the adapter.

        Args:
            property_name (str): name of a property that specifies the topic name
                to subscribe to.
            interface_handler (int): icedriver handler that is associated with the
                Topic to be subscribed.

        Returns:
            instance of an `Adapter: an activated Iceoryx adapter object.
            
            		- `adapter`: This is the adapter instance that was created, which
            can be used to handle messages for the given topic name.
            		- `handler`: This is the interface handler that was passed to the
            `addWithUUID` method to create the adapter.
            		- `proxy`: This is the proxy instance that was created by adding the
            interface handler to the adapter using the `ice_oneway` method.
            		- `topic_name`: This is the name of the topic that was passed as a
            parameter to the function, which is used to create the publisher for
            the adapter.
            		- `qos`: This is an empty dictionary, indicating that no QoS settings
            were provided when subscribing to the topic.
            		- `status`: This is a variable that holds the status of the adapter
            creation, which is set to 0 in case of any error.

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
        self.llm = self.create_adapter("LLM", llmI.LLMI(default_handler))

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an object adapter based on a property name and adds an interface
        handler to it. It also activates the adapter using the `activate` method.

        Args:
            property_name (str): name of an ice properties property that is used
                to store the identity of an interface handler for communication
                between the adapter and the rest of the application.
            interface_handler (`identity` value.): identity of the interface that
                is being connected to the adapter, and it is added to the adapter
                through the `add()` method.
                
                		- `self.ice_connector`: A reference to an object of class
                `ice.connector`, which provides a connection point for various ice
                (Interoperability Contracts for Electronic Business) services.
                		- `property_name`: The name of the property to be created as an
                adapter, passed as a string parameter.
                		- `stringToIdentity`: A method provided by the `ice_connector`
                class that converts a string to an identity.
                
                	In summary, `adapter = self.ice_connector.createObjectAdapter(property_name)`
                creates an adapter for a given property using the `ice_connector`
                object and the `stringToIdentity` method. The adapter is then
                activated with `adapter.activate()`.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an object's attributes based on its class and input parameters.
        It loads an Ice configuration file, creates an Ice connector instance,
        sets up a topic manager, sets properties, implements requirements, publishes
        topics, subscribes to topics, and sets the status of the object to 0.

        Args:
            ice_config_file (file.): icy file containing configuration information
                for the current component, which is used to initialize the Ice
                framework and set up the component's topic manager.
                
                	1/ `ice_connector`: This is an instance of the `IceConnector`
                class, which contains information about the communication between
                IceGrid and external clients.
                	2/ `topic_manager`: This is an instance of the `TopicManager`
                class, which manages the topics published by this module. If
                `needs_rcnode` is False, then `topic_manager` will be None.
                	3/ `status`: This is an integer value representing the current
                status of the IceGrid module. Its meaning is determined by the
                context in which it is used.
                	4/ `parameters`: This is a dictionary containing parameter values
                returned by `ice_connector.getProperties()`. Each key is a property
                name, and each value is the corresponding property value.
                	5/ `requires`: This is an instance of the `Requires` class, which
                represents the requirements for this module.
                	6/ `publishes`: This is an instance of the `Publishes` class,
                which represents the publications from this module.
                	7/ `implements`: This is a list of interfaces implemented by this
                module.
                	8/ `subscribes`: This is a list of interfaces subscribed to by
                this module.

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
        Obtains a Proxy object from the `TopicManager.Proxy` property, converts
        it to an IceStorm.TopicManagerPrx object using the `stringToProxy` method,
        and returns the converted object.

        Returns:
            IceStorm.TopicManagerPrx` object: an IceStorm TopicManagerPrx object.
            
            		- `TopicManagerPrx`: This is the Proxy object for the Topic Manager
            interface, which represents the management of pub/sub topics in IceStorm.
            		- `stringToProxy()`: This method is used to convert a string
            representation of an interface into its Proxy counterpart.
            		- `checkeCast()`: This method checks if the passed-in object is a
            valid instance of the Topic Manager interface, and returns it if it
            is. If it is not, it raises an `Ice.ConnectionRefusedException`.

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
        Updates a `result` object with the proxies maps of `requires` and `publishes`.

        Returns:
            object with two properties: update results from both `requires` and
            `publishes: a dictionary of proxy information for both required and
            published services.
            
            		- `result`: A dictionary containing the proxies maps for both required
            and published resources. The keys in the dictionary represent the
            resource names, while the values represent lists of proxies associated
            with each resource.
            		- `self.requires`: The attribute representing the set of required
            resources. It contains the list of resources that must be available
            for the component to function correctly.
            		- `self.publishes`: The attribute representing the set of published
            resources. It contains the list of resources that are exposed to other
            components or external entities.
            
            	By calling `update()` on the `result` dictionary with the output of
            `get_proxies_map()`, the proxies maps for both required and published
            resources are added to the dictionary, providing a comprehensive view
            of the available proxies for the component.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





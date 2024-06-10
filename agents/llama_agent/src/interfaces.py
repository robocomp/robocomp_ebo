import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()


Ice.loadSlice("-I ./src/ --all ./src/LLM.ice")
import RoboCompLLM





class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes an instance of `Self` by setting member variables: `ice_connector`,
        `mprx`, and `topic_manager`.

        Args:
            ice_connector (`object`.): 3rd party library used to handle Ice
                (Interoperability Contract for Electronic Communications) connectivity
                in the provided code.
                
                		- `self.ice_connector`: A `IceConnector` instance that represents
                the communication channel between the client and server. It provides
                various methods for establishing and managing the connection.
            topic_manager (`object`.): manager for managing topics in the communication
                framework, providing access to various functionalities related to
                topic management and messaging.
                
                		- `mprx`: This is a dictionary containing the MPrix objects that
                hold the topics' information.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Retrieves a topic from the topic manager, creates one if it doesn't exist,
        and returns an IcePy Publisher object that can be used to publish messages
        to the topic.

        Args:
            topic_name (str): name of the topic to be retrieved or created.
            ice_proxy (`ice.Reference` object.): icy publisher object that gets
                transformed into an unchecked cast publisher object, allowing it
                to be used as a regular publisher object in the Topic Manager.
                
                		- `uncheckedCast`: This is a property of the `ice_proxy` class
                that indicates whether or not the proxy should be checked for
                invalidity before being used. In this case, it is set to
                `uncheckedCast`, which means that the proxy will not be checked
                for invalidity before being used.
                		- `ice_oneway`: This is a property of the `pub` object that
                indicates whether or not the topic can only publish data but cannot
                subscribe to data from others. In this case, it is set to `ice_oneway`,
                which means that the topic can only publish data and not subscribe
                to data from others.
                		- `getPublisher`: This is a property of the `topic` object that
                returns the publisher for the topic. It is used in the function
                to retrieve the publisher for the topic.
                		- `topic_name`: This is a string that represents the name of the
                topic. It is used as the argument to the `retrieve` and `create`
                methods of the `topic_manager` object.

        Returns:
            IcePy.MPROXY` object: an ICE proxy for the given topic.
            
            		- `pub`: This is the publisher interface of the topic, which can be
            used to send messages to the topic. It is an ice_oneway() object,
            indicating that it allows one-way communication from sender to receiver
            without receiving any response.
            		- `proxy`: This is a proxy object that wraps the `pub` interface and
            provides additional functionality for working with the topic. It can
            be used to send messages to the topic, as well as to check if the topic
            has been created successfully or not.

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
        Sets up an instance of the `ice_connector` class, creates a proxy for the
        `LLMProxy` class and maps it to the RoboComp LLM object.

        Args:
            ice_connector (`ice_connector`.): iced connection handler for the Robot
                Operating System (ROS) communication between the LLM and other
                nodes or services.
                
                		- `self.ice_connector`: The deserialized input `ice_connector`,
                which is an instance of `RoboCompLLM`.
                		- `self.mprx`: An empty dictionary.

        """
        self.ice_connector = ice_connector
        self.mprx={}

        self.LLM = self.create_proxy("LLMProxy", RoboCompLLM.LLMPrx)

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Creates a proxy for a remote object based on its name and returns a tuple
        containing the successfully created proxy and a boolean value indicating
        whether the operation was successful.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (`Ice.Prx`.): icy proxy object that is generated from the
                Ice code and used to retrieve the property value.
                
                		- `uncheckedCast`: This is an Ice-specific attribute that indicates
                whether the method returns a wrapped proxy or not.
                		- `base_prx`: This is the base proxy returned by
                `self.ice_connector.stringToProxy()`, which can be any type of
                proxy (e.g., servant, reference, or value).
                		- `mprx`: This is an instance attribute that stores the retrieved
                remote object proxy for the specified property name.

        Returns:
            ice proxy object: a tuple of two values: a boolean value indicating
            whether the proxy was created successfully and the created proxy object.
            
            		- `True, proxy`: If the function succeeds in creating a proxy for
            the remote object, `True` is returned along with the proxy itself. The
            proxy can be used to access the remote object through the Ice client.
            		- `False, None`: If the function encounters an error while trying
            to create the proxy, `False` is returned along with `None`, indicating
            that the operation failed.
            
            	Inside the try-except block, the following properties/attributes of
            the output are explained:
            
            		- `proxy`: The proxy object created by the `create_proxy` function.
            This can be used to access the remote object through the Ice client.
            		- `base_prx`: The base proxy string returned by the
            `ice_connector.stringToProxy()` method.
            		- `mprx`: A dictionary that stores the created proxies for different
            remote objects. In this case, `mprx[property_name]` stores the proxy
            created for the remote object with the specified `property_name`.

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
        Creates an Ice object adapter based on a given property name, adds a handler
        to the adapter using oneway proxy, retrieves the topic based on the property
        name, and subscribes to the topic.

        Args:
            property_name (str): name of a property that holds the topic name to
                be created and subscribed to.
            interface_handler (int): handler for the created topic, which is used
                to receive and process messages from the topic.

        Returns:
            Adapter: an activated Iceoryx adapter instance.
            
            		- `adapter`: An instance of the `ICEConnector` adapter.
            		- `handler`: A reference to an interface handler object.
            		- `proxy`: An instance of the `ICEOneWay` proxy.
            		- `topic_name`: The name of the topic for which the adapter is created.
            		- `subscribe_done`: A boolean flag indicating whether the topic
            exists or not. It is set to `True` if the topic exists, and `False` otherwise.
            		- `qos`: An instance of the `QoS` class, containing information about
            the quality of service (QoS) settings for the topic.
            		- `adapter.activate()`: A call to activate the adapter, which makes
            it available for use in the application.

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
        Creates an Adaptor object for a given property name and adds an interface
        handler to it. Then, it activates the adaptor.

        Args:
            property_name (str): identity string for the object adapter being
                created, which is then added to the interface handler and activated.
            interface_handler (str): 10-tuples containing the interface for which
                an adaptor is being created.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an Ice container object, sets up a topic manager, retrieves
        property values from Ice, and creates `Requires`, `Publishes`, `Implements`,
        and `Subscribes` objects based on the retrieved properties.

        Args:
            ice_config_file (str): configuration file for the Ice framework, which
                is used to initialize and set up the necessary objects and properties
                for the rest of the function to work properly.

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
        Takes a property value representing a Proxy and converts it into an instance
        of `TopicManagerPrx`. If the connection to the proxy is refused, it logs
        an error message and exits with a negative status code.

        Returns:
            IceStorm.TopicManagerPrx` instance: an IceStorm TopicManager Prx object.
            
            		- `TopicManagerPrx`: This is the Proxy object representing the Topic
            Manager instance. It can be cast to an IceStorm.TopicManager Prx using
            `checkedCast()`.

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
        Updates the `result` dictionary with the union of `requires` and `publishes`
        proxies maps.

        Returns:
            object: a dictionary of proxies for both requires and publishes, keyed
            by endpoint.
            
            	The `result` dictionary contains proxies maps from both `requires`
            and `publishes`. These maps represent the mappings between original
            URLs and their corresponding proxied versions. The maps contain keys
            that correspond to the original URLs and values that represent the
            proxied URLs.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





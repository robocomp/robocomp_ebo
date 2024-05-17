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
        Verifies that each element in the `iterable` is an instance of `int`, then
        adds those elements to the object's internal list.

        Args:
            iterable (int): 2D audio vectors to be extended with the given method.

        """
        for item in iterable:
            assert isinstance(item, int)
        super(audioVector, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, int)
        super(audioVector, self).insert(index, item)

setattr(RoboCompASR, "audioVector", audioVector)

import asrI



class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes the `IceConnector` instance by setting the `ice_connector`
        attribute and creating an empty `mprx` dictionary. It also sets the
        `topic_manager` attribute to a provided `topic_manager` instance.

        Args:
            ice_connector (`ICEConnector`.): icy (Intermediate C++ Representation)
                connector, which is used to convert the code's output into an
                intermediate representation.
                
                	1/ `ice_connector`: This is an instance of the `ice_connector`
                class, which contains various attributes related to the connection
                and management of the Icehouse topic manager.
                	2/ `mprx`: A dictionary containing the mapping of Icehouse topic
                names to their corresponding message producers.
            topic_manager (object of class `TopicManager`.): topic manager of the
                ROS bag, which manages the publication and subscription of topics
                in the ROS system.
                
                		- `mprx`: A dictionary containing the manager for each profile
                registered in the topic manager.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic or retrieves an existing one based on its name, and
        then returns a publisher object for the topic.

        Args:
            topic_name (str): name of the topic to be retrieved or created in the
                IceStorm topic management system.
            ice_proxy (`IceProxy` object.): icy publisher that is being turned
                into an IceProxy object for one-way communication.
                
                		- `uncheckedCast`: This is an ice_proxy attribute that returns
                an unchecked Ice proxy for the published object.
                		- `pub`: This is an attribute of the ice_proxy object that
                references the publisher for the topic.

        Returns:
            ice.proxy.Publisher: a publisher object for the specified topic.
            
            		- `pub`: The publisher instance for the topic, which can be used to
            send messages to the topic.
            		- `proxy`: An ice_proxy instance that proxies the publisher instance,
            allowing other clients to connect to the topic without needing to
            authenticate with the original publisher.

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
        Creates an IcePy Proxy object based on a given string representation of a
        proxy and sets the resulting object as the value of a property in the
        CameraSimple module's mprx dictionary.

        Args:
            property_name (str): name of the property to retrieve from the remote
                object.
            ice_proxy (icy.exception.): Ice.Proxy object that is returned by the
                `stringToProxy()` method of the `Ice.Connection` object, which is
                used to wrap and return the remote object's proxy for further
                processing or interaction.
                
                		- `uncheckedCast`: This method is used to convert a serialized
                Proxy instance into an unchecked Proxy instance, without checking
                if the input is valid. It is useful when working with remotely
                accessible objects, as it allows for quick creation of Proxies
                without worrying about validation errors.
                		- `stringToProxy`: This method is used to convert a string
                representation of a Proxy instance into an actual Proxy object.
                It takes a string input and returns a valid Proxy instance upon
                successful conversion.

        Returns:
            ice.exception object: a tuple of two values: (True, proxy) if successful,
            or (False, None) otherwise.
            
            		- `True`: This indicates that the proxy was successfully created for
            the given property name.
            		- `proxy`: The actual proxy object obtained from the remote object.
            
            	In case an exception is thrown, the output is:
            
            		- `False`: This indicates that there was an error while creating the
            proxy.
            		- `None`: This represents the error message or traceback information
            related to the exception.

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
        Creates an adapter instance and adds a one-way proxy to it. It also checks
        for the existence of a topic with a specified name and subscribes to it
        if it doesn't exist, or creates it if it doesn't. Finally, it activates
        the adapter and returns it.

        Args:
            property_name (str): name of a property that the user wants to set as
                a topic name.
            interface_handler (`object`): icedriver.icing connection handler that
                is used to handle the ice proxy creation and activation for the
                specified topic.
                
                		- `property_name`: This is the name of the topic for which an
                adapter needs to be created.
                		- `interface_handler`: This is the instance of
                `iceoryx.interface_factory.InterfaceHandler` that contains the
                information about the interface and its properties.
                		- `topic_name`: This is the name of the topic that needs to be
                subscribed to. It is derived from the `property_name` by replacing
                the 'Topic' suffix with an empty string.
                		- `subscribe_done`: This variable keeps track of whether the
                subscription to the topic has been successfully completed or not.
                It is initially set to `False`.
                		- `qos`: This is a dictionary that holds the QoS (Quality of
                Service) settings for the topic subscription.
                
                	The `interface_handler` object has various properties and attributes
                that are used throughout the function, such as:
                
                		- `ice_connector`: This is the instance of `IceConnector` that
                provides a connection to the Iceoryx environment.
                		- `topic_manager`: This is the instance of `TopicManager` that
                manages the creation and subscription to topics in the Iceoryx environment.
                		- `qos_map`: This is a dictionary that maps the QoS settings for
                each topic.
                		- `interface_id`: This is the unique identifier of the interface
                that is being created.
                
                	By understanding these properties and attributes, the purpose of
                the `create_adapter` function can be fulfilled more effectively.

        Returns:
            ObjectAdapter: an Ice.Adapater object that can be used to communicate
            with a Topic.
            
            		- `adapter`: A Ice::Adapter object, which is created using the
            `self.ice_connector.createObjectAdapter()` method and passed as an
            argument to the function. This object represents a communication adapter
            that can be used for message passing between processes.
            		- `handler`: An Ice::InterfaceHandler object, which is obtained
            through the `interface_handler` parameter of the function. This object
            manages the interface of the adapter and provides methods for adding,
            removing, and retrieving interfaces.
            		- `proxy`: An Ice::ObjectProxy object that represents a connection
            to the remote object. This object is created using the `adapter.addWithUUID()`
            method and can be used for sending and receiving messages.
            		- `topic_name`: A string variable that contains the name of the topic
            for which the adapter is being created. This variable is used in the
            function to retrieve or create a topic from the TopicManager object.
            		- `subscribe_done`: A boolean variable that indicates whether the
            topic has been successfully subscribed to or not. This variable is set
            to true if the topic exists and false otherwise, indicating that the
            topic does not exist and it needs to be created.
            		- `qos`: A dictionary object that represents the QoS (Quality of
            Service) parameters for the topic subscription. These parameters
            determine how messages are routed and delivered in the system.
            		- `adapter.activate()`: This method is called at the end of the
            function to activate the adapter, which makes it ready for message passing.

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
        self.asr = self.create_adapter("ASR", asrI.ASRI(default_handler))

    def create_adapter(self, property_name, interface_handler):
        """
        Creates an adaptor for a specific property and adds it to the ice connector,
        then activates the adaptor to make it ready to use.

        Args:
            property_name (str): name of the property that the `ice_connector`
                will create an adapter for.
            interface_handler (str): Identity object of an interface to be added
                to the Adapter.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an Ice runtime configuration file, creates an Ice connector,
        and sets up a topic manager based on the configuration.

        Args:
            ice_config_file (str): configuration file for the Intermediate
                Representation (Ice) library, which is used to initialize the Ice
                connector and fetch the necessary information from the file.

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
        Ices.stringToProxy and checkedCast functions to create a Proxy instance
        from a given string representation. It also catches ConnectionRefusedExceptions
        and logs an error message before exiting with a negative status code.

        Returns:
            IceStorm TopicManager Prx object: an IceStorm.TopicManagerPrx object,
            which represents a proxy for accessing the topic manager service.
            
            		- `proxy`: A string representing the Proxy property of the TopicManagerPrx
            object.
            		- `obj`: An object that represents the TopicManagerPrx object, which
            can be checked cast to an IceStorm.TopicManagerPrx object if appropriate.

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
        Updates the `result` variable with proxies maps from both required and
        published sources.

        Returns:
            None: a dictionary that contains the union of the required and published
            proxies for a given module.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





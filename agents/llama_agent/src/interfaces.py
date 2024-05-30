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
        Sets attributes `self.ice_connector` and `self.mprx`, and assigns
        `topic_manager` to a attribute named `self.topic_manager`.

        Args:
            ice_connector (object.): icedTEA connector for the IceoryX framework,
                which is used to interact with external services through the IceoryX
                platform.
                
                	1/ `ice_connector`: A variable representing an instance of
                `IceConnector`. No further details are provided in the code snippet
                given.
                	2/ `mprx`: An empty dictionary (`{}`). Its purpose or properties
                are not discussed in the code snippet provided.
                	3/ `topic_manager`: An instance of `TopicManager`. No further
                information is available regarding its attributes or properties
                from the code snippet given.
            topic_manager (object.): TopicManager class instance that provides
                access to the managed topics.
                
                		- `self.mprx`: This attribute stores a dictionary containing all
                the message producers registered with the topic manager. It is an
                instance variable that cannot be changed after construction.
                		- `self.ice_connector`: This attribute stores the IceConnector
                object, which is used to connect to external services.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Creates a new topic or retrieves an existing one from the Topic Manager,
        and then creates an publisher object for that topic using IcePy's `ice_oneway`
        method. It then sets the topic name in the `mprx` dictionary for later use.

        Args:
            topic_name (icy.topic.TopicName object.): name of a topic for which
                an instance of its publisher is being requested, and it is used
                to retrieve or create a publisher instance for that topic.
                
                		- `topic_name`: This is the name of the topic to be created. It
                is a string attribute that represents the identifier of the topic.
                
                	Inside the `while` loop, the following checks are performed:
                
                	1/ If the `topic` variable is None, it means that the `topic_manager`
                could not find the requested topic with the specified name. The
                program will then try to create a new topic using the `create()`
                method.
                	2/ If an `IceStorm.NoSuchTopic` exception is caught, it means
                that another client has already created a topic with the same name.
                The program will then print a message indicating that another
                client has created the topic.
                	3/ In the third branch of the `while` loop, if the `create()`
                method throws an exception, it means that there was an error
                creating the new topic. The program will not handle this exception
                and will instead print a message.
                
                	Inside the `try`-`except` block, the following operations are performed:
                
                	1/ The `pub` variable is obtained from the `topic.getPublisher().ice_oneway()`
                method, which returns an `Ice::InputStream` proxy.
                	2/ The `proxy` variable is created by unchecked casting the `pub`
                variable using the `ice_proxy.uncheckedCast()` method. This creates
                a proxy that can be used to access the topic's publisher.
                	3/ The `mprx` dictionary is updated with the new topic proxy,
                where the key is the topic name and the value is the proxy object.
            ice_proxy (icedriver.Object.): iced tea publisher that is unchecked
                and cast into an ice proxy, allowing the resulting proxy to be
                stored in the `mprx` dictionary for later use.
                
                		- `uncheckedCast`: This property indicates that the input object
                is an IcePy proxy and should be cast unchecked to its underlying
                IceMessenger publication.

        Returns:
            Ice::Proxy: an Ice Proxy object that provides one-way communication
            with a topic.
            
            		- `pub`: The publisher for the topic, which is an Ice::OneWay proxy.
            		- `proxy`: An IceProxy object that wraps the publisher and allows
            unchecked casting to an Ice::Publisher instance.
            
            	Note that the function does not provide a summary at the end, as
            specified in the directives provided.

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
        Sets up objects for an ice connector and a proxy to the LLM's PRX.

        Args:
            ice_connector (`object`.): ICE connector, which is responsible for
                handling the interaction between the RoboComP and the external world.
                
                		- `self.ice_connector`: A variable assigned to hold the deserialized
                object `ice_connector`.

        """
        self.ice_connector = ice_connector
        self.mprx={}

        self.LLM = self.create_proxy("LLMProxy", RoboCompLLM.LLMPrx)

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Creates a Proxy object for a remote object specified by a string representation
        of its ice proxy. It returns a tuple of (success, proxy) indicating whether
        the creation was successful and the Proxy object created.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (IcePy Proxy.): iced Proxy object that will be returned if
                the property can be retrieved successfully, or the exception thrown
                if there is an error in retrieving the property.
                
                		- `uncheckedCast`: This is an unchecked conversion of the
                `base_prx` string to an `ice_proxy` object using the `stringToProxy`
                method. It returns a reference to the internal implementation of
                the proxy, without checking if it's valid or not. (source: `Ice.Exception`)
                		- `mprx`: A dictionary-like object that stores properties of the
                remote object as proxies. Each property name is associated with a
                proxy object, which can be obtained by calling the `getProperties`
                method on the `ice_connector` instance. (source: `self.mprx`)

        Returns:
            ice. proxy: a tuple of two values: `True`, indicating success, and the
            created proxy object.
            
            		- `True, proxy`: If the method call is successful, the output is
            `True` indicating that the proxy was created successfully, and `proxy`
            is the created proxy object.
            		- `False, None`: If the method call fails, the output is `False`,
            indicating that an error occurred during creation of the proxy, and
            `None` represents the exception thrown during creation.

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
        Creates a new Ice Python adapter object and adds an interface handler to
        it using one-way proxying. It also retrieves a topic by its name and
        subscribes to it if it exists, creating it otherwise. Finally, it returns
        the activated adapter object.

        Args:
            property_name (str): name of a property to be created as an Ice::Adapter
                object, which will be used to handle messages from a given topic.
            interface_handler (int): handler for an interface that will be created
                and managed by the adapter when adding it with the UUID returned
                by the `createObjectAdapter`.

        Returns:
            ObjectAdapter: an instance of an ICE adaptor with a given name and properties.
            
            		- `adapter`: The IceAdatper object created with the
            `ice_connector.createObjectAdapter` method.
            		- `handler`: The interface handler associated with the adapter.
            		- `proxy`: The IceOneway proxy added to the adapter using the
            `addWithUUID` method.
            		- `topic_name`: The name of the topic associated with the adapter,
            obtained by removing the "Topic" prefix from the property name passed
            as an argument.
            		- `subscribe_done`: A boolean value indicating whether the topic has
            been successfully subscribed to or not. If false, the function tries
            to create the topic again in a loop until it succeeds.
            		- `qos`: An empty dictionary (a default value is returned if none
            is provided as an argument) representing the QoS (quality of service)
            parameters for the subscription.
            		- `adapter.activate()`: A method call to activate the adapter.

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
        Creates a new object adapter based on the provided property name and adds
        an interface handler to it. It then activates the adapter using the Ice
        Connector's `activate()` method.

        Args:
            property_name (str): name of a property that is being set as the
                identity for an object adapter created by the function.
            interface_handler (str): identity of the interface that is to be
                accessed or communicated through the adapter, which is created and
                activated by the `self.ice_connector.createObjectAdapter()` method.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an Ice framework component by setting instance variables and
        calling method to interact with the Ice configuration file, connect to the
        Ice daemon, create a topic manager, set status, and retrieve property values.

        Args:
            ice_config_file (file path or URL.): iced configuration file used to
                initialize the Ice runtime environment and establish connections
                with the necessary endpoints.
                
                	1/ `self.ice_config_file`: This attribute stores the deserialized
                Ice configuration file contents.
                	2/ `self.ice_connector`: This attribute holds an instance of
                `Ice.initialize()` method call, which returns an object that manages
                communication between different objects in the system.
                	3/ `needs_rcnode`: This variable is set to `False` by default,
                indicating that no remote node is needed for initialization. If
                `True`, it means a remote node is required.
                	4/ `self.topic_manager`: This attribute refers to an object that
                manages topics and their related data in the system. It is created
                only if `needs_rcnode` is `True`.
                	5/ `self.status`: This attribute holds the current status of the
                Ice connection, which can be any integer value between 0 and 2.
                	6/ `self.parameters`: This attribute maps property names to their
                corresponding values received from the Ice configuration file.
                Each entry in the dictionary is a string representation of a
                property name followed by its value.
                	7/ `self.requires`: This attribute stores a list of dependent
                topics that are required for this topic to function correctly.
                	8/ `self.publishes`: This attribute lists the topics that this
                topic publishes data to.
                	9/ `self.implements`: This attribute holds the interfaces implemented
                by this topic.
                	10/ `self.subscribes`: This attribute represents the interfaces
                subscribed by this topic.

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
        Gets the Proxy value for Topic Manager from the properties and casts it
        to an IceStorm.TopicManagerPrx object. If the connection is refused, an
        error message is logged and the function exits with a negative status code.

        Returns:
            IceStorm.TopicManagerPrx` object: an instance of `TopicManagerPrx`.
            
            		- `proxy`: A string representing the proxy to be used for communication
            with the Topic Manager.
            		- `obj`: An object reference representing the Topic Manager proxy.

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
        Updates the `result` object with proxies maps obtained from both `requires`
        and `publishes` dependencies.

        Returns:
            dict: a dictionary containing the proxies required and published by
            the class instance.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





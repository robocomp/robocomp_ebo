import time
import Ice
import IceStorm
from rich.console import Console, Text
console = Console()


Ice.loadSlice("-I ./src/ --all ./src/EmotionalMotor.ice")
import RoboCompEmotionalMotor





class Publishes:
    def __init__(self, ice_connector, topic_manager):
        """
        Initializes variables for `self.ice_connector`, `self.mprx`, and `self.topic_manager`

        Args:
            ice_connector (object reference (a variable with some value).): icedte
                Lemon connector instance that the function is supposed to generate
                documentation for.
                
                		- `self.ice_connector`: A `IceConnector` instance representing
                the ROS node.
            topic_manager (object reference (i.e., a valid object instance or
                null).): 3rd party middleware manager for managing topics, which
                enables communication between different components of an application.
                
                		- `mprx`: A dictionary that contains information about the topic
                map, which is an association of strings to other strings.

        """
        self.ice_connector = ice_connector
        self.mprx={}
        self.topic_manager = topic_manager


    def create_topic(self, topic_name, ice_proxy):
        # Create a proxy to publish a AprilBasedLocalization topic
        """
        Retrieves or creates a topic from the topic manager based on the given
        name, and returns a publisher proxy for that topic.

        Args:
            topic_name (str): name of the topic to be retrieved or created by the
                function.
            ice_proxy (`IceProxy` object.): icy publisher object that gets cast
                to an unchecked ice proxy object.
                
                		- `ice_oneway()` - returns a publisher object for the topic
                		- `uncheckedCast()` - converts the `ice_proxy` to a proxy object
                for the publisher
                		- `getPublisher()` - retrieves the publisher from the topic

        Returns:
            ice_proxy: an IcePy proxy object for a published topic.
            
            		- `pub`: This is an instance of the `ice::oneway` class, which
            represents an ice publisher. It provides a way to send data from the
            client to the server.
            		- `proxy`: This is an instance of the `ice_proxy` class, which acts
            as a proxy between the client and the server. It allows the client to
            communicate with the server using the published object.
            		- `topic_name`: This is the name of the topic that was created by
            the function. It is used to identify the topic in the code and can be
            referenced later for further communication.

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
        Initializes a `RoboCompEmotionalMotor` object by setting instance variables:
        `ice_connector`, `mprx`, and `EmotionalMotor`. It also creates a Proxy for
        the `EmotionalMotor` interface.

        Args:
            ice_connector (`ICEConnectorPrx` object.): icy-Ros interface (Ice)
                connector, which is used to generate high-quality documentation
                for given code.
                
                		- `self.ice_connector`: A Python object that is a combination
                of Ice and Pyro technologies. It has several attributes that allow
                communication between the RoboComp environment and other systems.
                
                	These attributes include `RoboCompEmotionalMotorPrx`, which is a
                CORBA proxy class, and `mprx`, which is an empty dictionary with
                no values. The `mprx` dictionary may contain additional properties
                or attributes that are specific to the user's requirements.
                
                	Overall, the properties of `ice_connector` are designed to
                facilitate communication between the RoboComp environment and other
                systems using Pyro and Ice technologies.

        """
        self.ice_connector = ice_connector
        self.mprx={}

        self.EmotionalMotor = self.create_proxy("EmotionalMotorProxy", RoboCompEmotionalMotor.EmotionalMotorPrx)

    def get_proxies_map(self):
        return self.mprx

    def create_proxy(self, property_name, ice_proxy):
        # Remote object connection for
        """
        Takes a string representing an Ice Python object proxy and returns a tuple
        containing the successfully created proxy or `False` if there is an error
        during the creation process.

        Args:
            property_name (str): name of the property to be retrieved from the
                remote object.
            ice_proxy (iced (Input Proxy).): icy proxy object that is returned by
                `ice_connector.stringToProxy()` method and is used to store the
                received proxy object for further usage.
                
                		- `uncheckedCast`: This method returns an unchecked cast of the
                `base_prx` to the desired type `ice_proxy`. It is used to convert
                a proxy object of a different type to the desired type without any
                type safety checks.
                		- `stringToProxy`: This method converts a string representation
                of a proxy to an instance of the `ice_proxy` class. The input
                string may contain the full path of a remote object, or it may be
                a reference to an existing proxy object.
                		- `getProperties`: This method returns a dictionary containing
                the properties of the remote object. The properties are represented
                as key-value pairs, where the keys are the property names and the
                values are the corresponding property values.
                		- `getProperty`: This method returns a specific property value
                of the remote object. The input parameter is the name of the
                property to be retrieved.

        Returns:
            instance of `IceProxy`, which is an object that can be used to access
            remote object methods through a proxy connection: a tuple containing
            either a successfully created proxy or an error message indicating why
            the creation failed.
            
            		- `True`, `Proxy`: The function successfully created a proxy for the
            given property name.
            		- `False`, `None`: The function failed to create a proxy due to an
            error or invalid input.
            		- `proxy`: A proxy object that represents the remote object's property
            with the specified name.

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
        Creates a new instance of an object adapter using the given property name
        and adds a one-way ice proxy to the adapter. It then creates a topic with
        the same name as the property, subscribes to it, and returns the activated
        adapter.

        Args:
            property_name (str): name of the topic to which the code wants to
                subscribe, and it is used to generate the unique UUID for the
                publisher proxy and to create the corresponding Topic object in
                the Topic Manager.
            interface_handler (`Ice.ObjectProxy`.): handle for an interface that
                is being created and added to the adaptor.
                
                		- `self.ice_connector`: A reference to an IceConductor object
                that provides connectivity between the adapter and the Ice framework.
                		- `property_name`: The name of a property in the input message
                that defines the topic to be subscribed.
                		- `topic_name`: The name of the topic to be created or retrieved
                from the topic manager.
                		- `handler`: An instance of an interface handler, which defines
                how messages are processed by the adapter.
                		- `adapter`: A reference to the Adapter object that is being created.
                		- `qos`: An instance of a QoS object, which defines the quality
                of service for the subscription.
                
                	Note: In this function, the properties of `interface_handler` are
                not explicitly destructured, as they are used within the function
                without needing to be explicitly referenced.

        Returns:
            ice.adaptor.Adapter: an activated adapter object with a published topic.
            
            		- `adapter`: The adapted Ice client adapter instance.
            		- `handler`: The interface handler for which the adapter was created.
            		- `proxy`: The one-way Ice proxy instance created by the adapter.
            		- `topic_name`: The name of the topic to subscribe to, without the
            "Topic" prefix.
            		- `qos`: The quality of service (QoS) parameters for the subscription,
            which includes the QoS level, maximum message size, and maximum number
            of messages per second.
            
            	Note that the function does not provide a summary at the end, as
            instructed. Instead, each property or attribute is explained individually
            in the output.

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
        Creates a new adapter object and adds an interface handler to it. It then
        activates the adapter.

        Args:
            property_name (str): identity string that will be used to connect the
                interface to the correct endpoint.
            interface_handler (`Identity`.): ices_interfacetype_holder interface
                for which a adapter is being created.
                
                		- `self.ice_connector`: This is an instance of the
                `InteroperabilityConnector` class, which provides a mechanism for
                connecting and communicating between different systems or components.
                		- `property_name`: This is a string variable that represents the
                name of the property being manipulated or accessed.
                		- `add`: This method is used to add a new object to an adapter,
                typically for the purpose of interfacing with another system or
                component. In this case, `interface_handler` is being added to the
                adapter with a specific identity value.
                		- `activate`: This method is called to activate an adapter after
                it has been populated with objects or values. Activation allows
                the adapter to be used for communication or interaction between
                systems or components.

        """
        adapter = self.ice_connector.createObjectAdapter(property_name)
        adapter.add(interface_handler, self.ice_connector.stringToIdentity(property_name.lower()))
        adapter.activate()


class InterfaceManager:
    def __init__(self, ice_config_file):
        # TODO: Make ice connector singleton
        """
        Initializes an Ice configuration and sets up the topic manager, status,
        parameters, requires, publishes, implements, and subscribes based on the
        given ice_config_file and Ice connector.

        Args:
            ice_config_file (str): configuration file for Ice, which is used to
                initialize the Ice client and determine the properties and connections
                required for communication with the Ice server.

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
        Retrieves the TopicManager's proxy value and casts it to an IceStorm
        TopicManagerPrx object using `IceStorm.TopicManagerPrx.checkedCast`. If
        the connection to rcnode is refused, it logs an error message and exits
        with a status code -1.

        Returns:
            IceStorm.TopicManagerPrx object: an instance of the `TopicManagerPrx`
            interface, which represents a proxy object for the Topic Manager service.
            
            		- `IceStorm.TopicManagerPrx`: This is the proxy object returned by
            the `self.ice_connector.stringToProxy()` method. It represents the
            Topic Manager interface.
            		- ` checkedCast`: This is a type cast that returns an instance of
            the Topic Manager proxy.
            		- `Exit Code`: In case of an exception, this variable is used to
            print an error message and exit with a negative value.

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
        Updates `result`, a dict, with values from `requires` and `publishes`.

        Returns:
            object: a dictionary that contains the union of the `requires` and
            `publishes` proxies.
            
            	The `result` dictionary contains both the proxies defined by the
            `requires` and `publishes` modules. This indicates that the returned
            object is a union of the two modules' proxy maps.
            
            	The `update()` method in each module updates the object with its
            corresponding map, adding any new entries to the existing ones.
            
            	Overall, the returned output is a single, unified proxy map that
            includes proxies from both the `requires` and `publishes` modules.

        """
        result = {}
        result.update(self.requires.get_proxies_map())
        result.update(self.publishes.get_proxies_map())
        return result

    def destroy(self):
        if self.ice_connector:
            self.ice_connector.destroy()





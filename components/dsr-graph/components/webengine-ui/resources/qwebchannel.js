/****************************************************************************
 **
 ** Copyright (C) 2016 The Qt Company Ltd.
 ** Copyright (C) 2016 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com, author Milian Wolff <milian.wolff@kdab.com>
 ** Contact: https://www.qt.io/licensing/
 **
 ** This file is part of the QtWebChannel module of the Qt Toolkit.
 **
 ** $QT_BEGIN_LICENSE:LGPL$
 ** Commercial License Usage
 ** Licensees holding valid commercial Qt licenses may use this file in
 ** accordance with the commercial license agreement provided with the
 ** Software or, alternatively, in accordance with the terms contained in
 ** a written agreement between you and The Qt Company. For licensing terms
 ** and conditions see https://www.qt.io/terms-conditions. For further
 ** information use the contact form at https://www.qt.io/contact-us.
 **
 ** GNU Lesser General Public License Usage
 ** Alternatively, this file may be used under the terms of the GNU Lesser
 ** General Public License version 3 as published by the Free Software
 ** Foundation and appearing in the file LICENSE.LGPL3 included in the
 ** packaging of this file. Please review the following information to
 ** ensure the GNU Lesser General Public License version 3 requirements
 ** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
 **
 ** GNU General Public License Usage
 ** Alternatively, this file may be used under the terms of the GNU
 ** General Public License version 2.0 or (at your option) the GNU General
 ** Public license version 3 or any later version approved by the KDE Free
 ** Qt Foundation. The licenses are as published by the Free Software
 ** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
 ** included in the packaging of this file. Please review the following
 ** information to ensure the GNU General Public License requirements will
 ** be met: https://www.gnu.org/licenses/gpl-2.0.html and
 ** https://www.gnu.org/licenses/gpl-3.0.html.
 **
 ** $QT_END_LICENSE$
 **
 ****************************************************************************/

"use strict";

var QWebChannelMessageTypes = {
    signal: 1,
    propertyUpdate: 2,
    init: 3,
    idle: 4,
    debug: 5,
    invokeMethod: 6,
    connectToSignal: 7,
    disconnectFromSignal: 8,
    setProperty: 9,
    response: 10,
};

/**
 * @description Establishes a Web channel between a client and a server, handling
 * message passing between them. It defines an object with methods for sending/receiving
 * messages and properties.
 * 
 * @param { object } transport - transport object that is used to send messages between
 * the client and the server.
 * 
 * @param { `function`. } initCallback - initialization callback that is called with
 * the `channel` object as an argument after the necessary objects are created and
 * unwrapped properties are resolved, allowing the caller to perform any additional
 * setup or customization of the channel.
 * 
 * 		- `initCallback`: A callback function that is called after the QWebChannel's
 * initialization. It receives the channel object as its parameter and can be used
 * to perform any post-initialization tasks.
 * 
 * 	The `QWebChannel` class has several properties and methods to handle messages,
 * signals, responses, property updates, and debugging. The following are explained:
 * 
 * 		- `objects`: A hash table that maps object names to their respective QObject instances.
 * 		- `transport`: The transport object that is used to send and receive messages
 * over the channel.
 * 		- `send`: A method that sends a message to the channel. It takes a data payload
 * as its parameter, which can be a string or an JSON-serialized object.
 * 		- `onmessage`: A method that handles incoming messages on the channel. It takes
 * a message object as its parameter and processes it based on its type (signal,
 * response, property update, or debugging).
 * 		- `exec`: A method that executes a message callback function. It takes a data
 * payload as its parameter and schedules the callback function to be called with the
 * corresponding data parameter.
 * 		- `execCallbacks`: A hash table that maps message IDs to their respective callback
 * functions. These callbacks are called when a message is received on the channel.
 * 		- `objects`: A hash table that maps object names to their respective QObject instances.
 * 		- `handleSignal`: A method that handles incoming signals on the channel. It takes
 * a signal name and any argument objects as its parameters and calls the corresponding
 * signal emitted callback function.
 * 		- `handleResponse`: A method that handles incoming responses on the channel. It
 * takes a message ID and any response data as its parameters and calls the corresponding
 * response callback function.
 * 		- `handlePropertyUpdate`: A method that handles incoming property update messages
 * on the channel. It takes a hash table of signal IDs and any property updates as
 * its parameters and updates the properties of the corresponding QObject instances.
 * 		- `debug`: A method that sends a debugging message to the channel. It takes a
 * data payload as its parameter and logs it at the console.
 * 
 * @returns { object } a QWebChannel object with methods for sending messages, handling
 * signals and property updates, and unwrapping properties.
 */
var QWebChannel = function(transport, initCallback)
{
    if (typeof transport !== "object" || typeof transport.send !== "function") {
        console.error("The QWebChannel expects a transport object with a send function and onmessage callback property." +
            " Given is: transport: " + typeof(transport) + ", transport.send: " + typeof(transport.send));
        return;
    }

    var channel = this;
    this.transport = transport;

    /**
     * @description Converts any input `data` to a string before sending it over the
     * `channel.transport.send()` method.
     * 
     * @param { object } data - data to be sent through the channel's transport method.
     */
    this.send = function(data)
    {
        if (typeof(data) !== "string") {
            data = JSON.stringify(data);
        }
        channel.transport.send(data);
    }

    /**
     * @description Handles messages from a Web channel by determining the message type
     * and invoking an appropriate callback function.
     * 
     * @param { object } message - Web Channel message object that contains the data being
     * processed by the function.
     */
    this.transport.onmessage = function(message)
    {
        var data = message.data;
        if (typeof data === "string") {
            data = JSON.parse(data);
        }
        switch (data.type) {
            case QWebChannelMessageTypes.signal:
                channel.handleSignal(data);
                break;
            case QWebChannelMessageTypes.response:
                channel.handleResponse(data);
                break;
            case QWebChannelMessageTypes.propertyUpdate:
                channel.handlePropertyUpdate(data);
                break;
            default:
                console.error("invalid message received:", message.data);
                break;
        }
    }

    this.execCallbacks = {};
    this.execId = 0;
    /**
     * @description Modifies the `channel` object by adding an executive callback for a
     * message and incrementing the next available exec ID.
     * 
     * @param { object } data - message to be sent on the messaging channel.
     * 
     * @param { function. } callback - function to execute when the message is successfully
     * sent through the `channel.send()` method.
     * 
     * 		- If `callback` is not provided, the function will directly send the message to
     * the channel without any modification.
     * 		- If `channel.execId` is set to `Number.MAX_VALUE`, then `callback` will be
     * wrapped with a new unique id.
     * 		- If the input message has its own `id` property, the function will log an error
     * and return without modifying the message.
     * 		- The `id` property of the input message is updated with the next available value
     * from the channel's executive id sequence.
     * 		- The modified message is then sent to the channel using the `send()` method.
     * 
     * @returns { object } a message sent to a message queue along with a unique identifier
     * for the message, as specified in the input data object.
     */
    this.exec = function(data, callback)
    {
        if (!callback) {
            // if no callback is given, send directly
            channel.send(data);
            return;
        }
        if (channel.execId === Number.MAX_VALUE) {
            // wrap
            channel.execId = Number.MIN_VALUE;
        }
        if (data.hasOwnProperty("id")) {
            console.error("Cannot exec message with property id: " + JSON.stringify(data));
            return;
        }
        data.id = channel.execId++;
        channel.execCallbacks[data.id] = callback;
        channel.send(data);
    };

    this.objects = {};

    /**
     * @description Receives a `message` parameter, which contains information about a
     * signal emitted by a object in a communication channel. If the object exists in the
     * channel's `objects` array, the function signals it with the provided `signal` and
     * `args`. Otherwise, it warns about an unhandled signal.
     * 
     * @param { object } message - signal emitted event that triggered the function and
     * provides information about the signal, including its object source and arguments.
     */
    this.handleSignal = function(message)
    {
        var object = channel.objects[message.object];
        if (object) {
            object.signalEmitted(message.signal, message.args);
        } else {
            console.warn("Unhandled signal: " + message.object + "::" + message.signal);
        }
    }

    /**
     * @description Processes a message object and executes callback functions associated
     * with it if it exists, then removes the association between the message ID and the
     * callback function.
     * 
     * @param { object } message - message object passed from the client to the server,
     * and its properties are validated before being passed to the `execCallbacks` callback
     * function for processing.
     * 
     * @returns { undefined` value due to the use of the `delete` operator for removing
     * the property `execCallbacks } a message processed and forwarded to the next stage
     * of the bot's functionality.
     * 
     * 		- `id`: This property is a string that represents the unique identifier of the
     * message being processed. It is a required property in the input message and is
     * used to identify the message within the callback execution.
     * 		- `data`: This property is an object that contains the data passed along with
     * the message. It is the actual payload of the message and is passed through to the
     * callback functions for processing.
     */
    this.handleResponse = function(message)
    {
        if (!message.hasOwnProperty("id")) {
            console.error("Invalid response message received: ", JSON.stringify(message));
            return;
        }
        channel.execCallbacks[message.id](message.data);
        delete channel.execCallbacks[message.id];
    }

    /**
     * @description Handles incoming property updates from a QWebChannel message and
     * updates the properties of an object or logs an error if the object is not found.
     * 
     * @param { object } message - message that contains data updates for objects in a
     * web channel, and the function processes the updates for each object in the message.
     */
    this.handlePropertyUpdate = function(message)
    {
        for (var i in message.data) {
            var data = message.data[i];
            var object = channel.objects[data.object];
            if (object) {
                object.propertyUpdate(data.signals, data.properties);
            } else {
                console.warn("Unhandled property update: " + data.object + "::" + data.signal);
            }
        }
        channel.exec({type: QWebChannelMessageTypes.idle});
    }

    this.debug = function(message)
    {
        channel.send({type: QWebChannelMessageTypes.debug, data: message});
    };

    /**
     * @description Creates new QObjects from data provided, unwraps properties of
     * registered objects, and invokes an `initCallback` function if one is specified.
     * 
     * @param { object } data - JSON data object containing the serialized QObject instances
     * and their properties, which are then unwrapped and registered in the channel.
     */
    channel.exec({type: QWebChannelMessageTypes.init}, function(data) {
        for (var objectName in data) {
            var object = new QObject(objectName, data[objectName], channel);
        }
        // now unwrap properties, which might reference other registered objects
        for (var objectName in channel.objects) {
            channel.objects[objectName].unwrapProperties();
        }
        if (initCallback) {
            initCallback(channel);
        }
        channel.exec({type: QWebChannelMessageTypes.idle});
    });
};

/**
 * @description Generates a new QObject instance and defines its properties, methods,
 * and signals based on a JSON data object passed as argument. It also adds callbacks
 * to signal emitted method for further processing.
 * 
 * @param { string } name - 0-based index of the property, signal, or enumeration in
 * the QObject definition data, which is used to identify the corresponding property,
 * signal, or enumeration in the object and to construct the corresponding QObject
 * methods and signals.
 * 
 * @param { object } data - QObject subclass configuration data that will be processed
 * by the function, containing information about methods, properties, signals, enums,
 * and other metadata to be used for initializing the object's properties and methods.
 * 
 * @param { object } webChannel - QWebChannel interface, which is used to communicate
 * between QObjects in different threads and handle signals and properties updates.
 * 
 * @returns { object } an instance of a custom QObject class that provides additional
 * features such as method invocation, signal emission, and property notifications.
 */
function QObject(name, data, webChannel)
{
    this.__id__ = name;
    webChannel.objects[name] = this;

    // List of callbacks that get invoked upon signal emission
    this.__objectSignals__ = {};

    // Cache of all properties, updated when a notify signal is emitted
    this.__propertyCache__ = {};

    var object = this;

    // ----------------------------------------------------------------------

    this.unwrapQObject = function(response)
    {
        if (response instanceof Array) {
            // support list of objects
            var ret = new Array(response.length);
            for (var i = 0; i < response.length; ++i) {
                ret[i] = object.unwrapQObject(response[i]);
            }
            return ret;
        }
        if (!response
            || !response["__QObject*__"]
            || response.id === undefined) {
            return response;
        }

        var objectId = response.id;
        if (webChannel.objects[objectId])
            return webChannel.objects[objectId];

        if (!response.data) {
            console.error("Cannot unwrap unknown QObject " + objectId + " without data.");
            return;
        }

        var qObject = new QObject( objectId, response.data, webChannel );
        qObject.destroyed.connect(function() {
            if (webChannel.objects[objectId] === qObject) {
                delete webChannel.objects[objectId];
                // reset the now deleted QObject to an empty {} object
                // just assigning {} though would not have the desired effect, but the
                // below also ensures all external references will see the empty map
                // NOTE: this detour is necessary to workaround QTBUG-40021
                var propertyNames = [];
                for (var propertyName in qObject) {
                    propertyNames.push(propertyName);
                }
                for (var idx in propertyNames) {
                    delete qObject[propertyNames[idx]];
                }
            }
        });
        // here we are already initialized, and thus must directly unwrap the properties
        qObject.unwrapProperties();
        return qObject;
    }

    this.unwrapProperties = function()
    {
        for (var propertyIdx in object.__propertyCache__) {
            object.__propertyCache__[propertyIdx] = object.unwrapQObject(object.__propertyCache__[propertyIdx]);
        }
    }

    /**
     * @description Defines a signal handler function for an object. It stores the callback
     * function in the object's `__objectSignals__` array and notifies other connected
     * objects through webChannel.exec() if the signal is not marked as "property notify"
     * or its name is equal to "destroyed".
     * 
     * @param { array } signalData - 2-element array containing the name of the signal
     * and its index, which are used to create the signal object and its connections.
     * 
     * @param { boolean } isPropertyNotifySignal - informational state of the signal,
     * where if set to `true`, separates "pure" signals which get handled individually,
     * while properties in `propertyUpdate` use separate processing; otherwise it is ignored.
     * 
     * @returns { object } an object with two properties: `connect` and `disconnect`,
     * which respectively add and remove a callback function from an object's signal
     * subscription list.
     */
    function addSignal(signalData, isPropertyNotifySignal)
    {
        var signalName = signalData[0];
        var signalIndex = signalData[1];
        object[signalName] = {
            /**
             * @description Adds a callback to an object's signal list. It validates the callback
             * input, then sends a message to a web channel to connect the object and the specified
             * signal index.
             * 
             * @param { `function`. } callback - function to be executed when the given signal
             * is emitted.
             * 
             * 	1/ `typeof`: The type of the callback function, which is `function`.
             * 	2/ `callback`: The function that will be called when the signal is emitted. It
             * must have no arguments.
             * 
             * @returns { undefined value, as it only logs an error message to the console if the
             * given callback parameter does not have the expected data type of a function } a
             * successful notification to the web channel about a connected signal.
             * 
             * 		- `object`: The ID of the object to which the signal is connected.
             * 		- `signalIndex`: The index of the signal in the object's __objectSignals__ property.
             * 		- `isPropertyNotifySignal`: A boolean value indicating whether the signal is a
             * property notify signal. If true, the signal is handled separately for properties
             * in property updates.
             */
            connect: function(callback) {
                if (typeof(callback) !== "function") {
                    console.error("Bad callback given to connect to signal " + signalName);
                    return;
                }

                object.__objectSignals__[signalIndex] = object.__objectSignals__[signalIndex] || [];
                object.__objectSignals__[signalIndex].push(callback);

                if (!isPropertyNotifySignal && signalName !== "destroyed") {
                    // only required for "pure" signals, handled separately for properties in propertyUpdate
                    // also note that we always get notified about the destroyed signal
                    webChannel.exec({
                        type: QWebChannelMessageTypes.connectToSignal,
                        object: object.__id__,
                        signal: signalIndex
                    });
                }
            },
            /**
             * @description Removes a callback from an object's signal index and notifies the web
             * channel if necessary.
             * 
             * @param { `function`. } callback - signal to be disconnected from and is expected
             * to be a function.
             * 
             * 		- `typeof(callback) !== "function"`: If the input `callback` is not a function,
             * an error message is displayed to the user.
             * 		- `object.__objectSignals__[signalIndex] = object.__objectSignals__[signalIndex]
             * || [];`: This line assigns the signal index to the array of connections, if it
             * does not exist already or has no elements.
             * 		- `var idx = object `__objectSignals__ [signalIndex].indexOf(callback);` :This
             * line finds the index of the input `callback` in the array of connections using the
             * `indexOf()` method.
             * 		- `if (idx === -1)`: If the `callback` is not found in the array of connections,
             * an error message is displayed to the user.
             * 		- `object `__objectSignals__ [signalIndex].splice(idx, 1);` : This line removes
             * the `callback` from the array of connections at the found index.
             * 		- `if (!isPropertyNotifySignal && object `__objectSignals__ [signalIndex].length
             * === 0)`: If the signal is not a "pure" signal and has no connections left, a message
             * is sent to the web channel to disconnect from the signal.
             * 
             * 	Note: Throughout this explanation, we have avoided referring to `callback` as an
             * object or making any statements that include the words "I", "me", or "you".
             * 
             * @returns { array } a notification to the web channel that a signal has been disconnected.
             */
            disconnect: function(callback) {
                if (typeof(callback) !== "function") {
                    console.error("Bad callback given to disconnect from signal " + signalName);
                    return;
                }
                object.__objectSignals__[signalIndex] = object.__objectSignals__[signalIndex] || [];
                var idx = object.__objectSignals__[signalIndex].indexOf(callback);
                if (idx === -1) {
                    console.error("Cannot find connection of signal " + signalName + " to " + callback.name);
                    return;
                }
                object.__objectSignals__[signalIndex].splice(idx, 1);
                if (!isPropertyNotifySignal && object.__objectSignals__[signalIndex].length === 0) {
                    // only required for "pure" signals, handled separately for properties in propertyUpdate
                    webChannel.exec({
                        type: QWebChannelMessageTypes.disconnectFromSignal,
                        object: object.__id__,
                        signal: signalIndex
                    });
                }
            }
        };
    }

    /**
     * Invokes all callbacks for the given signalname. Also works for property notify callbacks.
     */
    function invokeSignalCallbacks(signalName, signalArgs)
    {
        var connections = object.__objectSignals__[signalName];
        if (connections) {
            connections.forEach(function(callback) {
                callback.apply(callback, signalArgs);
            });
        }
    }

    this.propertyUpdate = function(signals, propertyMap)
    {
        // update property cache
        for (var propertyIndex in propertyMap) {
            var propertyValue = propertyMap[propertyIndex];
            object.__propertyCache__[propertyIndex] = propertyValue;
        }

        for (var signalName in signals) {
            // Invoke all callbacks, as signalEmitted() does not. This ensures the
            // property cache is updated before the callbacks are invoked.
            invokeSignalCallbacks(signalName, signals[signalName]);
        }
    }

    this.signalEmitted = function(signalName, signalArgs)
    {
        invokeSignalCallbacks(signalName, this.unwrapQObject(signalArgs));
    }

    /**
     * @description Adds a new method to an object, providing the method name and index,
     * as well as any arguments the method takes. It then calls the webChannel's
     * `invokeMethod` method to execute the method and pass back the result.
     * 
     * @param { object } methodData - 2-element array containing the method name and its
     * index within the object, which are used to invoke the method on the given object
     * and pass the arguments to it.
     */
    function addMethod(methodData)
    {
        var methodName = methodData[0];
        var methodIdx = methodData[1];
        object[methodName] = function() {
            var args = [];
            var callback;
            for (var i = 0; i < arguments.length; ++i) {
                var argument = arguments[i];
                if (typeof argument === "function")
                    callback = argument;
                else if (argument instanceof QObject && webChannel.objects[argument.__id__] !== undefined)
                    args.push({
                        "id": argument.__id__
                    });
                else
                    args.push(argument);
            }

            webChannel.exec({
                "type": QWebChannelMessageTypes.invokeMethod,
                "object": object.__id__,
                "method": methodIdx,
                "args": args
            }, function(response) {
                if (response !== undefined) {
                    var result = object.unwrapQObject(response);
                    if (callback) {
                        (callback)(result);
                    }
                }
            });
        };
    }

    /**
     * @description Defines a property on an object and sets up notifications for changes
     * to that property, and defines getters and setters for the property.
     * 
     * @param { array } propertyInfo - 4-element array containing the property name, its
     * index, and notify signal data, which are used to define and cache a property on
     * an object.
     * 
     * @returns { undefined value } a QObject with defined properties and signals, ready
     * to be used in a web channel.
     * 
     * 		- `propertyIndex`: A integer property that represents the index of the property
     * in the array `propertyInfo`.
     * 		- `propertyName`: A string property that represents the name of the property.
     * 		- `notifySignalData`: An object property that contains information about a signal
     * associated with the property. The properties of this object are explained below:
     * 		+ `signalName`: A string property that represents the name of the signal.
     * 		+ `isOptimizedAway`: A boolean property that indicates whether the signal name
     * has been optimized away.
     * 		- `object`: An object property that represents the object for which the property
     * getter and setter are being created.
     * 		- `__id__`: A string property that represents the unique ID of the object.
     * 
     * 	The function takes a single argument, `propertyInfo`, which is an array of six properties:
     * 
     * 	1/ `propertyIndex`: The integer index of the property in the `propertyInfo` array.
     * 	2/ `propertyName`: The string name of the property.
     * 	3/ `notifySignalData`: An object containing information about a signal associated
     * with the property. See below for the properties of this object.
     * 	4/ `value`: The value that will be assigned to the property, which can be either
     * a QObject or a scalar value.
     * 	5/ `type`: The type of the message being sent over the web channel, which is set
     * to `"setProperty"` in this case.
     * 	6/ `object`: The object for which the property getter and setter are being created.
     * This is the same object that is passed as the first argument to the function.
     */
    function bindGetterSetter(propertyInfo)
    {
        var propertyIndex = propertyInfo[0];
        var propertyName = propertyInfo[1];
        var notifySignalData = propertyInfo[2];
        // initialize property cache with current value
        // NOTE: if this is an object, it is not directly unwrapped as it might
        // reference other QObject that we do not know yet
        object.__propertyCache__[propertyIndex] = propertyInfo[3];

        if (notifySignalData) {
            if (notifySignalData[0] === 1) {
                // signal name is optimized away, reconstruct the actual name
                notifySignalData[0] = propertyName + "Changed";
            }
            addSignal(notifySignalData, true);
        }

        Object.defineProperty(object, propertyName, {
            configurable: true,
            /**
             * @description Retrieves a cached property value from an object's `__propertyCache__`
             * index, or issues a warning if the value is undefined.
             * 
             * @returns { undefined value } the value of a property in an object's cache, or a
             * warning message if the property does not exist.
             * 
             * 		- `var propertyValue = object.__propertyCache_[propertyIndex];`: The property
             * value is retrieved from the cache using the index `propertyIndex`.
             * 		- `if (propertyValue === undefined) {...}`: If the property value is undefined,
             * a warning message is logged to the console.
             * 
             * 	Overall, the `get` function retrieves and caches the value of a property in an
             * object, with the ability to handle undefined property values through the use of a
             * cache.
             */
            get: function () {
                var propertyValue = object.__propertyCache__[propertyIndex];
                if (propertyValue === undefined) {
                    // This shouldn't happen
                    console.warn("Undefined value in property cache for property \"" + propertyName + "\" in object " + object.__id__);
                }

                return propertyValue;
            },
            /**
             * @description Sets a property on an object and sends the updated information through
             * a web channel.
             * 
             * @param { `undefined`. } value - value that is being set for the specified property
             * of an object.
             * 
             * 		- `value` is passed as an argument to the function, which can take on any value
             * (either primitive or an instance of QObject).
             * 		- If `value` is undefined, a warning is printed to the console using `console.warn()`.
             * 		- `object` is a QObject that is being worked on, and it has a property called
             * `__propertyCache__` where the property index is stored.
             * 		- `propertyIndex` is the index of the property within the `__propertyCache__`
             * dictionary of `object`.
             * 		- `valueToSend` is the value to be sent through the web channel as part of a
             * QWebChannelMessage object. It can take any form, but if it's an instance of QObject,
             * its `__id__` property must be defined.
             * 
             * 	In summary, the function takes in `value` as the input, checks for undefined
             * values and warns accordingly, updates the property index cache of the QObject, and
             * sends a message through the web channel with the updated value.
             * 
             * @returns { undefined } a QWebChannelMessage object containing the set property values.
             * 
             * 		- `value`: The actual value assigned to the specified property of the object.
             * It is of type `any`, indicating that it can be any type of data.
             * 		- `valueToSend`: A variable that represents the value being sent through the web
             * channel. Its type is inferred as an object based on the fact that it is a QObject
             * and it has an `__id__` property. The `__id__` property is used to identify the
             * object being passed through the channel.
             * 		- `webChannel`: A variable that represents the web channel through which the set
             * property message is being sent. It is of type `QWebChannel`, which is a class
             * provided by Qt for communicating between JavaScript objects in a browser.
             * 		- `objects`: An array-like object that stores references to objects in the
             * JavaScript program. The key in this object is the `__id__` property of each object,
             * and its value is the reference to the object. This array-like object is used to
             * map the values being sent through the web channel to their corresponding objects.
             * 		- `propertyIndex`: An integer that indicates the index of the property in the
             * object's property list. It is used to identify the property being set.
             */
            set: function(value) {
                if (value === undefined) {
                    console.warn("Property setter for " + propertyName + " called with undefined value!");
                    return;
                }
                object.__propertyCache__[propertyIndex] = value;
                var valueToSend = value;
                if (valueToSend instanceof QObject && webChannel.objects[valueToSend.__id__] !== undefined)
                    valueToSend = { "id": valueToSend.__id__ };
                webChannel.exec({
                    "type": QWebChannelMessageTypes.setProperty,
                    "object": object.__id__,
                    "property": propertyIndex,
                    "value": valueToSend
                });
            }
        });

    }

    // ----------------------------------------------------------------------

    data.methods.forEach(addMethod);

    data.properties.forEach(bindGetterSetter);

    data.signals.forEach(function(signal) { addSignal(signal, false); });

    for (var name in data.enums) {
        object[name] = data.enums[name];
    }
}

//required for use with nodejs
if (typeof module === 'object') {
    module.exports = {
        QWebChannel: QWebChannel
    };
}

#!/usr/bin/env python
"""
DFU tool for ReSpeaker USB Mic Array

Requirements:
    pip install pyusb click

Usage:
    python dfu.py --download new_firmware.bin
    python dfu.py --revertfactory
"""

import sys
import time
import usb.core
import usb.util
import click


class DFU(object):
    TIMEOUT = 120000

    DFU_DETACH = 0
    DFU_DNLOAD = 1
    DFU_UPLOAD = 2
    DFU_GETSTATUS = 3
    DFU_CLRSTATUS = 4
    DFU_GETSTATE = 5
    DFU_ABORT = 6

    DFU_STATUS_DICT = {
        0x00: 'No error condition is present.',
        0x01: 'File is not targeted for use by this device.',
        0x02: 'File is for this device but fails some vendor-specific '
            'verification test.',
        0x03: 'Device is unable to write memory.',
        0x04: 'Memory erase function failed.',
        0x05: 'Memory erase check failed.',
        0x06: 'Program memory function failed.',
        0x07: 'Programmed memory failed verification.',
        0x08: 'Cannot program memory due to received address that is our of '
            'range.',
        0x09: 'Received DFU_DNLOAD with wLength = 0, but device does not think it'
            'has all of the data yet.',
        0x0a: "Device's firmware is corrupt. It cannot return to run-time "
            "(non-DFU) operations.",
        0x0b: 'iString indicates a vendor-specific error.',
        0x0c: 'Device detected unexpected USB reset signaling.',
        0x0d: 'Device detected unexpected power on reset.',
        0x0e: 'Something went wrong, but the device does not know what is was.',
        0x0f: 'Device stalled a unexpected request.',
    }

    @staticmethod
    def find():
        """
        find all USB devices with a DFU interface
        """
        devices = []
        for device in usb.core.find(find_all=True, idVendor=0x2886, idProduct=0x0018):
            configuration = device.get_active_configuration()

            for interface in configuration:
                if interface.bInterfaceClass == 0xFE and interface.bInterfaceSubClass == 0x01:
                    devices.append((device,  interface.bInterfaceNumber, configuration.bNumInterfaces))
                    break

        return devices

    def __init__(self):
        """
        Initializes and prepares a `Device` object for use. It retrieves a list
        of DFU devices from the system, checks if only one device is found, and
        extracts information about the selected device. Additionally, it determines
        if the kernel driver is active on the selected interface and detaches it
        before claiming the interface for use.

        """
        devices = self.find()
        if not devices:
            raise ValueError('No DFU device found')

        # TODO: support multiple devices
        if len(devices) > 1:
            raise ValueError('Multiple DFU devices found')

        self.device, self.interface, self.num_interfaces = devices[0]

        # if self.device.is_kernel_driver_active(self.interface):
        #     self.device.detach_kernel_driver(self.interface)

        usb.util.claim_interface(self.device, self.interface)

    def __enter__(self):
        # TODO: suppose the device has more than 1 interface at Run-Time
        """
        Enables the USB device interface, detects re-enumeration of the DFU device,
        and claims the interface for the Python code to interact with it.

        Returns:
            usb.Device` object: the detached and claimed USB interface.
            
            		- `self.num_interfaces`: This variable holds the number of interfaces
            associated with the `Usb` object. If it is greater than 1, the function
            enters DFU mode and performs further actions accordingly.
            		- `self._detach()`: This method detaches the kernel driver from the
            interface.
            		- `self.close()`: This method closes the device connection.
            		- `devices`: This variable holds a list of devices that are found
            during the enumeration process.
            		- `devices[0][2]`: This variable holds the device index in the list
            of devices. If it is equal to 1, it means that a DFU device was found.
            		- `self.device`, `self.interface`: These variables hold the device
            and interface information returned by the `find()` method.
            		- `if self.device.is_kernel_driver_active(self.interface)`: This
            check determines if the kernel driver is active on the interface. If
            it is, the method detaches the kernel driver before claiming the interface.

        """
        if self.num_interfaces > 1:
            print('entering dfu mode')
            self._detach()
            self.close()

            # wait for re-enumerating device
            timeout = 20
            while timeout:
                timeout -= 1
                time.sleep(1)
                devices = self.find()

                if len(devices) and devices[0][2] == 1:
                    print('found dfu device')
                    break
            else:
                raise ValueError('No re-enumerated DFU device found')

            self.device, self.interface, _ = devices[0]

            # # Windows doesn't implement this
            # if self.device.is_kernel_driver_active(self.interface):
            #     self.device.detach_kernel_driver(self.interface)

            usb.util.claim_interface(self.device, self.interface)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def download(self, firmware):
        """
        Args:
            firmware (file object): the file to download.
        """
        block_size = 64
        block_number = 0
        print('downloading')
        while True:
            data = firmware.read(block_size)
            self._download(block_number, data)
            status = self._get_status()[0]
            if status:
                raise IOError(self.DFU_STATUS_DICT[status])

            block_number += 1
            sys.stdout.write('{} bytes\r'.format(block_number * block_size))
            sys.stdout.flush()

            if not data:
                break

        print('\ndone')

    def upload(self, firmware):
        pass

    def _detach(self):
        return self._out_request(self.DFU_DETACH)

    def _download(self, block_number, data):
        return self._out_request(self.DFU_DNLOAD, value=block_number, data=data)


    def _get_status(self):
        """
        Retrieves status information from a device and returns it in the form of
        a tuple containing four values: status, timeout, state, and status description.

        Returns:
            int: a tuple containing four values: `status`, `timeout`, `state`, and
            `status_description`.

        """
        data = self._in_request(self.DFU_GETSTATUS, 6)

        status = data[0]
        timeout = data[1] + data[2] << 8 + data[3] << 16
        state = data[4]
        status_description = data[5]         # index of status description in string table

        return status, timeout, state, status_description

    def _clear_status(self):
        return self._out_request(self.DFU_CLRSTATUS)

    def _get_state(self):
        return self._in_request(self.DFU_GETSTATE, 1)[0]

    def _abort(self):
        return self._out_request(self.DFU_ABORT)

    def _out_request(self, request, value=0, data=None):
        """
        Sends an outgoing control message from a device to a recipient interface
        within the same class and type as the calling function.

        Args:
            request (USB packet command code (USB.util.CTRL_TYPE_CLASS).): 7-bit
                or 10-bit control code to be transmitted over the USB interface.
                
                		- `usb.util.CTRL_OUT`: Specifies that the control transfer is
                being sent from the device to the host.
                		- `usb.util.CTRL_TYPE_CLASS`: Specifies that the control transfer
                is a class-specific command.
                		- `usb.util.CTRL_RECIPIENT_INTERFACE`: Specifies that the control
                transfer is addressed to a particular interface on the device.
                		- `value`: The value of the control transfer request, which can
                be one of the enumerated values from `usb.util.CtrlTransferRequest`.
                		- `self.interface`: The interface number for which the control
                transfer is being sent.
                		- `data`: A variable that contains data related to the control
                transfer request, such as the endpoint address or other configuration
                settings.
                		- `self.TIMEOUT`: The maximum time allowed for completing the
                control transfer operation in milliseconds.
            value (int): 8-bit or 16-bit integer value to be written to the USB
                device as part of the control transfer request.
            data (int): 8-bit interface number for the transaction.

        Returns:
            int: a standard USB error code.

        """
        return self.device.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_CLASS | usb.util.CTRL_RECIPIENT_INTERFACE,
            request, value, self.interface, data, self.TIMEOUT)

    def _in_request(self, request, length):
        """
        Performs a control transfer operation on the connected USB device using
        the provided request value and parameter.

        Args:
            request (`usb.util.CTRL_REQUEST`.): 8-bit request value that determines
                the type of control transfer being performed.
                
                		- `usb.util.CTRL_IN`: indicates that this is an inbound control
                transfer request.
                		- `usb.util.CTRL_TYPE_CLASS`: specifies the control class
                associated with the request.
                		- `usb.util.CTRL_RECIPIENT_INTERFACE`: identifies the interface
                to which the request is directed.
                		- `0x0`: the value of the recipient index, indicating that the
                request is intended for the interface associated with this object.
                		- `self.interface`: references the current interface being worked
                on.
                		- `length`: specifies the size of the input buffer.
            length (int): length of the data transfer buffer for the control
                transfer request.

        Returns:
            int: a boolean value indicating the result of the control transfer operation.

        """
        return self.device.ctrl_transfer(
            usb.util.CTRL_IN | usb.util.CTRL_TYPE_CLASS | usb.util.CTRL_RECIPIENT_INTERFACE,
            request, 0x0, self.interface, length, self.TIMEOUT)

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.device)


class XMOS_DFU(DFU):
    XMOS_DFU_RESETDEVICE = 0xf0
    XMOS_DFU_REVERTFACTORY = 0xf1
    XMOS_DFU_RESETINTODFU = 0xf2
    XMOS_DFU_RESETFROMDFU = 0xf3
    XMOS_DFU_SAVESTATE = 0xf5
    XMOS_DFU_RESTORESTATE = 0xf6

    def __init__(self):
        super(XMOS_DFU, self).__init__()

    def _detach(self):
        return self._out_request(self.XMOS_DFU_RESETINTODFU)

    def leave(self):
        return self._out_request(self.XMOS_DFU_RESETFROMDFU)

    def revertfactory(self):
        return self._out_request(self.XMOS_DFU_REVERTFACTORY)

    def __exit__(self, exc_type, exc_value, traceback):
        self.leave()   



@click.command()
@click.option('--download', '-d', nargs=1, type=click.File('rb'), help='the firmware to download')
@click.option('--revertfactory', is_flag=True, help="factory reset")
def main(download, revertfactory):
    """
    Allows the user to either download a file or revert a factory default on an
    XMOS device using the `XMOS_DFU()` class.

    Args:
        download (int): 64-bit download address of the firmware file to be downloaded
            onto the XMOS device.
        revertfactory (`object` or a class that can be downcast to an object.):
            command to revert the factory settings of the device when passed as `True`.
            
            		- `download`: This is a boolean value indicating whether the
            `revertfactory` should download any data during its execution.

    """
    dev = XMOS_DFU()

    with dev:
        if download:
            dev.download(download)
        elif revertfactory:
            dev.revertfactory()

    dev.close()

if __name__ == '__main__':
    main()



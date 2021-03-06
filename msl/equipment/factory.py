"""
Establish a connection to the equipment.
"""
from .utils import logger
from .config import Config
from .constants import (
    Backend,
    MSLInterface
)
from .exceptions import ResourceClassNotFound
from .resources import find_resource_class
from .resources.dmm import dmm_factory
from .connection_demo import ConnectionDemo
from .connection_pyvisa import ConnectionPyVISA
from .connection_sdk import ConnectionSDK
from .connection_serial import ConnectionSerial
from .connection_socket import ConnectionSocket
from .connection_nidaq import ConnectionNIDAQ
from .connection_prologix import ConnectionPrologix


def connect(record, demo=None):
    """Factory function to establish a connection to the equipment.

    Parameters
    ----------
    record : :class:`~.record_types.EquipmentRecord`
        A record from an :ref:`equipment-database`.

    demo : :class:`bool`, optional
        Whether to simulate a connection to the equipment by opening
        a connection in demo mode. This allows you to test your code
        if the equipment is not physically connected to a computer.

        If :data:`None` then the `demo` value is determined from the
        :attr:`~.config.Config.DEMO_MODE` attribute.

    Returns
    -------
    A :class:`~.connection.Connection` subclass.
    """
    def _connect(_record):
        """Processes a single EquipmentRecord object"""
        def _raise(name):
            raise ValueError('The connection {} has not been set for {}'.format(name, _record))

        conn = _record.connection

        if conn is None:
            _raise('object')
        if not conn.address and conn.backend != Backend.NIDAQ:
            _raise('address')
        if conn.backend == Backend.UNKNOWN:
            _raise('backend')

        cls = None
        if conn.backend == Backend.MSL:
            if conn.interface == MSLInterface.NONE:
                _raise('interface')
            cls = find_resource_class(conn)
            if cls is None:
                if conn.interface == MSLInterface.SDK:
                    raise ResourceClassNotFound(record)
                elif conn.interface == MSLInterface.SERIAL:
                    cls = ConnectionSerial
                elif conn.interface == MSLInterface.SOCKET:
                    cls = ConnectionSocket
                elif conn.interface == MSLInterface.PROLOGIX:
                    cls = ConnectionPrologix
                else:
                    raise NotImplementedError('The {!r} interface has not be written yet'.format(conn.interface.name))
        elif conn.backend == Backend.PyVISA:
            if demo:
                cls = ConnectionPyVISA.resource_class(conn)
            else:
                cls = ConnectionPyVISA
        elif conn.backend == Backend.NIDAQ:
            if demo:
                raise NotImplementedError('NIDAQ cannot be run in demo mode...')
            else:
                cls = ConnectionNIDAQ

        assert cls is not None, 'The Connection class is None'

        if _record.category == 'DMM':
            cls = dmm_factory(conn, cls)

        logger.debug('Connecting to {} using {}'.format(conn, conn.backend.name))
        if demo:
            return ConnectionDemo(_record, cls)
        else:
            return cls(_record)

    if demo is None:
        demo = Config.DEMO_MODE

    if isinstance(record, dict) and len(record) == 1:
        key = list(record.keys())[0]
        return _connect(record[key])
    elif isinstance(record, (list, tuple)) and len(record) == 1:
        return _connect(record[0])
    return _connect(record)


def find_interface(address):
    """Find the interface enum.

    Parameters
    ----------
    address : :class:`str`
        The address of a :class:`~msl.equipment.record_types.ConnectionRecord`.

    Returns
    -------
    :class:`.constants.MSLInterface`
        The interface to use for `address`.
    """
    if ConnectionSDK.parse_address(address):
        return MSLInterface.SDK

    # this check must come before the SERIAL and SOCKET checks
    if ConnectionPrologix.parse_address(address):
        return MSLInterface.PROLOGIX

    if ConnectionSerial.parse_address(address):
        return MSLInterface.SERIAL

    if ConnectionSocket.parse_address(address):
        return MSLInterface.SOCKET

    raise ValueError('Cannot determine the MSLInterface from address {!r}'.format(address))

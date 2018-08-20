"""
Records from :ref:`equipment_database`\'s or :ref:`connections_database`\'s.
"""
import re
import enum
import logging
import datetime
from xml.etree.cElementTree import Element

from dateutil.relativedelta import relativedelta

from .constants import Backend, MSLInterface, MSL_INTERFACE_ALIASES

logger = logging.getLogger(__name__)


class EquipmentRecord(object):

    def __init__(self, **kwargs):
        """Contains the information about an equipment record in an :ref:`equipment_database`.

        Parameters
        ----------
        **kwargs
            The argument names can be any of the :class:`EquipmentRecord` property names.
        """

        # these properties are NOT defined as fields in the equipment-register database
        self._alias = u''
        self._connection = None
        self._team = u''

        # these properties can be defined as fields in the equipment-register database
        self._calibration_cycle = 0.0
        self._category = u''
        self._date_calibrated = datetime.date(datetime.MINYEAR, 1, 1)
        self._description = u''
        self._latest_report_number = u''
        self._location = u''
        self._manufacturer = u''
        self._model = u''
        self._serial = u''
        # IMPORTANT: when a new property is added remember to include it in docs/database#register_field_names

        valid_names = self._valid_names()
        for name in kwargs:
            if name == 'connection':
                # set the connection after the manufacturer, model and serial are all set
                pass
            elif name == 'date_calibrated':
                if isinstance(kwargs[name], datetime.date):
                    self._date_calibrated = kwargs[name]
                else:
                    raise TypeError('The date_calibrated value must be a datetime.date object')
            elif name == 'calibration_cycle':
                try:
                    self._calibration_cycle = max(0.0, float(kwargs[name]))
                    err = ''
                except ValueError:
                    err = 'The calibration_cycle must be a number.'
                if err:
                    raise ValueError(err)
            else:
                if name in valid_names:
                    setattr(self, '_'+name, str(kwargs[name]))
                else:
                    err = 'An EquipmentRecord has no "{}" attribute.\nValid attributes are {}'.format(name, valid_names)
                    raise AttributeError(err)

        if 'connection' in kwargs:
            self.connection = kwargs['connection']

    def __repr__(self):
        return u'{}<{}|{}|{}>'.format(self.__class__.__name__, self.manufacturer, self.model, self.serial)

    def _valid_names(self):
        """Returns a list of the valid property names for an EquipmentRecord"""
        return sorted([k[1:] for k in vars(self)])

    @property
    def alias(self):
        """:class:`str`: An alias to use to reference this equipment by.

        The `alias` can be defined in different in 3 ways:

        * in the **<equipment>** XML tag in a :ref:`configuration_file`
        * in the **Properties** field in a :ref:`connections_database`
        * by redefining the `alias` value after the :class:`EquipmentRecord` has been instantiated

        """
        return self._alias

    @alias.setter
    def alias(self, text):
        self._alias = u'{}'.format(text)

    @property
    def calibration_cycle(self):
        """:class:`float`: The number of years that can pass before the equipment must be re-calibrated."""
        return self._calibration_cycle

    @property
    def category(self):
        """:class:`str`: The category (e.g., Laser, DMM) that the equipment belongs to."""
        return self._category

    @property
    def connection(self):
        """:class:`ConnectionRecord` or :data:`None`: The information necessary to
        establish a connection to the equipment."""
        return self._connection

    @connection.setter
    def connection(self, connection_record):
        """Set the information necessary to establish a connection to the equipment.
        
        Parameters
        ----------
        connection_record : :class:`ConnectionRecord`
            A connection record.
        
        Raises
        ------
        TypeError
            If `connection_record` is not of type :class:`ConnectionRecord`.            
        ValueError
            If any of the `manufacturer`, `model`, `serial` values in the `connection_record` 
            are set and they do not match those values in this :class:`EquipmentRecord`.
        """
        if not isinstance(connection_record, ConnectionRecord):
            raise TypeError('The connection record must be a ConnectionRecord object')

        # check that the manufacturer, model number and serial number match
        for attrib in ('_manufacturer', '_model', '_serial'):
            if not getattr(connection_record, attrib):
                # then it was not set in the connection_record
                setattr(connection_record, attrib, getattr(self, attrib))
            elif getattr(connection_record, attrib) != getattr(self, attrib):
                msg = 'ConnectionRecord.{0} ({1}) != EquipmentRecord.{0} ({2})'\
                    .format(attrib[1:], getattr(connection_record, attrib), getattr(self, attrib))
                raise ValueError(msg)

        self._connection = connection_record

    @property
    def date_calibrated(self):
        """:class:`datetime.date`: The date that the equipment was last calibrated."""
        return self._date_calibrated

    @property
    def description(self):
        """:class:`str`: A description of the equipment."""
        return self._description

    @property
    def latest_report_number(self):
        """:class:`str`: The report number for the last time that the equipment was calibrated."""
        return self._latest_report_number

    @property
    def location(self):
        """:class:`str`: The location where the equipment can usually be found."""
        return self._location

    @property
    def manufacturer(self):
        """:class:`str`: The name of the manufacturer of the equipment."""
        return self._manufacturer

    @property
    def model(self):
        """:class:`str`: The model number of the equipment."""
        return self._model

    @property
    def serial(self):
        """:class:`str`: The serial number, or engraved unique ID, of the equipment."""
        return self._serial

    @property
    def team(self):
        """:class:`str`: The team (e.g., Light Standards) that the equipment belongs to."""
        return self._team

    def connect(self, demo=None):
        """Establish a connection to the equipment.

        Calls the :func:`~msl.equipment.factory.connect` function.

        Parameters
        ----------
        demo : :class:`bool`, optional
            Whether to simulate a connection to the equipment by opening
            a connection in demo mode. This allows you to test your code
            if the equipment is not physically connected to a computer.
            
            If :data:`None` then the `demo` value is determined from the
            :attr:`~.config.Config.DEMO_MODE` attribute.

        Returns
        -------
        A :class:`~msl.equipment.connection.Connection` subclass.
        """
        from msl.equipment import factory  # import here to avoid circular imports
        return factory.connect(self, demo)

    def is_calibration_due(self, months=0):
        """Whether the equipment needs to be re-calibrated.

        Parameters
        ----------
        months : :class:`int`
            The number of months to add to today's date to determine if
            the equipment needs to be re-calibrated within a certain amount
            of time. For example, if ``months = 6`` then that is a way of
            asking *"is a re-calibration due within the next 6 months?"*.

        Returns
        -------
        :class:`bool`
            :data:`True` if the equipment needs to be re-calibrated, :data:`False`
            if it does not need to be re-calibrated.
        """
        if self.date_calibrated.year == datetime.MINYEAR or self.calibration_cycle == 0.0:
            return False
        ask_date = datetime.date.today() + relativedelta(months=max(0, int(months)))
        return ask_date >= self.next_calibration_date()

    def next_calibration_date(self):
        """The date that the next calibration is due.

        Returns
        -------
        :class:`datetime.date`
            The next calibration date."""
        years = int(self.calibration_cycle)
        months = int(round(12 * (self.calibration_cycle - years)))
        return self.date_calibrated + relativedelta(years=years, months=months)

    def to_dict(self):
        """Convert this :class:`EquipmentRecord` to a dictionary.

        Returns
        -------
        :class:`dict`
            The :class:`EquipmentRecord` as a dictionary.
        """
        d = {}
        for name in self._valid_names():
            if name == 'connection':
                d[name] = self.connection.to_dict() if self.connection is not None else None
            else:
                d[name] = getattr(self, name)
        return d

    def to_xml(self):
        """Convert this :class:`EquipmentRecord` to an XML :class:`~xml.etree.ElementTree.Element`.

        All values of the :class:`EquipmentRecord` are converted to a :class:`str`.

        Returns
        -------
        :class:`~xml.etree.ElementTree.Element`
            The :class:`EquipmentRecord` as an XML element.
        """
        root = Element('equipment')
        for name in self._valid_names():
            element = Element(name)
            if name == 'connection':
                if self.connection is None:
                    element.text = u''
                else:
                    for el in self.connection.to_xml():
                        element.append(el)
            elif name == 'date_calibrated':
                date = self.date_calibrated
                element.text = u'{}'.format(date.isoformat()) if date.year != datetime.MINYEAR else u''
            elif name == 'calibration_cycle':
                if self.calibration_cycle == 0:
                    element.text = u''
                elif int(self.calibration_cycle) == self.calibration_cycle:
                    element.text = u'{}'.format(int(self.calibration_cycle))
                else:
                    element.text = u'{}'.format(self.calibration_cycle)
            else:
                element.text = u'{}'.format(getattr(self, name))
            root.append(element)
        return root

    def to_yaml(self, indent=2):
        """Convert this :class:`EquipmentRecord` to a YAML_ string.

        .. _YAML: https://en.wikipedia.org/wiki/YAML

        Parameters
        ----------
        indent : :class:`int`
            The amount of indentation added for each recursive level.

        Returns
        -------
        :class:`str`
            The :class:`EquipmentRecord` as a string.
        """
        out = u''
        for element in self.to_xml():
            if element.text is not None:
                if element.text:
                    out += u'{}: {}\n'.format(element.tag, element.text)
                else:
                    out += u"{}: ''\n".format(element.tag)
            else:  # the connection values
                out += u'connection:\n'
                for line in self.connection.to_yaml(indent=indent).splitlines():
                    out += u' ' * indent + line + u'\n'
        return out[:-1]


class ConnectionRecord(object):

    def __init__(self, **kwargs):
        """Contains the information about a connection record in a :ref:`connections_database`.

        Parameters
        ----------
        **kwargs
            The argument names can be any of the :class:`ConnectionRecord` property names.
        """

        # these properties are NOT defined as fields in the connection database
        self._interface = MSLInterface.NONE

        # these properties can be defined as fields in the connection database
        self._address = u''
        self._backend = Backend.UNKNOWN
        self._manufacturer = u''
        self._model = u''
        self._properties = dict()
        self._serial = u''
        # IMPORTANT: when a new property is added remember to include it in table in docs/database#connections_database

        valid_names = self._valid_names()
        for name in kwargs:
            if name == 'address':
                # the backend value is dependent on the address value and the MSL Interface is dependant on the
                # backend value, so deal with the backend and the interface here
                self._address = str(kwargs[name])
                if 'backend' in kwargs:
                    self._backend = Backend(kwargs['backend'])
                if self._backend == Backend.MSL:
                    interface = MSLInterface[self._get_interface_name_from_address()]
                    if 'interface' in kwargs:
                        if not isinstance(kwargs['interface'], MSLInterface):
                            raise TypeError('The interface must be of type {}'.format(MSLInterface))
                        if kwargs['interface'] != interface:
                            raise ValueError('The interface does not agree with what is expected from the address')
                    self._interface = interface

            elif name == 'backend':
                if 'address' not in kwargs:
                    self._backend = Backend(kwargs[name])
            elif name == 'interface':
                pass  # handled by `address`
            elif name == 'properties':
                self.properties = kwargs[name]
            else:
                if name in valid_names:
                    setattr(self, '_'+name, str(kwargs[name]))
                else:
                    err = 'A ConnectionRecord has no "{}" attribute.\nValid attributes are {}'.format(name, valid_names)
                    raise AttributeError(err)

        # helpful checks based on the value of `address`
        if self._address.startswith('UDP'):
            self._properties['type'] = 'SOCK_DGRAM'

    def __repr__(self):
        return u'{}<{}|{}|{}>'.format(self.__class__.__name__, self.manufacturer, self.model, self.serial)

    def _valid_names(self):
        """Returns a list of the valid property names for an ConnectionRecord"""
        return sorted([k[1:] for k in vars(self)])

    @property
    def address(self):
        """:class:`str`: The address to use for the connection (see :ref:`address_syntax` for examples)."""
        return self._address

    @property
    def backend(self):
        """:class:`~.constants.Backend`: The backend to use to communicate with the equipment."""
        return self._backend

    @property
    def interface(self):
        """:class:`~.constants.MSLInterface`: The interface that is used for the
        communication system that transfers data between a computer and the equipment
        (only used if the :attr:`.backend` is equal to :attr:`~.constants.Backend.MSL`).
        """
        return self._interface

    @property
    def manufacturer(self):
        """:class:`str`: The name of the manufacturer of the equipment."""
        return self._manufacturer

    @property
    def model(self):
        """:class:`str`: The model number of the equipment."""
        return self._model

    @property
    def properties(self):
        """
        :class:`dict`: Additional properties that may be required to connect to the equipment.

        For example, communicating via RS-232 may require::

            {'baud_rate': 19200, 'parity': 'even'}

        See the :ref:`connections_database` for examples on how to set the `properties`.
        """
        return self._properties

    @properties.setter
    def properties(self, props):
        if not isinstance(props, dict):
            raise TypeError('The properties must be a dictionary')
        self._properties = props.copy()

    @property
    def serial(self):
        """:class:`str`: The serial number, or engraved unique ID, of the equipment."""
        return self._serial

    def to_dict(self):
        """Convert this :class:`ConnectionRecord` to a dictionary.

        Returns
        -------
        :class:`dict`
            The :class:`ConnectionRecord` as a dictionary.
        """
        return {n: getattr(self, n) for n in self._valid_names()}

    def to_xml(self):
        """Convert this :class:`ConnectionRecord` to an XML :class:`~xml.etree.ElementTree.Element`.

        All values of the :class:`ConnectionRecord` are converted to a :class:`str`.

        Returns
        -------
        :class:`~xml.etree.ElementTree.Element`
            The :class:`ConnectionRecord` as a XML element.
        """
        root = Element('connection')
        for name in self._valid_names():
            element = Element(name)
            if name == 'properties':
                if not self.properties:
                    element.text = u''
                else:
                    for key, value in self.properties.items():
                        prop = Element(key)
                        if isinstance(value, enum.Enum):
                            prop.text = u'{}'.format(str(value))
                        elif 'termination' in key:
                            prop.text = u'{!r}'.format(value)
                        else:
                            prop.text = u'{}'.format(value)
                        element.append(prop)
            elif name == 'backend' or name == 'interface':
                # want to get the enum name not the enum value
                element.text = u'{}'.format(getattr(self, name).name)
            else:
                element.text = u'{}'.format(getattr(self, name))
            root.append(element)
        return root

    def to_yaml(self, indent=2):
        """Convert this :class:`ConnectionRecord` to a YAML_ string.

        .. _YAML: https://en.wikipedia.org/wiki/YAML

        Parameters
        ----------
        indent : :class:`int`
            The amount of indentation added for each recursive level.

        Returns
        -------
        :class:`str`
            The :class:`ConnectionRecord` as a string.
        """
        out = u''
        for element in self.to_xml():
            if element.text:
                out += u'{}: {}\n'.format(element.tag, element.text)
            else:
                out += u'{}'.format(element.tag)
                if not element:
                    out += u": ''\n"
                else:
                    out += u':\n'
                    for prop in element:
                        out += u' ' * indent + u'{}: {}\n'.format(prop.tag, prop.text)
        return out[:-1]

    def _get_interface_name_from_address(self):
        """:class:`str`: Gets the interface name based on the address value."""

        address_upper = self._address.upper()

        # checks for equivalent PyVISA addresses
        if address_upper.startswith('TCPIP') and address_upper.endswith('SOCKET'):
            return 'SOCKET'

        # determine the MSL Interface
        match = re.match('[+_A-Z]+', address_upper)
        interface_name = '' if match is None else match.group(0).replace('+', '_')

        # check if aliases are used for the MSL Interface
        replaced = False
        for name, values in MSL_INTERFACE_ALIASES.items():
            for value in values:
                if value in interface_name:
                    interface_name = interface_name.replace(value, name)
                    replaced = True
            if replaced:
                break

        return interface_name

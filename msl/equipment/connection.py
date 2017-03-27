"""
Base class for establishing a connection to the equipment.
"""


class Connection(object):

    def __init__(self, record):
        """
        All Connection :class:`~msl.equipment.constants.Backend` classes must 
        have this class as the base class.

        Do not instantiate this class directly. Use :func:`msl.equipment.factory.connect`
        or :meth:`record.connect() <msl.equipment.record_types.EquipmentRecord.connect>`
        to connect to the equipment.

        Args:
            record (:class:`~.record_types.EquipmentRecord`): An equipment 
                record (a row) from the :class:`~.database.Database`.
        """
        self._record = record

    @property
    def equipment_record(self):
        """
        :py:class:`~msl.equipment.record_types.EquipmentRecord`: The equipment record from a database.
        """
        return self._record

    def disconnect(self):
        """
        Implement tasks that need to be performed in order to safely disconnect 
        from the equipment. For example,

        * clean up system resources from memory
        * configure the equipment to be in a state that is safe for people 
          working in the lab when the equipment is not in use
        
        .. note::
           This method gets called automatically when the :class:`.Connection` 
           object gets destroyed.
        """
        pass

    def __repr__(self):
        return '{}<{}|{}|{} at {}>'.format(self.__class__.__name__,
                                           self._record.manufacturer,
                                           self._record.model,
                                           self._record.serial,
                                           self._record.connection.address)

    def __del__(self):
        self.disconnect()

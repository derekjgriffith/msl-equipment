"""
OMEGA iTHX Series Temperature and Humidity Chart Recorder.

This class is compatible with the following model numbers:

* iTHX-W3
* iTHX-D3
* iTHX-SD
* iTHX-M
* iTHX-W
* iTHX-2
"""
import os
import re
import time
import socket
import sqlite3
import datetime
try:
    ConnectionResetError
except NameError:
    ConnectionResetError = socket.error  # for Python 2.7

from msl.equipment.exceptions import OmegaError, MSLTimeoutError
from msl.equipment.connection_socket import ConnectionSocket
from msl.equipment.resources import register


@register(manufacturer=r'OMEGA', model=r'iTHX-[2DMSW][3D]*', flags=re.IGNORECASE)
class iTHX(ConnectionSocket):

    def __init__(self, record):
        """OMEGA iTHX Series Temperature and Humidity Chart Recorder.

        Do not instantiate this class directly. Use the :meth:`~.EquipmentRecord.connect`
        method to connect to the equipment.

        Parameters
        ----------
        record : :class:`~.EquipmentRecord`
            A record from an :ref:`equipment-database`.
        """
        super(iTHX, self).__init__(record)
        self.set_exception_class(OmegaError)
        self.IS_W_OR_2 = record.model.upper() in ['ITHX-2', 'ITHX-W']

    def temperature(self, probe=1, celsius=True, nbytes=None):
        """Read the temperature.

        Parameters
        ----------
        probe : :class:`int`, optional
            The probe number to read the temperature of (for iTHX's that contain multiple probes).
        celsius : class:`bool`, optional
            :data:`True` to return the temperature in celsius, :data:`False` for fahrenheit.
        nbytes : class:`int`, optional
            The number of bytes to read. If :data:`None` then read until the termination
            character sequence.

        Returns
        -------
        :class:`float` or :class:`tuple` of :class:`float`
            The current temperature.
        """
        msg = 'TC' if celsius else 'TF'
        return self._get(msg, probe, size=nbytes)

    def humidity(self, probe=1, nbytes=None):
        """Read the percent humidity.

        Parameters
        ----------
        probe : :class:`int`, optional
            The probe number to read the humidity of (for iTHX's that contain multiple probes).
        nbytes : class:`int`, optional
            The number of bytes to read. If :data:`None` then read until the termination
            character sequence.

        Returns
        -------
        :class:`float` or :class:`tuple` of :class:`float`
            The current percent humidity.
        """
        return self._get('H', probe, size=nbytes)

    def dewpoint(self, probe=1, celsius=True, nbytes=None):
        """Read the dew point.

        Parameters
        ----------
        probe : :class:`int`, optional
            The probe number to read the dew point of (for iTHX's that contain multiple probes).
        celsius : :class:`bool`, optional
            :data:`True` to return the dew point in celsius, :data:`False` for fahrenheit.
        nbytes : class:`int`, optional
            The number of bytes to read. If :data:`None` then read until the termination
            character sequence.

        Returns
        -------
        :class:`float` or :class:`tuple` of :class:`float`
            The current dew point.
        """
        msg = 'D' if celsius else 'DF'
        return self._get(msg, probe, size=nbytes)

    def temperature_humidity(self, probe=1, celsius=True, nbytes=None):
        """Read the temperature and the humidity.

        Parameters
        ----------
        probe : :class:`int`, optional
            The probe number to read the temperature and humidity of (for iTHX's that contain multiple probes).
        celsius : :class:`bool`, optional
            :data:`True` to return the temperature in celsius, :data:`False` for fahrenheit.
        nbytes : class:`int`, optional
            The number of bytes to read. If :data:`None` then the default value is 13 bytes.

        Returns
        -------
        :class:`float`
            The current temperature.
        :class:`float`
            The current humidity.
        """
        if nbytes is None:
            # since the returned bytes are of the form b'019.4\r,057.0\r'
            # the _get method would stop reading bytes at the first instance of '\r'
            # therefore, we will specify the number of bytes to read to get both values
            nbytes = 13

        if self.IS_W_OR_2:
            # iTHX-W and iTHX-2 do not support the 'B' command
            n = nbytes//2
            return self.temperature(probe=probe, celsius=celsius, nbytes=n), self.humidity(probe=probe, nbytes=n)

        msg = 'B' if celsius else 'BF'
        return self._get(msg, probe, size=nbytes)

    def temperature_humidity_dewpoint(self, probe=1, celsius=True, nbytes=None):
        """Read the temperature, the humidity and the dew point.

        Parameters
        ----------
        probe : :class:`int`, optional
            The probe number to read the temperature, humidity and dew point (for iTHX's that contain multiple probes).
        celsius : :class:`bool`, optional
            If :data:`True` then return the temperature and dew point in celsius, :data:`False` for fahrenheit.
        nbytes : :class:`int`, optional
            The number of bytes to read. If :data:`None` then read until the termination
            character sequence. For example, if no termination is returned and each value is
            represented by 6 bytes then specify ``nbytes=18`` to get all 3 values.

        Returns
        -------
        :class:`float`
            The current temperature.
        :class:`float`
            The current humidity.
        :class:`float`
            The current dew point.
        """
        nth = None if nbytes is None else (nbytes*2)//3
        nd = None if nbytes is None else nbytes//3
        t, h = self.temperature_humidity(probe=probe, celsius=celsius, nbytes=nth)
        return t, h, self.dewpoint(probe=probe, celsius=celsius, nbytes=nd)

    def start_logging(self, path, wait=60, nprobes=1, nbytes=None):
        """Start logging the temperature, humidity and dew point to the specified path.

        The information is logged to a SQLite_ database. To stop logging press ``CTRL+C``.

        .. _SQLite: https://www.sqlite.org/index.html

        Parameters
        ----------
        path : :class:`str`
            The path to the SQLite_ database. If you only specify a folder then a database
            with the default filename, ``model_serial.sqlite3``, is created/opened in this folder.
        wait : :class:`int`, optional
            The number of seconds to wait between each log.
        nprobes : :class:`int`, optional
            The number of probes that the iServer has (1 or 2).
        nbytes : :class:`int`, optional
            The number of bytes to read. If :data:`None` then read until the termination
            character sequence. For example, if no termination is used and each value is
            represented by 6 bytes then specify ``nbytes=18`` to get all three values.
        """
        if os.path.isdir(path):
            filename = self.equipment_record.model + '_' + self.equipment_record.serial + '.sqlite3'
            path = os.path.join(path, filename)

        db_timeout = 10.0

        db = sqlite3.connect(path, timeout=db_timeout)
        self.log_info('start logging to {}'.format(path))

        if nprobes == 1:
            db.execute(
                'CREATE TABLE IF NOT EXISTS data ('
                'timestamp TIMESTAMP, '
                'temperature FLOAT, '
                'humidity FLOAT, '
                'dewpoint FLOAT);'
            )
        elif nprobes == 2:
            db.execute(
                'CREATE TABLE IF NOT EXISTS data ('
                'timestamp TIMESTAMP, '
                'temperature1 FLOAT, '
                'humidity1 FLOAT, '
                'dewpoint1 FLOAT, '
                'temperature2 FLOAT, '
                'humidity2 FLOAT, '
                'dewpoint2 FLOAT);'
            )
        else:
            raise ValueError('The number-of-probes value must be either 1 or 2. Got {}'.format(nprobes))

        db.commit()
        db.close()

        msg = 'Sn:{} - {}:{} => '.format(self.equipment_record.serial, self._host, self._port)

        try:
            while True:
                t0 = time.time()
                results = [datetime.datetime.now()]

                # get the values
                try:
                    data = self.temperature_humidity_dewpoint(probe=1, celsius=True, nbytes=nbytes)
                    if nprobes == 2:
                        data += self.temperature_humidity_dewpoint(probe=2, celsius=True, nbytes=nbytes)
                        self.log_info(msg+'T1={:.1f} H1={:.1f} DP1={:.1f} T2={:.1f} H2={:.1f} DP2={:.1f}'.format(*data))
                    else:
                        self.log_info(msg+'T={:.1f} H={:.1f} DP={:.1f}'.format(*data))
                except MSLTimeoutError:
                    while True:
                        try:
                            self._connect()
                        except MSLTimeoutError:
                            pass
                        else:
                            break
                    continue
                else:
                    results.extend(data)

                # save the values to the database and then wait
                try:
                    db = sqlite3.connect(path, timeout=db_timeout)
                    if nprobes == 1:
                        db.execute('INSERT INTO data VALUES (?, ?, ?, ?);', results)
                    else:
                        db.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?);', results)
                    db.commit()
                    db.close()
                except sqlite3.OperationalError as e:  # database is locked, someone is reading data
                    db.close()
                    self.log_error('sqlite3.OperationalError: ' + str(e))
                else:
                    time.sleep(max(0.0, wait - (time.time() - t0)))

        except (KeyboardInterrupt, SystemExit):
            pass

        db.close()
        self.log_info('stopped logging to {}'.format(path))

    @staticmethod
    def data(path, date1=None, date2=None, as_datetime=True, select='*'):
        """Fetch all the log records between two dates.

        Parameters
        ----------
        path : :class:`str`
            The path to the SQLite_ database.
        date1 : :class:`datetime.datetime` or :class:`str`, optional
            Include all records that have a timestamp > `date1`. If :class:`str` then in
            ``yyyy-mm-dd`` or ``yyyy-mm-dd HH:MM:SS`` format.
        date2 : :class:`datetime.datetime` or :class:`str`, optional
            Include all records that have a timestamp < `date2`. If :class:`str` then in
            ``yyyy-mm-dd`` or ``yyyy-mm-dd HH:MM:SS`` format.
        as_datetime : :class:`bool`, optional
            Whether to fetch the timestamps from the database as :class:`datetime.datetime` objects.
            If :data:`False` then the timestamps will be of type :class:`str` and this function
            will return much faster if requesting data over a large date range.
        select : :class:`str` or :class:`list` of :class:`str`, optional
            The column(s) in the database to use with the ``SELECT`` SQL command.

        Returns
        -------
        :class:`list` of :class:`tuple`
            A list of ``(timestamp, temperature, humidity, dewpoint)`` log records,
            depending on the value of `select`.
        """
        if not os.path.isfile(path):
            raise IOError('Cannot find {}'.format(path))

        detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES if as_datetime else 0
        db = sqlite3.connect(path, timeout=10.0, detect_types=detect_types)
        cursor = db.cursor()

        if select != '*':
            if isinstance(select, (list, tuple, set)):
                select = ','.join(select)
        base = 'SELECT {} FROM data'.format(select)

        if date1 is None and date2 is None:
            cursor.execute(base + ';')
        elif date1 is not None and date2 is None:
            cursor.execute(base + ' WHERE timestamp > ?;', (date1,))
        elif date1 is None and date2 is not None:
            cursor.execute(base + ' WHERE timestamp < ?;', (date2,))
        else:
            cursor.execute(base + ' WHERE timestamp BETWEEN ? AND ?;', (date1, date2))

        data = cursor.fetchall()
        cursor.close()
        db.close()
        return data

    def _get(self, message, probe, size=None):
        if not 1 <= probe <= 3:
            self.raise_exception('Invalid probe number, {}. Must be either 1, 2, or 3'.format(probe))

        command = '*SR' + message
        if probe > 1:
            command += str(probe)

        try:
            ret = self.query(command, size=size)
        except ConnectionResetError:
            # for some reason the socket closes if a certain amount of time passes and no
            # messages have been sent. For example, querying the temperature, humidity and
            # dew point every >60 seconds raised:
            #   [Errno errno.ECONNRESET] An existing connection was forcibly closed by the remote host
            self._connect()  # reconnect
            return self._get(message, probe, size=size)  # retry
        else:
            values = tuple(float(v) for v in re.split(r'[,;]', ret))
            if len(values) == 1:
                return values[0]
            else:
                return values

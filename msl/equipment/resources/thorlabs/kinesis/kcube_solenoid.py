"""
This module provides all the functionality required to control a
KCube Solenoid (KSC101).
"""
from ctypes import c_int16, c_uint, c_int64, byref

from msl.equipment.resources.utils import WORD, DWORD
from .motion_control import MotionControl
from .api_functions import KCube_Solenoid_FCNS
from .structs import (
    SC_CycleParameters,
    TLI_HardwareInformation,
    KSC_MMIParams,
    KSC_TriggerConfig,
)
from .enums import (
    SC_OperatingModes,
    SC_OperatingStates,
    SC_SolenoidStates,
    KSC_TriggerPortMode,
    KSC_TriggerPortPolarity
)


class KCubeSolenoid(MotionControl):

    def __init__(self, record):
        """A wrapper around Thorlabs.MotionControl.KCube.Solenoid

        Parameters
        ----------
        record : :class:`~msl.equipment.record_types.EquipmentRecord`
            An equipment record from an **Equipment-Register**
            :class:`~msl.equipment.database.Database`.
        """
        MotionControl.__init__(self, record, KCube_Solenoid_FCNS)

    def check_connection(self):
        """Check connection.

        Returns
        -------
        :obj:`bool`
            Whether the USB is listed by the FTDI controller.
        """
        return self.sdk.SC_CheckConnection(self._serial)

    def clear_message_queue(self):
        """Clears the device message queue."""
        self.sdk.SC_ClearMessageQueue(self._serial)

    def close(self):
        """Disconnect and close the device."""
        self.sdk.SC_Close(self._serial)

    def enable_last_msg_timer(self, enable, msg_timeout=0):
        """Enables the last message monitoring timer.

        This can be used to determine whether communications with the device is
        still good.

        Parameters
        ----------
        enable : :obj:`bool`
            :obj:`True` to enable monitoring otherwise :obj:`False` to disable.
        msg_timeout : :obj:`int`
            The last message error timeout in ms. Set to 0 to disable.
        """
        self.sdk.SC_EnableLastMsgTimer(self._serial, enable, msg_timeout)

    def get_cycle_params(self):
        """Gets the cycle parameters.

        Returns
        -------
        :obj:`int`
            The *On Time* parameter. Range 250 to 100,000,000 in steps of 1
            milliseconds (0.250s to 10,000s).
        :obj:`int`
            The *Off Time* parameter. Range 250 to 100,000,000 in steps of 1
            milliseconds (0.250s to 10,000s).
        :obj:`int`
            The *Number of Cycles* parameter. Range 0 to 1000,000 where 0
            represents unlimited.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        on_time = c_uint()
        off_time = c_uint()
        num_cycles = c_uint()
        self.sdk.SC_GetCycleParams(self._serial, byref(on_time), byref(off_time), byref(num_cycles))
        return on_time.value, off_time.value, num_cycles.value

    def get_cycle_params_block(self):
        """Get the cycle parameters.

        Returns
        -------
        :class:`.structs.SC_CycleParameters`
            The cycle parameters.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        cycle_params = SC_CycleParameters()
        self.sdk.SC_GetCycleParamsBlock(self._serial, byref(cycle_params))
        return cycle_params

    def get_digital_outputs(self):
        """Gets the digital output bits.

        Returns
        -------
        :obj:`int`
            Bit mask of states of the 4 digital output pins.
        """
        return self.sdk.SC_GetDigitalOutputs(self._serial)

    def get_hardware_info(self):
        """Gets the hardware information from the device.

        Returns
        -------
        :class:`.structs.TLI_HardwareInformation`
            The hardware information.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self._get_hardware_info(self.sdk.SC_GetHardwareInfo)

    def get_hardware_info_block(self):
        """Gets the hardware information in a block.

        Returns
        -------
        :class:`.structs.TLI_HardwareInformation`
            The hardware information.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        info = TLI_HardwareInformation()
        self.sdk.SC_GetHardwareInfoBlock(self._serial, byref(info))
        return info

    def get_hub_bay(self):
        """Gets the hub bay number this device is fitted to.

        Returns
        -------
        :obj:`int`
            Either the number, or 0x00 if unknown, or 0xff if not on a hub.
        """
        return self.sdk.SC_GetHubBay(self._serial)

    def get_led_switches(self):
        """Get the LED indicator bits on cube.

        Returns
        -------
        :obj:`int`
            Sum of: 8 to indicate moving 2 to indicate end of track and 1
            to flash on identify command.
        """
        return self.sdk.SC_GetLEDswitches(self._serial)

    def get_mmi_params(self):
        """Get the MMI Parameters for the KCube Display Interface.

        Deprecated: calls :meth:`get_mmi_params_ext`

        Returns
        -------
        :obj:`int`
            The display intensity, range 0 to 100%.
        :obj:`int`
            The display timeout, range 0 to 480 in minutes (0 is off, otherwise
            the inactivity period before dimming the display).
        :obj:`int`
            The display dimmed intensity, range 0 to 10 (after the timeout
            period the device display will dim).

        Raises
        ------
        ConnectionError
            If not successful.
        """
        return self.get_mmi_params_ext()

    def get_mmi_params_block(self):
        """Gets the MMI parameters for the device.

        Returns
        -------
        :class:`.structs.KSC_MMIParams`
            Options for controlling the mmi.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        mmi_params = KSC_MMIParams()
        self.sdk.SC_GetMMIParamsBlock(self._serial, byref(mmi_params))
        return mmi_params

    def get_mmi_params_ext(self):
        """Get the MMI Parameters for the KCube Display Interface.

        Returns
        -------
        :obj:`int`
            The display intensity, range 0 to 100%.
        :obj:`int`
            The display timeout, range 0 to 480 in minutes (0 is off, otherwise
            the inactivity period before dimming the display).
        :obj:`int`
            The display dimmed intensity, range 0 to 10 (after the timeout
            period the device display will dim).

        Raises
        ------
        ConnectionError
            If not successful.
        """
        intensity = c_int16()
        timeout = c_int16()
        dim_intensity = c_int16()
        self.sdk.SC_GetMMIParamsExt(self._serial, byref(intensity), byref(timeout), byref(dim_intensity))
        return intensity.value, timeout.value, dim_intensity.value

    def get_next_message(self):
        """Get the next Message Queue item. See :mod:`.messages`.

        Returns
        -------
        :obj:`int`
            The message type.
        :obj:`int`
            The message ID.
        :obj:`int`
            The message data.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        message_type = WORD()
        message_id = WORD()
        message_data = DWORD()
        self.sdk.SC_GetNextMessage(self._serial, byref(message_type), byref(message_id), byref(message_data))
        return message_type.value, message_id.value, message_data.value

    def get_operating_mode(self):
        """Gets the Operating Mode.

        Returns
        -------
        :class:`.enums.SC_OperatingModes`
            The current operating mode.
        """
        return SC_OperatingModes(self.sdk.SC_GetOperatingMode(self._serial))

    def get_operating_state(self):
        """Gets the current operating state.

        Returns
        -------
        :class:`.enums.SC_OperatingStates`
            The current operating state.
        """
        return SC_OperatingStates(self.sdk.SC_GetOperatingState(self._serial))

    def get_software_version(self):
        """Gets version number of the device software.

        Returns
        -------
        :obj:`str`
            The device software version.
        """
        return self.to_version(self.sdk.SC_GetSoftwareVersion(self._serial))

    def get_solenoid_state(self):
        """Gets the current solenoid state.

        Returns
        -------
        :class:`.enums.SC_SolenoidStates`
            The current solenoid state.
        """
        return SC_SolenoidStates(self.sdk.SC_GetSolenoidState(self._serial))

    def get_status_bits(self):
        """Get the current status bits.

        This returns the latest status bits received from the device. To get
        new status bits, use :meth:`.request_status` or use the polling
        function, :meth:`.start_polling`

        Returns
        -------
        :obj:`int`
            The status bits from the device.
        """
        return self.sdk.SC_GetStatusBits(self._serial)

    def get_trigger_config_params(self):
        """Get the Trigger Configuration Parameters.

        Returns
        -------
        :class:`.enums.KSC_TriggerPortMode`
            The trigger 1 mode.
        :class:`.enums.KSC_TriggerPortPolarity`
            The trigger 1 polarity.
        :class:`.enums.KSC_TriggerPortMode`
            The trigger 2 mode.
        :class:`.enums.KSC_TriggerPortPolarity`
            The trigger 2 polarity.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        mode1 = c_int16()
        polarity1 = c_int16()
        mode2 = c_int16()
        polarity2 = c_int16()
        self.sdk.SC_GetTriggerConfigParams(self._serial, byref(mode1), byref(polarity1), byref(mode2), byref(polarity2))
        return KSC_TriggerPortMode(mode1.value), KSC_TriggerPortPolarity(polarity1.value), \
               KSC_TriggerPortMode(mode2.value), KSC_TriggerPortPolarity(polarity2.value)

    def get_trigger_config_params_block(self):
        """Gets the trigger configuration parameters block.

        Returns
        -------
        :class:`.structs.KSC_TriggerConfig`
            Options for controlling the trigger configuration.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        params = KSC_TriggerConfig()
        self.sdk.SC_GetTriggerConfigParamsBlock(self._serial, byref(params))
        return params

    def has_last_msg_timer_overrun(self):
        """Queries if the time since the last message has exceeded the
        ``lastMsgTimeout`` set by :meth:`.enable_last_msg_timer`.

        This can be used to determine whether communications with the device is
        still good.

        Returns
        -------
        :obj:`bool`
            :obj:`True` if last message timer has elapsed or
            :obj:`False` if monitoring is not enabled or if time of last message
            received is less than ``lastMsgTimeout``.
        """
        return self.sdk.SC_HasLastMsgTimerOverrun(self._serial)

    def identify(self):
        """Sends a command to the device to make it identify itself."""
        self.sdk.SC_Identify(self._serial)

    def load_settings(self):
        """Update device with stored settings.

        The settings are read from ``ThorlabsDefaultSettings.xml``, which
        gets created when the Kinesis software is installed.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        if not self.sdk.SC_LoadSettings(self._serial):
            self.raise_exception('Error loading the stored settings.')

    def message_queue_size(self):
        """Gets the size of the message queue.

        Returns
        -------
        :obj:`int`
            The number of messages in the queue.
        """
        return self.sdk.SC_MessageQueueSize(self._serial)

    def open(self):
        """Open the device for communication.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_Open(self._serial)

    def persist_settings(self):
        """Persist the devices current settings.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        if not self.sdk.SC_PersistSettings(self._serial):
            self.raise_exception('Error to persist the current settings.')

    def polling_duration(self):
        """Gets the polling loop duration.

        Returns
        -------
        :obj:`int`
            The time between polls in milliseconds or 0 if polling is not active.
        """
        return self.sdk.SC_PollingDuration(self._serial)

    def register_message_callback(self, callback):
        """Registers a callback on the message queue.

        Parameters
        ----------
        callback : :obj:`.callbacks.MotionControlCallback`
            A function to be called whenever messages are received.
        """
        return self.sdk.SC_RegisterMessageCallback(self._serial, callback)

    def request_cycle_params(self):
        """Requests the cycle parameters.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestCycleParams(self._serial)

    def request_digital_outputs(self):
        """Requests the digital output bits.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestDigitalOutputs(self._serial)

    def request_hub_bay(self):
        """Requests the hub bay number this device is fitted to.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestHubBay(self._serial)

    def request_led_switches(self):
        """Requests the LED indicator bits on the cube.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestLEDswitches(self._serial)

    def request_mmi_params(self):
        """Requests the MMI Parameters for the KCube Display Interface.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestMMIParams(self._serial)

    def request_operating_mode(self):
        """Requests the operating mode.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestOperatingMode(self._serial)

    def request_operating_state(self):
        """Requests the operating state.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestOperatingState(self._serial)

    def request_settings(self):
        """Requests that all settings are download from device.

        This function requests that the device upload all it's settings to the DLL.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestSettings(self._serial)

    def request_status(self):
        """Requests the status from the device.

        This needs to be called to get the device to send it's current status bits.
        Note, this is called automatically if ``Polling`` is enabled for the device
        using :meth:`start_polling`.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestStatus(self._serial)

    def request_status_bits(self):
        """Request the status bits which identify the current motor state.

        This needs to be called to get the device to send it's current status bits.
        Note, this is called automatically if ``Polling`` is enabled for the device
        using :meth:`start_polling`.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestStatusBits(self._serial)

    def request_trigger_config_params(self):
        """Requests the Trigger Configuration Parameters.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_RequestTriggerConfigParams(self._serial)

    def set_cycle_params(self, on_time, off_time, num_cycles):
        """Sets the cycle parameters.

        Parameters
        ----------
        on_time : :obj:`int`
            The On Time parameter. Range 250 to 100,000,000 in steps of
            1 milliseconds (0.250s to 10,000s).
        off_time : :obj:`int`
            The Off Time parameter. Range 250 to 100,000,000 in steps of
            1 milliseconds (0.250s to 10,000s).
        num_cycles : :obj:`int`
            The Number of Cycles parameter Range 0 to 1,000,000 where
            0 represent unlimited.

        Raises
        ------
        ValueError
            If any of the input parameters are out of range.
        ConnectionError
            If not successful.
        """
        if on_time > 100000000 or on_time < 250:
            self.raise_exception('Invalid on_time value of {}. Must be 250 <= on_time <= 100e6'.format(on_time))
        if off_time > 100000000 or off_time < 250:
            self.raise_exception('Invalid off_time value of {}. Must be 250 <= off_time <= 100e6'.format(off_time))
        if num_cycles > 1000000 or num_cycles < 0:
            self.raise_exception('Invalid num_cycles value of {}. Must be 0 <= num_cycles <= 1e6'.format(num_cycles))
        self.sdk.SC_SetCycleParams(self._serial, on_time, off_time, num_cycles)

    def set_cycle_params_block(self, cycle_params):
        """Sets the cycle parameters.

        Parameters
        ----------
        cycle_params : :class:`.structs.SC_CycleParameters`
            The new cycle parameters.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        if not isinstance(cycle_params, SC_CycleParameters):
            self.raise_exception('Must pass in a SC_CycleParameters structure')
        self.sdk.SC_SetCycleParamsBlock(self._serial, byref(cycle_params))

    def set_digital_outputs(self, outputs_bits):
        """Sets the digital output bits.

        Parameters
        ----------
        outputs_bits : :obj:`int`
            Bit mask to set the states of the 4 digital output pins.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_SetDigitalOutputs(self._serial, outputs_bits)

    def set_led_switches(self, led_switches):
        """Set the LED indicator bits on the cube.

        Parameters
        ----------
        led_switches : :obj:`int`
            Sum of: 8 to indicate moving 2 to indicate end of track and
            1 to flash on identify command.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_SetLEDswitches(self._serial, led_switches)

    def set_mmi_params(self, display_intensity):
        """Set the MMI Parameters for the KCube Display Interface.

        Deprecated: superceded by :meth:`set_mmi_params_ext`

        Parameters
        ----------
        display_intensity : :obj:`int`
            The display intensity, range 0 to 100%.

        Raises
        ------
        ValueError
            If the value of `display_intensity` is out of range.
        ConnectionError
            If not successful.
        """
        if display_intensity > 100 or display_intensity < 0:
            m = 'Invalid display_intensity value of {}. Must be 0 <= display_intensity <= 100'.format(display_intensity)
            self.raise_exception(m)
        self.sdk.SC_SetMMIParams(self._serial, display_intensity)

    def set_mmi_params_block(self, mmi_params):
        """Sets the MMI parameters for the device.

        Parameters
        ----------
        mmi_params : :class:`.structs.KSC_MMIParams`
            Options for controlling the mmi.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        if not isinstance(mmi_params, KSC_MMIParams):
            self.raise_exception('Must pass in a KSC_MMIParams structure')
        self.sdk.SC_SetMMIParamsBlock(self._serial, byref(mmi_params))

    def set_mmi_params_ext(self, intensity, timeout, dim_intensity):
        """Set the MMI Parameters for the KCube Display Interface.

        Parameters
        ----------
        intensity : :obj:`int`
            The display intensity, range 0 to 100%.
        timeout : :obj:`int`
            The display timeout, range 0 to 480 in minutes (0 is off, otherwise the
            inactivity period before dimming the display).
        dim_intensity : :obj:`int`
            The display dimmed intensity, range 0 to 10 (after the timeout period
            the device display will dim).

        Raises
        ------
        ValueError
            If any of the input parameters are out of range.
        ConnectionError
            If not successful.
        """
        if intensity > 100 or intensity < 0:
            self.raise_exception('Invalid intensity value of {}. Must be 0 <= intensity <= 100'.format(intensity))
        if timeout > 480 or timeout < 0:
            self.raise_exception('Invalid timeout value of {}. Must be 0 <= timeout <= 480'.format(timeout))
        if dim_intensity > 10 or dim_intensity < 0:
            self.raise_exception('Invalid dim_intensity value of {}. Must be 0 <= dim_intensity <= 10'.format(dim_intensity))
        self.sdk.SC_SetMMIParamsExt(self._serial, intensity, timeout, dim_intensity)

    def set_operating_mode(self, mode):
        """Sets the operating mode.

        Parameters
        ----------
        mode : :class:`.enums.SC_OperatingModes`
            The required operating mode as a :class:`~.enums.SC_OperatingModes` enum
            value or member name.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        m = self.convert_to_enum(mode, SC_OperatingModes, prefix='SC_')
        self.sdk.SC_SetOperatingMode(self._serial, m)

    def set_operating_state(self, state):
        """Sets the operating state.

        Parameters
        ----------
        state : :class:`.enums.SC_OperatingStates`
            The required operating state as a :class:`~.enums.SC_OperatingStates` enum
            value or member name.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        s = self.convert_to_enum(state, SC_OperatingStates, prefix='SC_')
        self.sdk.SC_SetOperatingState(self._serial, s)

    def set_trigger_config_params(self, mode1, polarity1, mode2, polarity2):
        """

        Parameters
        ----------
        mode1 : :class:`.enums.KSC_TriggerPortMode`
            The trigger 1 mode as a :class:`~.enums.KSC_TriggerPortMode` enum
            value or member name.
        polarity1 : :class:`.enums.KSC_TriggerPortPolarity`
            The trigger 1 polarity as a :class:`~.enums.KSC_TriggerPortPolarity`
            enum value or member name.
        mode2 : :class:`.enums.KSC_TriggerPortMode`
            The trigger 2 mode as a :class:`~.enums.KSC_TriggerPortMode` enum
            value or member name.
        polarity2 : :class:`.enums.KSC_TriggerPortPolarity`
            The trigger 2 polarity as a :class:`~.enums.KSC_TriggerPortPolarity`
            enum value or member name.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        m1 = self.convert_to_enum(mode1, KSC_TriggerPortMode, prefix='KSC_')
        p1 = self.convert_to_enum(polarity1, KSC_TriggerPortPolarity, prefix='KSC_')
        m2 = self.convert_to_enum(mode2, KSC_TriggerPortMode, prefix='KSC_')
        p2 = self.convert_to_enum(polarity2, KSC_TriggerPortPolarity, prefix='KSC_')
        self.sdk.SC_SetTriggerConfigParams(self._serial, m1, p1, m2, p2)

    def set_trigger_config_params_block(self, trigger_config_params):
        """Sets the trigger configuration parameters block.

        Parameters
        ----------
        trigger_config_params : :class:`.structs.KSC_TriggerConfig`
            Options for controlling the trigger configuration.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        if not isinstance(trigger_config_params, KSC_TriggerConfig):
            self.raise_exception('Must pass in a KSC_TriggerConfig structure')
        self.sdk.SC_SetTriggerConfigParamsBlock(self._serial, byref(trigger_config_params))

    def start_polling(self, milliseconds):
        """Starts the internal polling loop.

        This function continuously requests position and status messages.

        Parameters
        ----------
        milliseconds : :obj:`int`
            The polling rate, in milliseconds.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        self.sdk.SC_StartPolling(self._serial, int(milliseconds))

    def stop_polling(self):
        """Stops the internal polling loop."""
        self.sdk.SC_StopPolling(self._serial)

    def time_since_last_msg_received(self):
        """Gets the time, in milliseconds, since tha last message was received.

        This can be used to determine whether communications with the device is
        still good.

        Returns
        -------
        :obj:`int`
            The time, in milliseconds, since the last message was received.
        """
        ms = c_int64()
        self.sdk.SC_TimeSinceLastMsgReceived(self._serial, byref(ms))
        return ms.value

    def wait_for_message(self):
        """Wait for next Message Queue item. See :mod:`.messages`.

        Returns
        -------
        :obj:`int`
            The message type.
        :obj:`int`
            The message ID.
        :obj:`int`
            The message data.

        Raises
        ------
        ConnectionError
            If not successful.
        """
        message_type = WORD()
        message_id = WORD()
        message_data = DWORD()
        self.sdk.SC_WaitForMessage(self._serial, byref(message_type), byref(message_id), byref(message_data))
        return message_type.value, message_id.value, message_data.value


if __name__ == '__main__':
    # from msl.equipment.resources.thorlabs.kinesis.api_functions import KCube_Solenoid_FCNS
    from msl.equipment.resources.utils import camelcase_to_underscore as convert

    for item in sorted(KCube_Solenoid_FCNS):
        method_name = convert(item[0].split('_')[1])
        args_p = ''
        args_c = ''
        for i, arg in enumerate(item[3]):
            if i == 0 and 'c_char_p' in str(arg[0]):
                args_c += 'self._serial, '
            elif 'PyCPointerType' in str(type(arg[0])):
                args_c += 'byref({}), '.format(convert(arg[1]))
            else:
                a = convert(arg[1])
                args_p += '{}, '.format(a)
                args_c += '{}, '.format(a)

        args_p = args_p[:-2]
        if args_p:
            print('    def {}(self, {}):'.format(method_name, args_p))
        else:
            print('    def {}(self):'.format(method_name))
        print('        return self.sdk.{}({})\n'.format(item[0], args_c[:-2]))


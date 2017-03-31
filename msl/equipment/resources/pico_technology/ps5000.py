from ctypes import c_int8, c_int16, c_int32, c_uint32, c_int64, c_float, c_void_p, byref

from .picoscope import PicoScope
from .pico_status import c_enum
from .picoscope_functions import ps5000Api_funcptrs
from .picoscope_structs import PS5000PwqConditions, PS5000TriggerConditions, PS5000TriggerChannelProperties


class PicoScope5000(PicoScope):

    PS5000_MAX_OVERSAMPLE_8BIT = 256
    PS5000_MAX_VALUE = 32512
    PS5000_MIN_VALUE = -32512
    PS5000_LOST_DATA = -32768
    PS5000_EXT_MAX_VALUE = 32767
    PS5000_EXT_MIN_VALUE = -32767
    MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215
    MAX_DELAY_COUNT = 8388607
    MAX_SIG_GEN_BUFFER_SIZE = 8192
    MIN_SIG_GEN_BUFFER_SIZE = 10
    MIN_DWELL_COUNT = 10
    # MAX_SWEEPS_SHOTS = ((1 << 30) - 1)
    PS5000_SINE_MAX_FREQUENCY = 20000000.
    PS5000_SQUARE_MAX_FREQUENCY = 20000000.
    PS5000_TRIANGLE_MAX_FREQUENCY = 20000000.
    PS5000_SINC_MAX_FREQUENCY = 20000000.
    PS5000_RAMP_MAX_FREQUENCY = 20000000.
    PS5000_HALF_SINE_MAX_FREQUENCY = 20000000.
    PS5000_GAUSSIAN_MAX_FREQUENCY = 20000000.
    PS5000_MIN_FREQUENCY = 0.03

    def __init__(self, record):
        PicoScope.__init__(self, record, ps5000Api_funcptrs)
        raise NotImplementedError('The {} class has not been tested'.format(self.__class__.__name__))

    def close_unit(self):
        self.sdk.ps5000CloseUnit(self._handle)

    def flash_led(self, start):
        self.sdk.ps5000FlashLed(self._handle, start)

    def get_max_down_sample_ratio(self, no_of_unaggreated_samples, down_sample_ratio_mode, segment_index):
        max_down_sample_ratio = c_uint32()
        self.sdk.ps5000GetMaxDownSampleRatio(self._handle, no_of_unaggreated_samples,
                                             byref(max_down_sample_ratio), down_sample_ratio_mode, segment_index)
        return max_down_sample_ratio.value

    def get_streaming_latest_values(self, lp_ps):
        p_parameter = c_void_p()
        self.sdk.ps5000GetStreamingLatestValues(self._handle, lp_ps, byref(p_parameter))
        return p_parameter.value

    def get_timebase(self, timebase, no_samples, oversample, segment_index):
        time_interval_nanoseconds = c_int32()
        max_samples = c_int32()
        self.sdk.ps5000GetTimebase(self._handle, timebase, no_samples, byref(time_interval_nanoseconds),
                                   oversample, byref(max_samples), segment_index)
        return time_interval_nanoseconds.value, max_samples.value

    def get_timebase2(self, timebase, no_samples, oversample, segment_index):
        time_interval_nanoseconds = c_float()
        max_samples = c_int32()
        self.sdk.ps5000GetTimebase2(self._handle, timebase, no_samples, byref(time_interval_nanoseconds),
                                    oversample, byref(max_samples), segment_index)
        return time_interval_nanoseconds.value, max_samples.value

    def get_trigger_time_offset(self, segment_index):
        time_upper = c_uint32()
        time_lower = c_uint32()
        time_units = c_enum()
        self.sdk.ps5000GetTriggerTimeOffset(self._handle, byref(time_upper), byref(time_lower),
                                            byref(time_units), segment_index)
        return time_upper.value, time_lower.value, time_units.value

    def get_trigger_time_offset64(self, segment_index):
        time = c_int64()
        time_units = c_enum()
        self.sdk.ps5000GetTriggerTimeOffset64(self._handle, byref(time), byref(time_units), segment_index)
        return time.value, time_units.value

    def get_unit_info(self, string_length, info):
        string = c_int8()
        required_size = c_int16()
        self.sdk.ps5000GetUnitInfo(self._handle, byref(string), string_length, byref(required_size), info)
        return string.value, required_size.value

    def get_values(self, start_index, down_sample_ratio, down_sample_ratio_mode, segment_index):
        no_of_samples = c_uint32()
        overflow = c_int16()
        self.sdk.ps5000GetValues(self._handle, start_index, byref(no_of_samples), down_sample_ratio,
                                 down_sample_ratio_mode, segment_index, byref(overflow))
        return no_of_samples.value, overflow.value

    def get_values_async(self, start_index, no_of_samples, down_sample_ratio, down_sample_ratio_mode, segment_index):
        lp_data_ready = c_void_p()
        p_parameter = c_void_p()
        self.sdk.ps5000GetValuesAsync(self._handle, start_index, no_of_samples, down_sample_ratio,
                                      down_sample_ratio_mode, segment_index, byref(lp_data_ready), byref(p_parameter))
        return lp_data_ready.value, p_parameter.value

    def get_values_bulk(self, from_segment_index, to_segment_index):
        no_of_samples = c_uint32()
        overflow = c_int16()
        self.sdk.ps5000GetValuesBulk(self._handle, byref(no_of_samples), from_segment_index,
                                     to_segment_index, byref(overflow))
        return no_of_samples.value, overflow.value

    def get_values_trigger_time_offset_bulk(self, from_segment_index, to_segment_index):
        times_upper = c_uint32()
        times_lower = c_uint32()
        time_units = c_enum()
        self.sdk.ps5000GetValuesTriggerTimeOffsetBulk(self._handle, byref(times_upper), byref(times_lower),
                                                      byref(time_units), from_segment_index, to_segment_index)
        return times_upper.value, times_lower.value, time_units.value

    def get_values_trigger_time_offset_bulk64(self, from_segment_index, to_segment_index):
        times = c_int64()
        time_units = c_enum()
        self.sdk.ps5000GetValuesTriggerTimeOffsetBulk64(self._handle, byref(times), byref(time_units),
                                                        from_segment_index, to_segment_index)
        return times.value, time_units.value

    def is_led_flashing(self):
        status = c_int16()
        self.sdk.ps5000IsLedFlashing(self._handle, byref(status))
        return status.value

    def is_ready(self):
        ready = c_int16()
        self.sdk.ps5000IsReady(self._handle, byref(ready))
        return ready.value

    def is_trigger_or_pulse_width_qualifier_enabled(self):
        trigger_enabled = c_int16()
        pulse_width_qualifier_enabled = c_int16()
        self.sdk.ps5000IsTriggerOrPulseWidthQualifierEnabled(self._handle, byref(trigger_enabled),
                                                             byref(pulse_width_qualifier_enabled))
        return trigger_enabled.value, pulse_width_qualifier_enabled.value

    def memory_segments(self, n_segments):
        n_max_samples = c_int32()
        self.sdk.ps5000MemorySegments(self._handle, n_segments, byref(n_max_samples))
        return n_max_samples.value

    def no_of_streaming_values(self):
        no_of_values = c_uint32()
        self.sdk.ps5000NoOfStreamingValues(self._handle, byref(no_of_values))
        return no_of_values.value

    def open_unit(self):
        handle = c_int16()
        self.sdk.ps5000OpenUnit(byref(handle))
        if handle.value > 0:
            self._handle = handle
        return handle.value

    def open_unit_async(self):
        status = c_int16()
        self.sdk.ps5000OpenUnitAsync(byref(status))
        return status.value

    def open_unit_progress(self):
        handle = c_int16()
        progress_percent = c_int16()
        complete = c_int16()
        self.sdk.ps5000OpenUnitProgress(byref(handle), byref(progress_percent), byref(complete))
        if handle.value > 0:
            self._handle = handle
        return 100 if complete.value else progress_percent.value

    def ping_unit(self):
        self.sdk.ps5000PingUnit(self._handle)

    def run_block(self, no_of_pre_trigger_samples, no_of_post_trigger_samples, timebase, oversample,
                  segment_index, lp_ready):
        time_indisposed_ms = c_int32()
        p_parameter = c_void_p()
        self.sdk.ps5000RunBlock(self._handle, no_of_pre_trigger_samples, no_of_post_trigger_samples,
                                timebase, oversample, byref(time_indisposed_ms), segment_index, lp_ready,
                                byref(p_parameter))
        return time_indisposed_ms.value, p_parameter.value

    def run_streaming(self, sample_interval_time_units, max_pre_trigger_samples, max_post_pre_trigger_samples,
                      auto_stop, down_sample_ratio, overview_buffer_size):
        sample_interval = c_uint32()
        self.sdk.ps5000RunStreaming(self._handle, byref(sample_interval), sample_interval_time_units,
                                    max_pre_trigger_samples, max_post_pre_trigger_samples, auto_stop,
                                    down_sample_ratio, overview_buffer_size)
        return sample_interval.value

    def set_channel(self, channel, enabled, dc, range_):
        self.sdk.ps5000SetChannel(self._handle, channel, enabled, dc, range_)

    def set_data_buffer(self, channel, buffer_lth):
        buffer = c_int16()
        self.sdk.ps5000SetDataBuffer(self._handle, channel, byref(buffer), buffer_lth)
        return buffer.value

    def set_data_buffer_bulk(self, channel, buffer_lth, waveform):
        buffer = c_int16()
        self.sdk.ps5000SetDataBufferBulk(self._handle, channel, byref(buffer), buffer_lth, waveform)
        return buffer.value

    def set_data_buffers(self, channel, buffer_lth):
        buffer_max = c_int16()
        buffer_min = c_int16()
        self.sdk.ps5000SetDataBuffers(self._handle, channel, byref(buffer_max), byref(buffer_min), buffer_lth)
        return buffer_max.value, buffer_min.value

    def set_ets(self, mode, ets_cycles, ets_interleave):
        sample_time_picoseconds = c_int32()
        self.sdk.ps5000SetEts(self._handle, mode, ets_cycles, ets_interleave, byref(sample_time_picoseconds))
        return sample_time_picoseconds.value

    def set_ets_time_buffer(self, buffer_lth):
        buffer = c_int64()
        self.sdk.ps5000SetEtsTimeBuffer(self._handle, byref(buffer), buffer_lth)
        return buffer.value

    def set_ets_time_buffers(self, buffer_lth):
        time_upper = c_uint32()
        time_lower = c_uint32()
        self.sdk.ps5000SetEtsTimeBuffers(self._handle, byref(time_upper), byref(time_lower), buffer_lth)
        return time_upper.value, time_lower.value

    def set_no_of_captures(self, n_captures):
        self.sdk.ps5000SetNoOfCaptures(self._handle, n_captures)

    def set_pulse_width_qualifier(self, n_conditions, direction, lower, upper, type_):
        conditions = PS5000PwqConditions()
        self.sdk.ps5000SetPulseWidthQualifier(self._handle, byref(conditions), n_conditions, direction, lower,
                                              upper, type_)
        return conditions.value

    def set_sig_gen_arbitrary(self, offset_voltage, pk_to_pk, start_delta_phase, stop_delta_phase,
                              delta_phase_increment, dwell_count, arbitrary_waveform_size, sweep_type, white_noise,
                              index_mode, shots, sweeps, trigger_type, trigger_source, ext_in_threshold):
        arbitrary_waveform = c_int16()
        self.sdk.ps5000SetSigGenArbitrary(self._handle, offset_voltage, pk_to_pk, start_delta_phase,
                                          stop_delta_phase, delta_phase_increment, dwell_count,
                                          byref(arbitrary_waveform), arbitrary_waveform_size, sweep_type,
                                          white_noise, index_mode, shots, sweeps, trigger_type, trigger_source,
                                          ext_in_threshold)
        return arbitrary_waveform.value

    def set_sig_gen_built_in(self, offset_voltage, pk_to_pk, wave_type, start_frequency, stop_frequency,
                             increment, dwell_time, sweep_type, white_noise, shots, sweeps, trigger_type,
                             trigger_source, ext_in_threshold):
        self.sdk.ps5000SetSigGenBuiltIn(self._handle, offset_voltage, pk_to_pk, wave_type, start_frequency,
                                        stop_frequency, increment, dwell_time, sweep_type, white_noise, shots,
                                        sweeps, trigger_type, trigger_source, ext_in_threshold)

    def set_sig_gen_built_in_v2(self, offset_voltage, pk_to_pk, wave_type, start_frequency, stop_frequency,
                                increment, dwell_time, sweep_type, white_noise, shots, sweeps, trigger_type,
                                trigger_source, ext_in_threshold):
        self.sdk.ps5000SetSigGenBuiltInV2(self._handle, offset_voltage, pk_to_pk, wave_type, start_frequency,
                                          stop_frequency, increment, dwell_time, sweep_type, white_noise, shots,
                                          sweeps, trigger_type, trigger_source, ext_in_threshold)

    def set_simple_trigger(self, enable, source, threshold, direction, delay, auto_trigger_ms):
        self.sdk.ps5000SetSimpleTrigger(self._handle, enable, source, threshold, direction, delay, auto_trigger_ms)

    def set_trigger_channel_conditions(self, n_conditions):
        conditions = PS5000TriggerConditions()
        self.sdk.ps5000SetTriggerChannelConditions(self._handle, byref(conditions), n_conditions)
        return conditions.value

    def set_trigger_channel_directions(self, channel_a, channel_b, channel_c, channel_d, ext, aux):
        self.sdk.ps5000SetTriggerChannelDirections(self._handle, channel_a, channel_b, channel_c, channel_d, ext, aux)

    def set_trigger_channel_properties(self, n_channel_properties, aux_output_enable, auto_trigger_milliseconds):
        channel_properties = PS5000TriggerChannelProperties()
        self.sdk.ps5000SetTriggerChannelProperties(self._handle, byref(channel_properties), n_channel_properties,
                                                   aux_output_enable, auto_trigger_milliseconds)
        return channel_properties.value

    def set_trigger_delay(self, delay):
        self.sdk.ps5000SetTriggerDelay(self._handle, delay)

    def sig_gen_arbitrary_min_max_values(self):
        min_arbitrary_waveform_value = c_int16()
        max_arbitrary_waveform_value = c_int16()
        min_arbitrary_waveform_size = c_uint32()
        max_arbitrary_waveform_size = c_uint32()
        self.sdk.ps5000SigGenArbitraryMinMaxValues(self._handle, byref(min_arbitrary_waveform_value),
                                                   byref(max_arbitrary_waveform_value),
                                                   byref(min_arbitrary_waveform_size),
                                                   byref(max_arbitrary_waveform_size))
        return (min_arbitrary_waveform_value.value, max_arbitrary_waveform_value.value,
                min_arbitrary_waveform_size.value, max_arbitrary_waveform_size.value)

    def sig_gen_frequency_to_phase(self, frequency, index_mode, buffer_length):
        phase = c_uint32()
        self.sdk.ps5000SigGenFrequencyToPhase(self._handle, frequency, index_mode, buffer_length, byref(phase))
        return phase.value

    def sig_gen_software_control(self, state):
        self.sdk.ps5000SigGenSoftwareControl(self._handle, state)

    def stop(self):
        self.sdk.ps5000Stop(self._handle)

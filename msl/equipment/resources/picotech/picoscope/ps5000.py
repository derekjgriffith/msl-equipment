"""
A wrapper around the PicoScope ps5000 SDK.
"""
from .picoscope_api import PicoScopeApi
from .functions import ps5000Api_funcptrs


class PicoScope5000(PicoScopeApi):

    MAX_OVERSAMPLE_8BIT = 256
    MAX_VALUE = 32512
    MIN_VALUE = -32512
    LOST_DATA = -32768
    EXT_MAX_VALUE = 32767
    EXT_MIN_VALUE = -32767
    MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215
    MAX_DELAY_COUNT = 8388607
    MAX_SIG_GEN_BUFFER_SIZE = 8192
    MIN_SIG_GEN_BUFFER_SIZE = 10
    MIN_DWELL_COUNT = 10
    MAX_SWEEPS_SHOTS = ((1 << 30) - 1)
    SINE_MAX_FREQUENCY = 20000000.
    SQUARE_MAX_FREQUENCY = 20000000.
    TRIANGLE_MAX_FREQUENCY = 20000000.
    SINC_MAX_FREQUENCY = 20000000.
    RAMP_MAX_FREQUENCY = 20000000.
    HALF_SINE_MAX_FREQUENCY = 20000000.
    GAUSSIAN_MAX_FREQUENCY = 20000000.
    MIN_FREQUENCY = 0.03

    # EXT_MAX_VOLTAGE = ?

    def __init__(self, record):
        """A wrapper around the PicoScope ps5000 SDK.

        Parameters
        ----------
        record : :class:`~msl.equipment.record_types.EquipmentRecord`
            An equipment record from an **Equipment-Register** 
            :class:`~msl.equipment.database.Database`.            
        """
        PicoScopeApi.__init__(self, record, ps5000Api_funcptrs)
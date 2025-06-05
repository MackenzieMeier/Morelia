from Morelia.packet.data.data_packet import DataPacket
from Morelia.signal import DigitalSignal

import Morelia.packet.conversion as conv

class DataPacket8206HRTest(DataPacket):

    __slots__ = ('_ch1', '_ch2', '_ch3')
    def __init__(self, raw_packet: bytes) -> None:
        super().__init__(raw_packet, 16)

        self._ch1 = None
        self._ch2 = None
        self._ch3 = None

    
    @property
    def ch1(self) -> int:
        if self._ch1 is None:
            self._ch1 = DataPacket8206HRTest.get_primary_channel_value(self._raw_packet[5:7])
        return self._ch1

    @property
    def ch2(self) -> int:
        if self._ch2 is None:
            self._ch2 = DataPacket8206HRTest.get_primary_channel_value(self._raw_packet[7:9])
        return self._ch2

    @property
    def ch3(self) -> int:
        if self._ch3 is None:
            self._ch3 = DataPacket8206HRTest.get_primary_channel_value(self._raw_packet[9:11])
        return self._ch3
 
    @staticmethod
    def get_primary_channel_value(raw_value: bytes) -> float:
        # print("Raw Values: " + str(raw_value))
        # calculate voltage 
        value = conv.binary_bytes_to_int(raw_value, conv.Endianness.LITTLE)
        voltage_adc = ( value / 65535.0 ) * 5 #4.096 # V
        # total_gain = preamp_gain * 50.2918
        real_voltage = ( voltage_adc -  2.50) #2.048/ total_gain
        # print("Real Voltage: " + str(real_voltage * 1E6))
        return round(real_voltage * 1E6, 12)


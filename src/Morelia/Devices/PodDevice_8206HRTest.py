# local imports 
from Morelia.Devices import AquisitionDevice, Pod
from Morelia.packet.data import DataPacket8206HRTest
from Morelia.packet import ControlPacket
from Morelia.Commands import CommandSet
import Morelia.packet.conversion as conv

from functools import partial

# authorship
__author__      = "Mackenzie Meier"
__maintainer__  = "Mackenzie Meier"
__credits__     = ["Mackenzie Meier", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2025, Mackenzie Meier"
__email__       = "sales@pinnaclet.com"

class Pod8206HRTest(AquisitionDevice) :
    """
    POD_8206HRTest handles communication using an 8206HR Testing Pod device

    Attributes:

    """

    # ------------ DUNDER ------------           ------------------------------------------------------------------------------------------------------------------------

    def __init__(self, port: str|int, baudrate:int=9600, device_name: str | None =  None) -> None :
        """Runs when an instance is constructed. It runs the parent's initialization. Then it updates \
        the _commands to contain the appropriate commands for an 8206-HR Test POD device. 

        Args:
            port (str | int): Serial port to be opened. Used when initializing the COM_io instance.
            baudrate (int, optional): Integer baud rate of the opened serial port. Used when initializing \
                the COM_io instance. Defaults to 9600.

        """

        # initialize POD Basics
        super().__init__(port, 2000, baudrate, device_name) 
        # get constants for adding commands
        U8 = Pod.GetU(8)
        U16 = Pod.GetU(16)
        B4  = 8
        self._commands.RemoveCommand(5)  # STATUS
        self._commands.RemoveCommand(9)  # ID
        self._commands.RemoveCommand(10) # SAMPLE RATE
        self._commands.RemoveCommand(11) # BINARY
        # add device specific commands
        self._commands.AddCommand(136, 'SET SINE WAVE',     (0,),   (0,),   False,  'Starts sine wave with current frequency and amplitude on current channel')
        self._commands.AddCommand(138, 'GET FREQ',          (0,),   (U16,),   False,  'Gets the frequency of the current sine wave')
        self._commands.AddCommand(139, 'SET FREQ',          (U16,),   (0,),   False,  'Sets the frequency of the current sine wave')
        self._commands.AddCommand(140, 'GET AMP',           (0,),   (U16,),   False,  'Gets the amplitude of the current sine wave')
        self._commands.AddCommand(141, 'SET AMP',           (U16,),   (0,),   False,  'Sets the amplitude of the current sine wave')
        self._commands.AddCommand(142, 'GET DIGITAL IO',    (U8,),   (U8,),   False,  'Gets the value of the digital pin')
        self._commands.AddCommand(143, 'SET DIGITAL IO',    (U8,U8,),   (0,),   False,  'Sets the value of the digital pin')
        self._commands.AddCommand(146, 'SET CHANNEL',       (U8,),   (0,),   False,  'Sets the channel for current sine wave')
        self._commands.AddCommand(180, 'BINARY4 DATA ',     (0,),    (B4,),  True,   'Binary4 data packets, enabled by using the STREAM command with a \'1\' argument.') # see _Read_Binary()

    # ------------ OVERWRITE ------------           ------------------------------------------------------------------------------------------------------------------------


    # def ReadPODpacket(self, validateChecksum: bool = True, timeout_sec: int | float = 5) -> Packet:
    #     """Reads a complete POD packet, either in standard or binary format, beginning with STX and \
    #     ending with ETX. Reads first STX and then starts recursion. 

    #     Args:
    #         validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
    #             skip validation. Defaults to True.
    #         timeout_sec (int|float, optional): Time in seconds to wait for serial data. \
    #             Defaults to 5. 

    #     Returns:
    #         Packet: POD packet beginning with STX and ending with ETX. This may be a \
    #             standard packet, binary packet, or an unformatted packet (STX+something+ETX). 
    #     """
    #     packet: Packet = super().ReadPODpacket(validateChecksum, timeout_sec)
    #     # check for special packets
    #     #if(isinstance(packet, PacketStandard)) : 
    #         #if(packet.CommandNumber() == 106) : # 106, 'GET TTL PORT'
    #             #packet.SetCustomPayload(self._TranslateTTLbyte_ASCII, (packet.payload,))
    #     # return packet
    #     return packet

    def _Read_Binary(self, prePacket: bytes, validateChecksum:bool=True) -> DataPacket8206HRTest :
        """After receiving the prePacket, it reads the 8 bytes(TTL+channels) and then reads to ETX \
        (checksum+ETX). 

        Args:
            prePacket (bytes): Bytes string containing the beginning of a POD packet: STX (1 byte) \
                + command number (4 bytes).
            validateChecksum (bool, optional): Set to True to validate the checksum. Set to False to \
                skip validation. Defaults to True.

        Raises:
            Exception: Bad checksum for binary POD packet read.

        Returns:
            Packet_Binary4: Binary4 POD packet.
        """

        # ------------------------------------------------------------		
        # Binary 4 Data Format
        # ------------------------------------------------------------		
        # Byte    Value	        Format      Description 
        # ------------------------------------------------------------		
        # 0	    0x02	        Binary		STX
        # 1	    0	            ASCII		Command Number Byte 0
        # 2	    0	            ASCII		Command Number Byte 1
        # 3	    B	            ASCII		Command Number Byte 2
        # 4	    4	            ASCII		Command Number Byte 3
        # 5	    Ch1 LSB	        Binary		Least significant byte of the Channel 0 (EEG1) value
        # 6	    Ch1 MSB	        Binary		Most significant byte of the Channel 0 (EEG1) value
        # 7	    Ch2 LSB	        Binary		Channel 1 / EEG2 LSB
        # 8     Ch2 MSB	        Binary		Channel 1 / EEG2 MSB
        # 9     Ch3 LSB	        Binary		Channel 2 / EEG3/EMG LSB
        # 10    Ch3 MSB	        Binary		Channel 2 / EEG3/EMG MSB
        # 11    Checksum MSB	ASCII		MSB of checksum
        # 12    Checksum LSB	ASCII		LSB of checkxum
        # 13    0x03	        Binary		ETX
        # ------------------------------------------------------------
        
        # get prepacket + packet number, TTL, and binary ch0-2 (these are all binary, do not search for STX/ETX) + read csm and ETX (3 bytes) (these are ASCII, so check for STX/ETX)
        packet = prePacket + self._port.Read(6) + self._Read_ToETX(validateChecksum=validateChecksum)
        # check if checksum is correct 
        if(validateChecksum):
            if(not self._ValidateChecksum(packet) ) :
                raise Exception('Bad checksum for binary POD packet read.')
        # return complete variable length binary packet
        return DataPacket8206HRTest(packet)
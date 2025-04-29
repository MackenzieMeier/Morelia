# local imports 
from Morelia.Devices import AquisitionDevice, Pod
from Morelia.packet.data import DataPacket8206HR
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

    def __init__(self, port: str|int, baudrate = 9600) -> None :
        """Runs when an instance is constructed. It runs the parent's initialization. Then it updates \
        the _commands to contain the appropriate commands for an 8206-HR Test POD device. 

        Args:
            port (str | int): Serial port to be opened. Used when initializing the COM_io instance.
            baudrate (int, optional): Integer baud rate of the opened serial port. Used when initializing \
                the COM_io instance. Defaults to 9600.

        """

        # initialize POD Basics
        super().__init__(port, baudrate=baudrate)
        # get constants for adding commands
        U8 = Pod.GetU(8)
        U16 = Pod.GetU(16)

        # add device specific commands
        self._commands.AddCommand(136, 'SET SINE WAVE',     (0,),   (0,),   False,  'Starts sine wave with current frequency and amplitude on current channel')
        self._commands.AddCommand(138, 'GET FREQ',          (0,),   (U16,),   False,  'Gets the frequency of the current sine wave')
        self._commands.AddCommand(139, 'SET FREQ',          (U16,),   (0,),   False,  'Sets the frequency of the current sine wave')
        self._commands.AddCommand(140, 'GET AMP',           (0,),   (U16,),   False,  'Gets the amplitude of the current sine wave')
        self._commands.AddCommand(141, 'SET AMP',           (U16,),   (0,),   False,  'Sets the amplitude of the current sine wave')
        self._commands.AddCommand(142, 'GET DIGITAL IO',    (U8,),   (U8,),   False,  'Gets the value of the digital pin')
        self._commands.AddCommand(143, 'SET DIGITAL IO',    (U8,U8,),   (0,),   False,  'Sets the value of the digital pin')
        self._commands.AddCommand(146, 'SET CHANNEL',       (U8,),   (0,),   False,  'Sets the channel for current sine wave')
        

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
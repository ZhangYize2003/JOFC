"""
This module provides functions to handle communication with an Arduino device over a serial connection.
It includes serial communication functions, user input parsing, and routines.

Functions:
    receivePacket(exitFlag: Event = _EXIT_EVENT) -> TPacket:
        Receives a packet from the Arduino over the serial connection.
    sendPacket(packetType: TPacketType, commandType: TCommandType, params: list):
        Sends a packet to the Arduino over the serial connection.
    printPacket(packet: TPacket):
        Prints the details of a packet.
    parseParams(p: list, num_p: int, inputMessage: str) -> list:
        Parses parameters for a command.
    parseUserInput(input_str: str, exitFlag: Event = _EXIT_EVENT):
        Parses user input and sends the corresponding packet to the Arduino.
    waitForHelloRoutine():
        Waits for a hello response from the Arduino.
    run_keypress_control(exitFlag: Event = _EXIT_EVENT):
        Implements a live keypress-based control mode (wasd_test integration).
"""

from threading import Event
from time import sleep
from .alex_control_serial import startSerial, readSerial, writeSerial, closeSerial
from .alex_control_serialize import serialize, deserialize
from .alex_control_constants import TCommandType, TPacketType, TResponseType, TPacket, PAYLOAD_PARAMS_COUNT, PAYLOAD_PACKET_SIZE
from .alex_control_constants import TComms, TResultType, COMMS_MAGIC_NUMBER, COMMS_PACKET_SIZE

# This default event is used to signal that the program should exit.
# Pass your own event to the parseUserInput() and receivePacket() functions if you want to control the exit behavior.
_EXIT_EVENT = Event()


############################
## SERIAL COMMS FUNCTIONS ##
############################
def receivePacket(exitFlag: Event = _EXIT_EVENT):
    """
    Receives a packet from the serial interface.

    This function continuously reads from the serial interface until a complete packet
    is received or the exit flag is set. The packet is then deserialized and returned.

    Args:
        exitFlag (Event, optional): An event flag to signal when to exit the loop. Defaults to _EXIT_EVENT.

    Returns:
        TPacket: The deserialized packet if received and valid.
        None: If the packet is invalid or if the exit flag is set before a complete packet is received.
    """
    global ack_received
    target_packet_size = COMMS_PACKET_SIZE
    buffer = bytearray(target_packet_size)
    buffer_size = 0
    while not exitFlag.is_set():
        res_size, res = readSerial(target_packet_size - buffer_size)
        # print(f"Received {res_size} bytes") if VERBOSE else None
        if res_size != 0:
            buffer[buffer_size:buffer_size + res_size] = res
            buffer_size += res_size
        if buffer_size == target_packet_size:
            # Deserialize packet.
            res_status, payload = deserialize(buffer)
            if res_status == TResultType.PACKET_OK:
                ack_received = True
                return TPacket.from_buffer(payload)
            else:
                handleError(res_status)
                ack_received = False
                return None
    return None


def sendPacket(packetType: TPacketType, commandType: TCommandType, params: []):
    """
    Sends a packet with the specified type, command, and parameters.

    Args:
        packetType (TPacketType): The type of the packet to send.
        commandType (TCommandType): The command type of the packet.
        params (list): A list of parameters to include in the packet.

    Returns:
        None
    """
    global ack_received
    if not ack_received:
        print("Cannot send packet: Previous packet not acknowledged.")
        return
    ack_received = False
    packet_to_send = TPacket()
    packet_to_send.packetType = int(packetType.value) if isinstance(packetType, TPacketType) else int(packetType)
    packet_to_send.command = int(commandType.value) if isinstance(commandType, TCommandType) else int(commandType)
    print(params)
    if params != []:
        packet_to_send.params[0:PAYLOAD_PARAMS_COUNT] = [int(x) for x in params]
    print(params)
    to_comms = serialize(packet_to_send)
    # print(f"Sending Packet.\nSize: {len(to_comms)}\nData: {to_comms}") if VERBOSE else None
    writeSerial(to_comms)


def handleError(res_status: TResultType):
    """
    Handles errors based on the result status type.

    Args:
        res_status (TResultType): The result status type indicating the error condition.

    Returns:
        None

    Prints:
        - "ERROR: Received Bad Packet from Arduino" if the result status is PACKET_BAD.
        - "ERROR: Received Bad Checksum from Arduino" if the result status is PACKET_CHECKSUM_BAD.
        - "ERROR: Unknown Error in Processing Packet" for any other result status.
    """
    if res_status == TResultType.PACKET_BAD:
        print("ERROR: Received Bad Packet from Arduino")
    elif res_status == TResultType.PACKET_CHECKSUM_BAD:
        print("ERROR: Received Bad Checksum from Arduino")
    else:
        print("ERROR: Unknown Error in Processing Packet")


def printPacket(packet: TPacket):
    """
    Prints the details of a TPacket object.

    Args:
        packet (TPacket): The packet object to be printed.
    """
    print(f"Packet Type: {packet.packetType}")
    print(f"Command: {packet.command}")
    print(f"Data: {packet.data}")
    params = [x for x in packet.params]
    print(f"Params: {params}")


##########################
## USER INPUT FUNCTIONS ##
##########################

def parseParams(p, num_p, inputMessage):
    """
    Parses and returns a list of parameters based on the given input.
    """
    if num_p == 0:
        return [0] * PAYLOAD_PARAMS_COUNT
    elif len(p) >= num_p:
        return p[:num_p] + [0] * (PAYLOAD_PARAMS_COUNT - num_p)
    elif len(p) < num_p and inputMessage is not None:
        params_str = input(inputMessage)
        split_input = params_str.split(" ")
        return parseParams(split_input, num_p, None)
    else:
        return None


def parseUserInput(input_str: str, exitFlag: Event = _EXIT_EVENT):
    """
    Parses the user input string and executes the corresponding command.
    """
    split_input = [x for x in input_str.strip().split(" ") if x != ""]
    if len(split_input) < 1:
        return print(f"{input_str} is not a valid command")
    command = split_input[0]
    packetType = TPacketType.PACKET_TYPE_COMMAND

    if command == "f":
        commandType = TCommandType.COMMAND_FORWARD
        params = parseParams(split_input[1:], 2, "Enter distance in cm (e.g. 50) and power in % (e.g. 75) separated by space.\n")
        return (packetType, commandType, params) if params is not None else print("Invalid Parameters")
    elif command == "b":
        commandType = TCommandType.COMMAND_REVERSE
        params = parseParams(split_input[1:], 2, "Enter distance in cm (e.g. 50) and power in % (e.g. 75) separated by space.\n")
        return (packetType, commandType, params) if params is not None else print("Invalid Parameters")
    elif command == "l":
        commandType = TCommandType.COMMAND_TURN_LEFT
        params = parseParams(split_input[1:], 2, "Enter degrees to turn left (e.g. 90) and power in % (e.g. 75) separated by space.\n")
        return (packetType, commandType, params) if params is not None else print("Invalid Parameters")
    elif command == "r":
        commandType = TCommandType.COMMAND_TURN_RIGHT
        params = parseParams(split_input[1:], 2, "Enter degrees to turn right (e.g. 90) and power in % (e.g. 75) separated by space.\n")
        return (packetType, commandType, params) if params is not None else print("Invalid Parameters")
    elif command == "s":
        commandType = TCommandType.COMMAND_STOP
        params = parseParams(split_input[1:], 0, None)
        return (packetType, commandType, params)
    elif command == "c":
        commandType = TCommandType.COMMAND_CLEAR_STATS
        params = parseParams(split_input[1:], 0, None)
        return (packetType, commandType, params)
    elif command == "g":
        commandType = TCommandType.COMMAND_GET_STATS
        params = parseParams(split_input[1:], 0, None)
        return (packetType, commandType, params)
    elif command == "q":
        print("Exiting! Setting Exit Flag...")
        print("\n==============CLEANING UP==============")
        _EXIT_EVENT.set()
        return None
    else:
        return print(f"{command} is not a valid command")


###########################
######## Routines #########
###########################
def waitForHelloRoutine():
    """
    Sends a "Hello" packet to the Arduino and waits for a response.
    """
    print("sending packet")
    sendPacket(TPacketType.PACKET_TYPE_HELLO, TCommandType.COMMAND_STOP, [0] * PAYLOAD_PARAMS_COUNT)
    print("sent packet")
    packet = receivePacket()
    print("got packet")
    if packet is not None:
        packetType = packet.packetType
        res_type = packet.command
        if (packetType == TPacketType.PACKET_TYPE_RESPONSE.value and
                res_type == TResponseType.RESP_OK.value):
            print("Received Hello Response")
            return
    raise Exception(f"Failed to receive proper response from Arduino: Packet Type Mismatch {packetType}")


##################################
## KEY PRESS BASED CONTROL MODE ##
##################################
import msvcrt

ack_received = True


def get_speed_label(speed):
    return {
        1: "park",
        2: "med",
        3: "fast"
    }.get(speed, "unknown")


def run_keypress_control(exitFlag=_EXIT_EVENT):
    """
    Realtime keypress-based control mode.
    Allows user to press w/a/s/d with fixed movement (2 cm) and turning (6 degrees),
    and adjust power with 1/2/3.
    Press ESC to exit.
    """
    # Fixed parameters for movement and turning
    move_distance = "2"  # Move 2 cm each time w/s is pressed
    turn_angle = "6"     # Turn 6 degrees each time a/d is pressed

    # Power levels as strings
    power_map = {
        '1': "50",  # 50% power
        '2': "75",  # 75% power
        '3': "100"  # 100% power
    }

    # Default speed (50% power)
    speed = power_map['1']  # Default to "50% power"

    print("Running live keypress control mode.")
    print("Press w/s to move 2 cm. Press a/d to turn 6 degrees. Press 1/2/3 to set power (50%, 75%, 100%). Press ESC to exit.")
    print(f"Speed = {speed}%")

    while not exitFlag.is_set():
        if not msvcrt.kbhit():
            continue

        ch = msvcrt.getch()
        try:
            key = ch.decode('utf-8').lower()
        except UnicodeDecodeError:
            continue

        t_list = [0] * 16
        # Adjust speed based on 1/2/3
        if key in ['1', '2', '3']:
            speed = power_map[key]
            print(f"Speed = {speed}%")

        # Move forward (w) or backward (s) with fixed distance
        elif key == 'w':
            print(f"Move forward {move_distance} cm at {speed}% power")
            t_list[0] = move_distance
            t_list[1] = speed
            sendPacket(TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_FORWARD, t_list)
        elif key == 's':
            print(f"Move backward {move_distance} cm at {speed}% power")
            t_list[0] = move_distance
            t_list[1] = speed
            sendPacket(TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_REVERSE, t_list)

        # Turn left (a) or right (d) with fixed angle
        elif key == 'a':
            print(f"Turn left {turn_angle} degrees at {speed}% power")
            t_list[0] = turn_angle
            t_list[1] = speed
            sendPacket(TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_TURN_LEFT, t_list)
        elif key == 'd':
            print(f"Turn right {turn_angle} degrees at {speed}% power")
            t_list[0] = turn_angle
            t_list[1] = speed
            sendPacket(TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_TURN_RIGHT, t_list)

        # Stop (z)
        elif key == 'z':
            print("Stop")
            sendPacket(TPacketType.PACKET_TYPE_COMMAND, TCommandType.COMMAND_STOP, ["0", "0", "0", "0"])

        # Exit on ESC
        elif ch == b'\x1b':  # ESC key
            print("Exiting live control mode.")
            exitFlag.set()
            break
        print("waiting to receive")
        packet = receivePacket()
        if packet is not None:
            packetType = packet.packetType
            res_type = packet.command
            if (
                    packetType == TPacketType.PACKET_TYPE_RESPONSE.value and
                    res_type == TResponseType.RESP_OK.value
            ):
                print("Received acknowledgement")
        else:
            print("No response from Arduino")


if __name__ == "__main__":
    # Example main routine for keypress-based control.
    # Adjust the serial port parameters as necessary.
    if startSerial("COM3", 9600, 8, 'N', 1, 3):
        waitForHelloRoutine()
        run_keypress_control()
        closeSerial()

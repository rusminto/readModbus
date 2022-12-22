import serial
import crcmod.predefined
import time

ser = serial.Serial(
    port='COM4',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.5
)

def send_data(hex_command = ""):

    header = "4E 54 00"

    thestring = hex_command.strip()
    crc_modbus = crcmod.predefined.mkCrcFun('modbus') #CRC-16
    crc_data = hex(crc_modbus(bytes.fromhex(thestring)))
    crc_data = "0x" + "0"*(6-len(str(crc_data))) + crc_data[2:]
    #print(crc_data)

    request= f"{hex_command} {crc_data[4:]} {crc_data[2:4]}"

    total_length = f"{len(request.split(' ')):x}"

    request = f"{header} {total_length} {request}".upper().strip()

    request_bytes = bytes.fromhex(request)
    print("TX -> ", request)
    ser.write(request_bytes)
    s = ser.read(100)
    s_formatted = s.hex(' ').upper()
    print("RX -> ",s_formatted)

def convert_to_modbus(is_read, index, sub_index, data):
    
    node_id = "00"
    modbus_slave_id = "05"
    modbus_function_block = "2B"
     
    protocol_control_read = "00 00"
    protocol_control_write = "01 00"

    mei_type = "0D"
    protocol_control = protocol_control_read if is_read else protocol_control_write

    starting_address = "00 00"

    number_of_data_values_raw = str(hex(int(len(data.replace(" ",""))/2))).replace("0x", "").zfill(4)
    number_of_data_values = number_of_data_values_raw[:2] + " " + number_of_data_values_raw[2:]

    command = f"{modbus_slave_id} {modbus_function_block} {mei_type} {protocol_control} {node_id} {index} {sub_index} {starting_address} {number_of_data_values} {data}"

    send_data(command)


# EXAMPLE
# convert_to_modbus(False, "20 09", "00", "7F")

# SET SPEED TO 50 RPM
convert_to_modbus(False, "60 FF", "00", "32 00 00 00")

# RUN
convert_to_modbus(False, "60 40", "00", "06 00")
convert_to_modbus(False, "60 40", "00", "0F 00")

time.sleep(3)

# SET SPEED TO 100 RPM
convert_to_modbus(False, "60 FF", "00", "64 00 00 00")

time.sleep(3)

# SET SPEED TO 300 RPM
convert_to_modbus(False, "60 FF", "00", "2C 01 00 00")

time.sleep(3)

# SET SPEED TO 100 RPM
convert_to_modbus(False, "60 FF", "00", "64 00 00 00")

time.sleep(3)

# SET SPEED TO 50 RPM
convert_to_modbus(False, "60 FF", "00", "32 00 00 00")


#STOP
convert_to_modbus(False, "60 40", "00", "00 00")

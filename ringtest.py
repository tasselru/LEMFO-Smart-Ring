# Test for retrieving accelerometer data from the LEMFO 2024 R02 Smart Ring.
# Hold the ring with its axis horizontally and rotate it until you see the scale start to move.
# WARNING: use at your own risk!

from bluepy.btle import Peripheral, UUID, DefaultDelegate, AssignedNumbers
import tkinter as tk
import time
import binascii
debugging=True

# Define the MAC address and UUIDs of the ring
device_mac_address = 'XX:XX:XX:XX:XX:XX'  # Replace with your device's MAC address
service_uuid = 0x18d0  # Service UUID
write_characteristic_uuid = 0x2d01  # Characteristic UUID for writing
read_characteristic_uuid = 0x2d00  # Characteristic UUID for reading

start_data_hex = 'ab0566031a'  # Data to write to start the stream
stop_data_hex = 'ab05660499'  # Data to write to stop the stream

# Delegate class to handle notifications
class NotificationDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleNotification(self, cHandle, data):
        hex_data = data.hex()

        if debugging:
            pairs = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)]
            formatted = ' '.join(pairs)
            print(formatted)

        # Only valid packets will be used to update the scale
        if (hex_data.startswith('5a0a67')) & (hex_data!='5a0a670000000000005b') & (hex_data!= '5a0a67fffa0000000016'):
            try:
                # Convert byte 7 and 8 to a signed int
                x = int.from_bytes(bytes([data[7], data[8]]), byteorder='little', signed=True)
                # Set the scale to this value
                scale.set(x / 100)
            except Exception as e:
                pass  # Do nothing if packet can't be converted.


# Connect to the BLE device
print(f'Connecting to {device_mac_address}...')
peripheral = Peripheral(device_mac_address)

# Discover services
print('Discovering services...')
service = peripheral.getServiceByUUID(service_uuid)

# Find characteristics for reading and writing
read_characteristic = service.getCharacteristics(read_characteristic_uuid)[0]
write_characteristic = service.getCharacteristics(write_characteristic_uuid)[0]

# Enable notifications on the reading characteristic
peripheral.setDelegate(NotificationDelegate())
peripheral.writeCharacteristic(read_characteristic.valHandle + 1, b"\x01\x00", withResponse=True)

# Start the accelerometer stream
print(f'Writing data {start_data_hex} to characteristic...')
write_characteristic.write(binascii.unhexlify(start_data_hex))

# Function to idle while waiting for notifications
def idle():
    peripheral.waitForNotifications(1.0)
    root.after(1, idle) # idle again and again

# Setup the GUI
root = tk.Tk()
root.title("Ring Test")
scale = tk.Scale(root, from_=-100, to=100, orient='horizontal', length=300)
scale.pack()
idle()
root.mainloop()

# Stop the accelerometer stream
print(f'Writing data {stop_data_hex} to characteristic...')
write_characteristic.write(binascii.unhexlify(stop_data_hex))

# Disconnect from the BLE device
peripheral.disconnect()
print('Disconnected.')

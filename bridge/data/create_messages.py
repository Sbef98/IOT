
def create_message_for_arduino(flags, device_id, datasize, data):
	data = bytearray(b'\xff')
	data.append(flags)
	data.append(device_id)
	data.append(datasize)
	if(datasize > 0):
		data.append(data)
	data.append(254) # equals b'\xfe' as stop sign
	print(data, len(data))

	return data

def create_device_initialization_message(flags, device_id):
	return create_message_for_arduino(flags=flags, device_id=device_id, datasize=0, data={})

def create_actuator_new_value_message(device_id, data):
	return create_message_for_arduino(flags=32, device_id=device_id, datasize=len(data), data=data)

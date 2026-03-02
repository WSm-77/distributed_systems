import socket

serverIP = "127.0.0.1"
serverPort = 9008
msg_bytes = (300).to_bytes(4, byteorder='little')

print('PYTHON UDP CLIENT')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(bytes(msg_bytes), (serverIP, serverPort))

response, address = client.recvfrom(1024)
int_response = int.from_bytes(response, byteorder='little')
print(int_response)

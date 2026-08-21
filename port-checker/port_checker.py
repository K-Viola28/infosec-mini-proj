import socket
print ("Simple Port Checker")
ip = input ("Enter target IP:")
port = int(input("Enter port number: "))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)

result = sock.connect_ex((ip, port))

if result == 0:
    print("Port is OPEN")
else:
    print("Port is CLOSED")

sock.close()

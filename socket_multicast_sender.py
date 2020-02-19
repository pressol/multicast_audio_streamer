#socket_multicast_sender.py
import socket
import struct
import sys
import zlib
import pyaudio

message = b'very important data'
multicast_group = ('224.3.29.71', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
sock.settimeout(0.2)

# Set the time-to-live for messages to 1 so they do not
# go past the local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:

    # Send data to the multicast group
    print('sending {!r}'.format(message))
    sent = sock.sendto(message, multicast_group)

    # Look for responses from all recipients
    responce = 0
    while True:
        if responce == 0:
            print('waiting to receive')
            try:
                data, server = sock.recvfrom(16)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print('received {!r} from {}'.format(
                    data, server))
                responce = 1
        else:

            CHUNK = 256
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            BLOCK_SIZE = 16

            p = pyaudio.PyAudio()

            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            print("* streaming")
            frames = []

            while True:
                data = stream.read(CHUNK)
                sent = sock.sendto(zlib.compress(data, 9), multicast_group)


finally:
    print('closing socket')
    sock.close()

import socket
import time

# i had to make an account just to see the like, 3 salient lines of this starter code.
# https://www.kodeco.com/5475-introduction-to-using-opencv-with-unity#toc-anchor-005

UDP_IP = "127.0.0.1"
UDP_PORT = 7999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def main():
    i = 0
    last = int(round(time.time() * 1000))
    while True:
        if int(round(time.time() * 1000)) - last > 1000:
            data = "ping" + str(i)
            sock.sendto(data.encode(), (UDP_IP, UDP_PORT))
            print(data)
            i += 1
            last = int(round(time.time() * 1000))



if __name__ == "__main__":
    main()
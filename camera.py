from machine import Pin, reset
from utime import sleep
from network import WLAN
import usocket as socket
import camera
import sys

SSID = "Hari"           # 🔹 Change to your WiFi SSID
PASSWORD = "123456789"  # 🔹 Change to your WiFi password

def start_camera():
    print("Initializing camera...")
    try:
        if camera.init(0):  # Try initializing
            print("✅ Camera initialized!")
        else:
            print("⚠️ Camera init returned False")
            reset()
    except Exception as e:
        print("❌ Camera init failed:", e)
        reset()

def connect_wifi():
    wifi = WLAN()
    wifi.active(True)
    try:
        wifi.connect(SSID, PASSWORD)
    except OSError:
        print("WiFi connect error! Restarting...")
        reset()
    print("Connecting to WiFi...")
    while not wifi.isconnected():
        print("...")
        sleep(1)
    print("✅ Connected! IP:", wifi.ifconfig()[0])
    return wifi.ifconfig()[0]

def start_server(ip):
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(1)
    print("🌐 Stream ready at: http://{}".format(ip))
    return server_socket

def stream(server_socket, wifi):
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print("📡 Client connected from:", addr)
            client_socket.write(b"HTTP/1.1 200 OK\r\n")
            client_socket.write(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n")
            client_socket.write(b"Connection: keep-alive\r\n\r\n")

            while True:
                frame = camera.capture()
                if not frame or not isinstance(frame, bytes):
                    print("⚠️ Frame capture failed, skipping...")
                    continue

                client_socket.write(b"--frame\r\n")
                client_socket.write(b"Content-Type: image/jpeg\r\n\r\n")
                client_socket.write(frame)
                client_socket.write(b"\r\n")
                sleep(0.05)
    except Exception as e:
        print("❌ Stream error:", e)
        sys.exit()
    except KeyboardInterrupt:
        print("🛑 Stopping server...")
        server_socket.close()
        wifi.disconnect()
        sys.exit()

# ================== MAIN ==================
start_camera()
ip = connect_wifi()
server_socket = start_server(ip)
stream(server_socket, WLAN())


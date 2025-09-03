from machine import Pin
from time import sleep

l1=Pin(4,Pin.OUT)

while True:
    l1.off()
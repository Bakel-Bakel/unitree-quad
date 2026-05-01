from unitree_sdk2py.core.channel import ChannelFactoryInitialize  # <-- change this import
from unitree_sdk2py.go2.sport.sport_client import SportClient
import time

ChannelFactoryInitialize(0, "wlan0")  # <-- and change this line

client = SportClient()
client.SetTimeout(10.0)
client.Init()

client.StandUp()
time.sleep(2)

client.Move(0.3, 0, 0)
time.sleep(1)
client.StopMove()
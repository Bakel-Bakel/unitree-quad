import time
from unitree_sdk2py.core.channel import ChannelFactory
from unitree_sdk2py.go2.sport.sport_client import SportClient

ChannelFactory.Instance().Init(0, "wlan0")

client = SportClient()
client.SetTimeout(10.0)
client.Init()

client.StandUp()
time.sleep(2)  # wait for it to fully stand before moving

client.Move(0.3, 0, 0)  # move forward slowly at 0.3 m/s
time.sleep(1)           # move for 1 second (~0.3 metres)
client.StopMove()       # stop
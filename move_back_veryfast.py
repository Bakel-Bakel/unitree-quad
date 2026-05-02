import asyncio
import logging
import json
import sys
from unitree_webrtc_connect.webrtc_driver import UnitreeWebRTCConnection, WebRTCConnectionMethod
from unitree_webrtc_connect.constants import RTC_TOPIC, SPORT_CMD

logging.basicConfig(level=logging.FATAL)

async def main():
    conn = UnitreeWebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip="192.168.1.66")
    await conn.connect()
    print("Connected!")

    # Check and switch to normal mode
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["MOTION_SWITCHER"],
        {"api_id": 1001}
    )
    data = json.loads(response['data']['data'])
    current_mode = data['name']
    print(f"Current mode: {current_mode}")

    if current_mode != "normal":
        print("Switching to normal mode...")
        await conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"],
            {"api_id": 1002, "parameter": {"name": "normal"}}
        )
        await asyncio.sleep(5)  # Wait for it to stand up

    # Move forward slowly
    print("Moving forward...")
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"],
        {"api_id": SPORT_CMD["Move"], "parameter": {"x": 1, "y": 0, "z": 0}}
    )

    await asyncio.sleep(3)  # Move for 1 second (~0.3m)

    # Stop
    print("Stopping...")
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"],
        {"api_id": SPORT_CMD["Move"], "parameter": {"x": 0, "y": 0, "z": 0}}
    )
    print("Done!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
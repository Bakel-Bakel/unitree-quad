import asyncio
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import RTC_TOPIC

async def main():
    conn = Go2WebRTCConnection(
        WebRTCConnectionMethod.LocalSTA,  # STA mode = both on same router
        ip="192.168.1.70"                 # Go2's IP
    )
    await conn.connect()

    # Move forward
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"],
        {"api_id": 1008, "parameter": {"x": 0.3, "y": 0, "z": 0}}
    )
    await asyncio.sleep(1)

    # Stop
    await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["SPORT_MOD"],
        {"api_id": 1008, "parameter": {"x": 0, "y": 0, "z": 0}}
    )

asyncio.run(main())
import asyncio
from unitree_webrtc_connect import UnitreeWebRTCConnection, WebRTCConnectionMethod

async def main():
    # Both laptop and Go2 are on the same router (192.168.1.x)
    conn = UnitreeWebRTCConnection(
        WebRTCConnectionMethod.LocalSTA,
        ip="192.168.1.70"  # your Go2's IP
    )
    await conn.connect()
    print("Connected!")

    # Stand up
    await conn.datachannel.pub_sub.publish_request_new(
        "rt/api/sport/request",
        {"header": {"identity": {"id": 1, "api_id": 1004}}, "parameter": "{}"}
    )
    await asyncio.sleep(2)

    # Move forward slowly
    await conn.datachannel.pub_sub.publish_request_new(
        "rt/api/sport/request",
        {"header": {"identity": {"id": 2, "api_id": 1008}},
         "parameter": '{"x": 0.3, "y": 0, "z": 0}'}
    )
    await asyncio.sleep(1)

    # Stop
    await conn.datachannel.pub_sub.publish_request_new(
        "rt/api/sport/request",
        {"header": {"identity": {"id": 3, "api_id": 1008}},
         "parameter": '{"x": 0, "y": 0, "z": 0}'}
    )
    print("Done!")

asyncio.run(main())
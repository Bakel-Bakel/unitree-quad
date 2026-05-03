# Unitree Go2 WebRTC Examples — Project Documentation

## 1. Overview

This project is a collection of standalone Python scripts that demonstrate how
to control a Unitree Go2 quadruped robot over WebRTC on a local network. The
scripts are intentionally small and single-purpose so newcomers can read one
file and understand exactly what is happening.

## 2. Goals

- Provide a minimal, working reference for connecting to a Go2 over `LocalSTA`.
- Show both the high-level Sport API (motion switcher + `SPORT_CMD`) and the
  raw `rt/api/sport/request` topic for users who need lower-level control.
- Show how to pull a live video stream from the dog via `aiortc` + OpenCV.

## 3. Architecture
+------------------+       WebRTC (LocalSTA)        +-------------------+
|  Your laptop     |  <-------------------------->  |  Unitree Go2      |
|  Python script   |   RTC_TOPIC / SPORT_CMD JSON   |  192.168.1.66     |
+------------------+                                +-------------------+

All scripts share the same connection method (`WebRTCConnectionMethod.LocalSTA`)
and target the dog by IP. The motion scripts go through the **motion switcher**
to make sure the robot is in `normal` mode before sending movement commands.
The raw script bypasses that layer and posts directly to `rt/api/sport/request`.

## 4. Scripts

| File | Purpose | Key API |
|---|---|---|
| `move_forward_0.3.py` | Moderate forward jog | `SPORT_CMD["Move"]`, x=0.3 |
| `move_back_0.3.py` | Moderate backward jog | `SPORT_CMD["Move"]`, x=-0.3 |
| `move_forward_veryfast.py` | Fast forward experiment | `SPORT_CMD["Move"]`, x=1 |
| `move_back_veryfast.py` | Intended fast reverse — currently x=1 (bug) | `SPORT_CMD["Move"]` |
| `raw_data_requests.py` | Stand + move using raw topic strings | `rt/api/sport/request` (1004, 1008) |
| `camera_preview.py` | Live camera in an OpenCV window | `aiortc` track callback |

## 5. Connection Lifecycle

Every script that talks to the dog walks through the same WebRTC handshake:

1. `WebRTC connection: started`
2. `ICE Gathering State: gathering -> complete`
3. `Signaling State: have-local-offer -> stable`
4. `Peer Connection State: connecting -> connected`
5. `Data Channel Verification: OK`

If the official Unitree mobile app or another WebRTC client is already
connected to the dog, the connection will fail with `RobotBusyError`.
Disconnect the other client and retry.

## 6. Known Issues

- `move_back_veryfast.py` uses `x: 1` (positive). It should be negative for a
  true fast reverse. The `print` text also still says "Moving forward".
- Hard-coded IP `192.168.1.66` in every script — no CLI flag yet.
- `raw_data_requests.py` has no `KeyboardInterrupt` handler in its main path.
- Comments in the motion scripts mention "1 second" while the actual sleep is 3.

## 7. Roadmap

- [ ] Add a shared `config.py` for IP and default speeds.
- [ ] Add a `joystick_control.py` script.
- [ ] Record video stream to disk in `camera_preview.py`.
- [ ] Add unit tests for the JSON payload shapes sent on `rt/api/sport/request`.
- [ ] Add a `LICENSE` file.

## 8. Safety

These scripts send real motion commands to a 15 kg robot. Always run them in
an open space, away from people, with the e-stop accessible. Validate `x` /
`y` / `z` velocities and sleep durations against your firmware before each
experiment.

## 9. Contributing

Fork, branch, PR. The coding style across the repo is intentionally simple:
small single-purpose scripts, logging at `FATAL`, a `KeyboardInterrupt`
handler in `__main__`, and the dog's IP at the top of the file.

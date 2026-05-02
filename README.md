# Gianni — Unitree Go2 WebRTC examples

This repository holds small standalone Python demos for talking to a **Unitree Go2** robot over **WebRTC**, using the same network path the official apps use when the dog is reachable on your LAN (typically **STA / Wi‑Fi client** mode, not pairing over the robot’s hotspot alone).

There is **no package layout** here: three scripts live at the repo root. They all assume your computer and the Go2 are on the **same LAN** (for example both on `192.168.1.x`) and that you know the robot’s IP address.

---

## What each file does

### `walk_with_motion_switch.py` — Motion mode check + timed forward jog

Purpose: connect, ensure the robot is in a sane motion state, walk forward briefly, then stop.

Flow:

1. **Connect** with `UnitreeWebRTCConnection` using `WebRTCConnectionMethod.LocalSTA` and the configured IP (`192.168.1.70` in the script).
2. **Motion switcher (high-level)**  
   - Publishes a request on `RTC_TOPIC["MOTION_SWITCHER"]` with `api_id` **1001** to read the current mode name.  
   - If the mode is not `"normal"`, sends **1002** with `parameter.name: "normal"` and sleeps **5 seconds** (to give the robot time to stand / settle).
3. **Move** via `RTC_TOPIC["SPORT_MOD"]` using `SPORT_CMD["Move"]`, with velocity **`x: 0.3`**, **`y: 0`**, **`z: 0`** (forward at a modest pace in the robot’s sport API convention).
4. After **1 second**, sends another **Move** with all zeros to **stop**.

Characteristics:

- Uses the library’s **named topics and command constants** (`RTC_TOPIC`, `SPORT_CMD`) instead of hand-built topic strings — easier to maintain and aligned with [`unitree_webrtc_connect`](https://github.com/unitreerobotics/unitree_webrtc_connect)-style bindings.
- Sets logging to `FATAL` to cut noise during runs.
- Handles **Ctrl+C** and exits cleanly.

### `sport_stand_walk_raw_requests.py` — Minimal sport API over raw topics

Purpose: shortest path “stand up, move forward, stop” without the motion-switcher prelude.

Flow:

1. Same **Local STA** connection pattern and IP as above.
2. Sends requests to the string topic **`rt/api/sport/request`** with a **`header.identity`** block (`id` + **`api_id`**) and a JSON **`parameter`** string.

Rough mapping in this script:

- **1004** — stand up (`parameter "{}"`).
- **1008** — move with `parameter '{"x": 0.3, "y": 0, "z": 0}'` then zeros to stop.

Characteristics:

- **Lower-level framing**: you assemble `header` / `parameter` manually. Useful to see the wire shape or to prototype calls that aren’t wrapped by constants yet.
- No mode check; assumes the robot can accept sport commands immediately.
- No structured stop on keyboard interrupt in the snippet (unlike `walk_with_motion_switch.py`).

### `camera_preview_webrtc.py` — Live camera preview (OpenCV window)

Purpose: subscribe to the Go2 **video channel** over the same WebRTC session and display frames in a window titled **Go2 Camera**.

Architecture:

1. Creates a **`unitree_webrtc_connect`** connection (`LocalSTA` + IP).
2. Runs **async setup** on a **background thread** with its own event loop:
   - `await conn.connect()`
   - `conn.video.switchVideoChannel(True)`
   - `conn.video.add_track_callback(recv_camera_stream)` — each decoded frame is pushed to a **`Queue`** shared with the main thread.
3. **Main thread** polls the queue with a short sleep when empty and uses **`cv2.imshow`**; press **`q`** to quit.
4. On exit: destroys OpenCV windows, stops the asyncio loop, joins the worker thread.

Dependencies beyond the WebRTC library: **`opencv-python`**, **`numpy`**, **`aiortc`** (`MediaStreamTrack` type hint / track API).

Characteristics:

- Mixes asyncio and GUI in a pragmatic way (thread + queue) so OpenCV doesn’t block the WebRTC loop.
- Default placeholder window uses **720×1280** until the first real frame arrives; actual frame size follows the incoming stream.

---

## Prerequisites

- **Python** 3.9+ recommended (stdlib `asyncio` usage is straightforward; match whatever your installed `unitree_webrtc_connect` supports).
- **Unitree Go2** reachable on the LAN in a mode compatible with **`WebRTCConnectionMethod.LocalSTA`** — typically the robot joins your Wi‑Fi and gets an IP like `192.168.1.x`.
- **`unitree_webrtc_connect`** installed and working with your firmware (see upstream repo / SDK docs).

---

## Configuration

Every script hard-codes:

```python
ip="192.168.1.70"
```

Change this to **your robot’s actual IP** (router DHCP list, Unitree app, or `ping`/`arp`). If your LAN uses another subnet (`10.0.0.x`, etc.), only the robot’s IP matters as long as routing is flat on that LAN.

**Velocity** (`x`, `y`, `z`) in `walk_with_motion_switch.py` / `sport_stand_walk_raw_requests.py` controls speed and direction in the sport API’s convention; **`0.3`** is a cautious forward example — tune for floor type and clearance.

---

## Installation

Clone the repo, create a virtual environment, install dependencies:

```bash
cd Gianni
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If `requirements.txt` is missing in your checkout, install at minimum:

```text
unitree_webrtc_connect
opencv-python
numpy
aiortc
```

Exact package names may follow the upstream naming on PyPI or GitHub; align with Unitree’s current instructions.

---

## Running the scripts

From the activated environment:

```bash
python walk_with_motion_switch.py     # Mode check → forward ~1 s → stop
python sport_stand_walk_raw_requests.py   # Stand → forward → stop (raw sport topic)
python camera_preview_webrtc.py           # Live camera window (press q to quit)
```

- Stop **`walk_with_motion_switch.py`** with **Ctrl+C** if needed.
- Stop **`camera_preview_webrtc.py`** by focusing the window and pressing **`q`**.

---

## Which script should I use?

| Goal | Script |
|------|--------|
| Reliable walk demo with motion-mode guard | **`walk_with_motion_switch.py`** |
| Inspect raw `/ rt/api/sport/request` payloads | **`sport_stand_walk_raw_requests.py`** |
| Verify video / latency / FoV | **`camera_preview_webrtc.py`** |

`walk_with_motion_switch.py` and `sport_stand_walk_raw_requests.py` illustrate **two layers** of the same stack: curated constants versus explicit topic + `api_id` JSON. Prefer **`walk_with_motion_switch.py`** for day-to-day control experiments unless you’re debugging payloads.

---

## Safety and responsibility

These scripts issue **real motion commands** to a legged robot. Run only with:

- Adequate **clear floor space**, traction, and no people or fragile objects in the workspace.
- The robot **on the ground** and in a configuration where stand/walk commands are appropriate.
- **Emergency stop / manual override** understood (hardware E-stop or app safety features per Unitree docs).

Authors of this demo code are responsible for validating behavior against their firmware; **do not** assume velocities or API IDs remain identical across firmware versions without checking Unitree documentation.

---

## Repository layout

```
Gianni/
├── README.md       # This file
├── requirements.txt # Python dependencies (if present)
├── walk_with_motion_switch.py       # Motion switcher + sport move (library topics)
├── sport_stand_walk_raw_requests.py # Sport API via raw topic strings
└── camera_preview_webrtc.py          # WebRTC video → OpenCV preview
```

---

## License

No license file is included in this repository. If you publish or redistribute, add a `LICENSE` that matches your intent and any obligations from `unitree_webrtc_connect` or Unitree’s SDK terms.

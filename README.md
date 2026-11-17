# unienv-zed

ZED camera node adaptor for UniEnv.

## Installation

Install the ZED SDK first so `pyzed.sl` is available, then install this package locally:

```bash
pip install -e .
```

## Usage

```python
from unienv_interface.backends.numpy import NumpyComputeBackend
from unienv_interface.world import RealWorld

from unienv_zed import ZedCameraNode, ZedResolution, ZedFlipMode

world = RealWorld(
    NumpyComputeBackend,
    world_timestep=1.0 / 30.0,
)

camera = ZedCameraNode(
    world=world,
    serial_number=None,            # or a specific device serial
    resolution=ZedResolution.HD720,
    fps=30,
    enable_left_rgb=True,
    enable_left_depth=True,
    enable_right_rgb=False,
    enable_right_depth=False,
    flip_mode=ZedFlipMode.OFF,
)

world.reset()
camera.after_reset()

while True:
    dt = world.step()
    camera.post_environment_step(dt)
    obs = camera.get_observation()
    rgb = obs["left_rgb"]
    depth = obs["left_depth"]
```

## Features

- Native `pyzed.sl` live-camera integration
- Configurable RGB/depth outputs for left and right sensors
- Resolution / FPS / depth mode / flip mode options
- Rectified intrinsics included in observations
- Real-world `WorldNode` lifecycle compatible with UniEnv

## Observations and space metadata

| Key | Shape | Dtype | Space metadata |
| --- | --- | --- | --- |
| `left_rgb` / `right_rgb` | `(H, W, 3)` | `uint8` | `kind="image"`, `format="rgb"` (converted from the SDK's BGRA), `layout="HWC"` |
| `left_depth` / `right_depth` | `(H, W)` | `float32` | `kind="depth"`, `layout="HW"`, `units` from `unit` (`METER` → `"m"`, `CENTIMETER` → `"cm"`, `MILLIMETER` → `"mm"`, `INCH` → `"in"`, `FOOT` → `"ft"`), `invalid_depth_value` (the value NaN / inf pixels are replaced with) |
| `left_intrinsics` / `right_intrinsics` | `(3, 3)` | `float32` | `kind="intrinsics"`, `frame="camera_cv"` (OpenCV `K`) |

Every leaf also records `source` (the serial number as a string),
`serial_number`, `camera_model` and `side` (`"left"` / `"right"`); images and
depth maps carry the camera's actual `fps`. Requires `unienv>=0.0.1b16`.
`build_zed_observation_space(height=..., width=..., ...)` builds the same space
without a camera.

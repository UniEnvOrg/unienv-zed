"""Camera-free tests of the ZED observation space and its metadata."""

import pytest

from unienv_interface.space.space_utils.metadata_utils import spaces_equal_with_metadata, validate_metadata

from unienv_zed import ZedCameraNode, ZedUnit, build_zed_observation_space


def _build(**overrides):
    kwargs = dict(
        height=720, width=1280, fps=30, serial_number=31726771, camera_model="ZED 2i",
        unit="METER", invalid_depth_value=0.0,
        enable_left_rgb=True, enable_right_rgb=True,
        enable_left_depth=True, enable_right_depth=True,
        include_intrinsics=True,
    )
    kwargs.update(overrides)
    return build_zed_observation_space(**kwargs)


def test_all_outputs_are_described():
    space = _build()
    validate_metadata(space)
    assert set(space.spaces) == {
        "left_rgb", "right_rgb", "left_depth", "right_depth", "left_intrinsics", "right_intrinsics",
    }
    for side in ("left", "right"):
        rgb = space[f"{side}_rgb"].metadata
        assert rgb["kind"] == "image"
        assert rgb["format"] == "rgb"
        assert rgb["layout"] == "HWC"
        assert rgb["fps"] == 30
        assert rgb["source"] == "31726771"
        assert rgb["serial_number"] == 31726771
        assert rgb["camera_model"] == "ZED 2i"
        assert rgb["side"] == side

        depth = space[f"{side}_depth"].metadata
        assert depth["kind"] == "depth"
        assert depth["units"] == "m"
        assert depth["layout"] == "HW"
        assert depth["invalid_depth_value"] == 0.0
        assert depth["side"] == side

        intrinsics = space[f"{side}_intrinsics"].metadata
        assert intrinsics["kind"] == "intrinsics"
        assert intrinsics["frame"] == "camera_cv"
        assert intrinsics["side"] == side


@pytest.mark.parametrize(
    "unit, units",
    [("METER", "m"), ("CENTIMETER", "cm"), (ZedUnit.MILLIMETER, "mm"), ("INCH", "in"), ("FOOT", "ft")],
)
def test_depth_units_follow_the_configured_unit(unit, units):
    space = _build(unit=unit, invalid_depth_value=-1.0)
    assert space["left_depth"].metadata["units"] == units
    assert space["left_depth"].metadata["invalid_depth_value"] == -1.0


def test_left_only_defaults():
    space = build_zed_observation_space(height=376, width=672)
    validate_metadata(space)
    assert set(space.spaces) == {"left_rgb", "left_intrinsics"}
    md = space["left_rgb"].metadata
    for key in ("source", "serial_number", "camera_model", "fps"):
        assert key not in md


def test_node_builds_its_space_with_the_helper():
    # A node as left by _refresh_camera_metadata, without opening a camera.
    node = ZedCameraNode.__new__(ZedCameraNode)
    node.actual_height, node.actual_width, node.actual_fps = 720, 1280, 15
    node.serial_number, node.camera_model = 123, "ZED X"
    node.unit, node.invalid_depth_value = ZedUnit.MILLIMETER, 0.0
    node.enable_left_rgb, node.enable_right_rgb = True, False
    node.enable_left_depth, node.enable_right_depth = True, False
    node.include_intrinsics = True
    node.zed = None
    space = node._build_observation_space()
    expected = build_zed_observation_space(
        height=720, width=1280, fps=15, serial_number=123, camera_model="ZED X",
        unit="MILLIMETER", enable_left_depth=True,
    )
    assert spaces_equal_with_metadata(space, expected)
    assert space["left_depth"].metadata["units"] == "mm"

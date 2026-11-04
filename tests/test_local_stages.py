"""k1m local stages: package import, gate and render run against the real K1 model.

Needs the k1-description assets (submodule or K1_ASSETS_DIR) and mujoco.
"""
import os
import shutil

import pytest

mujoco = pytest.importorskip("mujoco")
k1_description = pytest.importorskip("k1_description")

import k1m  # noqa: E402
from k1m import local_stages  # noqa: E402


@pytest.fixture
def fight_clip(tmp_path):
    try:
        src = k1_description.assets_dir() / "motions" / "K1" / "k1_fight_001_30fps.csv"
    except FileNotFoundError:
        pytest.skip("K1 assets not available")
    m, _ = k1m.schema.read_csv(str(src))
    dst = tmp_path / "fight.csv"
    k1m.schema.write_csv(str(dst), m[:60], fps=30)   # 2 s keeps render fast
    return dst, m


def test_schema_is_shared_contract():
    from k1_common import clip_schema
    assert k1m.schema is clip_schema
    assert clip_schema.N_COLS == 29


def test_model_joint_order_matches_contract():
    assert k1m.schema.verify_joint_order() == k1m.schema.K1_JOINT_NAMES


def test_gate_reports_joint_limit_violation(fight_clip, tmp_path):
    clip, _ = fight_clip
    rep = local_stages.gate(str(clip), fps=30, report_json=str(tmp_path / "g.json"))
    checks = {c["name"]: c for c in rep["reports"][0]["checks"]}
    assert "joint_limits" in checks
    assert os.path.exists(rep["_report_path"])


def test_gate_full_clip_flags_shoulder_limit(tmp_path):
    src = k1_description.assets_dir() / "motions" / "K1" / "k1_fight_001_30fps.csv"
    dst = tmp_path / "full.csv"
    shutil.copy(src, dst)
    rep = local_stages.gate(str(dst), fps=30)
    lim = next(c for c in rep["reports"][0]["checks"] if c["name"] == "joint_limits")
    assert not lim["passed"] and lim["worst_joint"] == "ALeft_Shoulder_Pitch"


def test_render_writes_video(fight_clip, tmp_path):
    clip, _ = fight_clip
    out = local_stages.render(str(clip), str(tmp_path / "r.mp4"), fps=30, width=320)
    assert os.path.getsize(out) > 10_000


def test_child_env_keeps_non_ros_pythonpath(monkeypatch):
    monkeypatch.setenv("AMENT_PREFIX_PATH", "/ws/install/pkg")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(
        ["/src/k1m", "/opt/ros/jazzy/lib/python3.12/site-packages", "/ws/install/pkg/lib"]))
    e = local_stages._env()
    assert e["PYTHONPATH"] == "/src/k1m"
    assert "AMENT_PREFIX_PATH" not in e

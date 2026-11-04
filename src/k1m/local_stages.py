"""Stages that run on the local machine: the feasibility gate and the render.

Both run :mod:`k1m.gate` / :mod:`k1m.render` in a subprocess rather than
in-process. `motion_feasibility_gate.py` is the pre-flight authority on whether a
motion is safe to send to hardware, and `record_k1_motion.py` is a validated
dynamic PD replay -- both have accumulated fixes (geom groups, quaternion
order, the K1 sole-frame offset) that would be easy to lose by forking them
into a library. Subprocess also keeps their single source of truth intact.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys



def _py() -> str:
    """Interpreter with mujoco + numpy. Honours K1M_PYTHON."""
    exe = os.environ.get("K1M_PYTHON") or sys.executable
    try:
        import mujoco  # noqa: F401
    except ImportError:
        alt = os.path.expanduser("~/.venvs/gmr/bin/python")
        if os.path.exists(alt):
            return alt
    return exe


def _env() -> dict:
    """A clean env.

    The ROS 2 workspace exports PYTHONPATH and LD_LIBRARY_PATH that shadow
    libtorch and break `import torch` in any venv, so ROS entries are stripped
    for every child process. Non-ROS PYTHONPATH entries (e.g. a source
    checkout of k1m) are kept so the child can import this package.
    """
    e = dict(os.environ)
    ros = tuple(p for k in ("AMENT_PREFIX_PATH", "COLCON_PREFIX_PATH")
                for p in e.get(k, "").split(os.pathsep) if p) + ("/opt/ros/",)
    keep = [p for p in e.get("PYTHONPATH", "").split(os.pathsep)
            if p and not p.startswith(ros)]
    for k in ("PYTHONPATH", "LD_LIBRARY_PATH", "AMENT_PREFIX_PATH",
              "COLCON_PREFIX_PATH", "CMAKE_PREFIX_PATH", "ROS_DISTRO"):
        e.pop(k, None)
    if keep:
        e["PYTHONPATH"] = os.pathsep.join(keep)
    return e


def gate(motion_csv: str, fps: float = 30.0,
         urdf: str | None = None,
         report_json: str | None = None) -> dict:
    """Run the feasibility gate. Returns the parsed report.

    The gate is the authority on hardware-readiness. A motion that fails it is
    not "probably fine" -- it is a kinematic solve with no foot locking, no
    dynamics and no actuator model behind it, which is exactly what breaks a
    real robot.
    """
    report_json = report_json or (os.path.splitext(motion_csv)[0] + "_gate.json")
    cmd = [sys.executable, "-m", "k1m.gate", motion_csv, "--fps", str(fps),
           "--json", report_json]
    if urdf:
        cmd += ["--urdf", urdf]
    p = subprocess.run(cmd, capture_output=True, text=True, env=_env())
    out = (p.stdout or "") + (p.stderr or "")
    if not os.path.exists(report_json):
        raise RuntimeError(f"gate produced no report (exit {p.returncode})\n"
                           + "\n".join(out.strip().splitlines()[-20:]))
    with open(report_json) as f:
        rep = json.load(f)
    rep["_stdout"] = out
    rep["_report_path"] = report_json
    return rep


def render(motion_csv: str, out_mp4: str, fps: float = 30.0,
           title: str = "", sim_fps: int = 200, width: int = 1280,
           gl: str = "egl") -> str:
    """Render the 3-panel MuJoCo replay to `out_mp4`. Returns the path."""
    cmd = [sys.executable, "-m", "k1m.render", motion_csv, "--out", out_mp4,
           "--fps", str(fps), "--sim-fps", str(sim_fps),
           "--width", str(width), "--gl", gl]
    if title:
        cmd += ["--title", title]
    p = subprocess.run(cmd, capture_output=True, text=True, env=_env())
    if p.returncode != 0 or not os.path.exists(out_mp4):
        raise RuntimeError(f"render failed (exit {p.returncode})\n"
                           + "\n".join(((p.stdout or "") + (p.stderr or ""))
                                       .strip().splitlines()[-20:]))
    return out_mp4


def summarize_gate(rep: dict) -> str:
    """One-line human summary of a gate report.

    The report schema is::

        {"reports": [{"path", "fps", "n_frames", "duration_s",
                      "checks": [{"name", "passed", "detail", "worst"}, ...]}]}
    """
    reports = rep.get("reports") or []
    if not reports:
        return "no reports in gate output"
    out = []
    for r in reports:
        checks = r.get("checks", [])
        fails = [c for c in checks if not c.get("passed", False)]
        verdict = "FAIL" if fails else "PASS"
        out.append(f"{verdict}: {r.get('path', '?')} -- "
                   f"{len(checks) - len(fails)}/{len(checks)} checks pass, "
                   f"{len(fails)} blocking")
        for c in fails:
            out.append(f"  - {c.get('name', '?')}: {c.get('detail', '')}")
    return "\n".join(out)

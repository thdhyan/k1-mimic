"""k1m -- Booster K1 motion retargeting: video or text in, joint angles out.

Stages live in :mod:`k1m.remote_stages` (GPU, on a DGX Spark) and
:mod:`k1m.local_stages` (the feasibility gate and the MuJoCo replay, local).
The CSV contract that every stage agrees on is :mod:`k1_common.clip_schema`
(re-exported as ``k1m.schema``).
"""
from __future__ import annotations

__version__ = "0.1.0"

from k1_common import clip_schema as schema  # noqa: F401  (re-exported)

from . import local_stages, pipeline, remote, remote_stages  # noqa: F401

__all__ = ["schema", "remote", "remote_stages", "local_stages", "pipeline",
           "__version__"]

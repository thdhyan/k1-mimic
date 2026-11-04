# src/k1m

Part of [k1-mimic](https://github.com/thdhyan/k1-mimic).

| File | What it does |
|---|---|
| `__init__.py` | k1m -- Booster K1 motion retargeting: video or text in, joint angles out. |
| `app.py` | Gradio front end for k1m. |
| `cli.py` | k1m -- turn a video or a text prompt into Booster K1 joint angles. |
| `gvhmr_amass_export.py` | GVHMR output -> AMASS-style SMPL-X npz, which is what GMR consumes. |
| `gvhrm_to_amass.py` | GVHMR output -> AMASS-style SMPL-X npz, which is what GMR consumes. |
| `local_stages.py` | Stages that run on the local machine: the feasibility gate and the render. |
| `pipeline.py` | End-to-end pipelines: video or text in, joint angles + replay video out. |
| `pkl_to_csv.py` | Convert a GMR retarget .pkl / .npz to the Booster K1 motion CSV contract. |
| `remote.py` | Run pipeline stages on a remote GPU host, or locally. |
| `remote_stages.py` | Stages that need a GPU, and so run on a remote DGX Spark. |
| `soma_retarget_node.py` | HMD-Poser body -> SOMA -> K1 arm joints, live (replaces the K1 arm IK when the teleop node runs with ``--arm-src soma``). Ported from G1_sim |

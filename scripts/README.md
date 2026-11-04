# scripts

Part of [k1-mimic](https://github.com/thdhyan/k1-mimic).

| File | What it does |
|---|---|
| `gmr_bvh_to_k1_csv.py` | GMR driver: BVH (SOMA / LAFAN1) -> Booster K1 motion CSV. |
| `gmr_pkl_to_k1_csv.py` | Convert a GMR retarget .pkl / .npz to the Booster K1 motion CSV contract. |
| `mk_soma_k1_target.py` | Generate a native booster_k1 SOMA Retargeter target from the bundled t1 one. |
| `restart_k1m_app.sh` | Restart the k1m Gradio app, and verify the NEW process owns the port. |
| `soma_csv_to_k1_csv.py` | SOMA Retargeter CSV -> Booster K1 motion CSV (the booster_train contract). |

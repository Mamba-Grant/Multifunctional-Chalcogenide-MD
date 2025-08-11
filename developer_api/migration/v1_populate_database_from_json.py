# {"MP-ID": "mp-19", "formula": "Te3", "spacegroup": "P3_121 (152)", "cell": {"array": [[4.589441374061009, -0.0, 0.0], [-2.294720687030504, 3.974572819116195, 0.0], [0.0, 0.0, 5.903595424768976]]}, "symbols": ["Te", "Te", "Te"], "positions": [[1.0900687767282833, 0.0, 1.9678651219110195], [-0.5450343883641413, 0.9440272525189205, 3.935730302857956], [1.7496862986663633, 3.030545566597275, 0.0]], "vdw gap": 1.9678651809469365, "bond length deviation": [], "bond angle deviation": [], "mass density": 3.5547172105641063, "total energy": -70.23506022, "total energy_soc": -69.8543599, "cohesive energy": 2.0055375700000013, "exfoliation energy": [], "born effective charge tensor": 0.9838399999999999, "born effective charge q_xy": 0.49191999999999997, "born effective charge q_z": 0.0, "dielectric constant XY": 11.533748, "dielectric constant Z": 11.87081, "bader charge": [["Te", 6.0, 6.004041], ["Te", 6.0, 5.999842], ["Te", 6.0, 5.996117]], "density of states at fermi": 0.0, "effective mass": -0.17239564703118065, "vbm": 0, "cbm": 0, "band gap": 0, "vbm soc": 0, "cbm soc": 0, "band gap soc": 0, "layered?": false, "component layers": [], "KPath": ["0.5000 0.0000 0.0000 ! M", "0.0000 0.0000 0.0000 ! G", "0.0000 0.0000 0.0000 ! G", "0.0000 0.0000 0.5000 ! A", "0.0000 0.0000 0.5000 ! A", "0.3333 0.3333 0.5000 ! H", "0.3333 0.3333 0.5000 ! H", "0.3333 0.3333 0.0000 ! K", "0.3333 0.3333 0.0000 ! K", "0.5000 0.0000 0.5000 ! L", "0.5000 0.0000 0.5000 ! L", "0.5000 0.0000 0.0000 ! M"], "band locations": "/home/gtown/Documents/carbon/mpAll/allbulk/calcs/dir_Te3-mp-19/scf/band", "band soc location": "/home/gtown/Documents/carbon/mpAll/allbulk/calcs/dir_Te3-mp-19/scf_soc/band_soc", "dos location": "/home/gtown/Documents/carbon/mpAll/allbulk/calcs/dir_Te3-mp-19/scf/dos"}

from hashlib import md5
import os
import json
import psycopg
from math import isnan, isinf

def sanitize(obj):
    if isinstance(obj, float) and (isnan(obj) or isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(v) for v in obj]
    else:
        return obj

conn = psycopg.connect(
    dbname="fastapi_psycopg3",
    user="postgres",
    password="",
    host="localhost"
)

for root, dirs, files in os.walk("./backend/json/"):
    for file in files:
        print(file)

        # Only accept valid json files
        if not file.endswith(".json"):
            print(f"WARNING: skipping {file}")
            continue

        with open(os.path.join(root, file), 'r') as f:
            raw = json.load(f)
            data_blob = json.dumps(sanitize(raw), sort_keys=True, indent=2)
            data_hash = md5(data_blob.encode("utf-8")).hexdigest()

            with conn.transaction():
                with conn.cursor() as cur:

                    # 1. Try to insert a hash (avoid duplicates)
                    cur.execute("""
                        INSERT INTO material_keys (data_hash) VALUES (%s)
                        ON CONFLICT (data_hash) DO NOTHING
                        RETURNING id;
                    """, (data_hash,))

                    # 2. Grab the hash, whether it already exists or if it was just added
                    result = cur.fetchone()
                    if result:
                        id = result[0]
                    else:
                        # Get existing id if conflict
                        cur.execute("SELECT id FROM material_keys WHERE data_hash = %s;", (data_hash,))
                        result = cur.fetchone()
                        if result:
                            id = result[0]
                        else: 
                            print("ERROR: Could not return id from fetch.")
                    print(id)

                    # 3. Insert JSON blob if not exists
                    cur.execute("SELECT 1 FROM material_data WHERE id = %s;", (id,)) # Check if exists at the id
                    if cur.fetchone() is None:
                        cur.execute("INSERT INTO material_data (id, data) VALUES (%s, %s);", (id, data_blob))

                    print(f"INSERTED: {file}")


from hashlib import md5
import os
import json
from typing import Any, Dict, cast
import psycopg
from math import isnan, isinf
from numbers import Number

def is_str_number_mix(lst):
    """
    Recursively checks if a list (possibly nested) contains both string and numeric types.
    """
    has_str = has_num = False

    def check(item):
        nonlocal has_str, has_num
        if isinstance(item, list):
            for sub in item:
                check(sub)
        elif isinstance(item, str):
            has_str = True
        elif isinstance(item, Number):
            has_num = True

    check(lst)
    return has_str and has_num

from psycopg.abc import Query

valid_columns = [
    "MP-ID",
    "formula",
    "spacegroup",
    "cell",
    "symbols",
    "positions",
    "vdw gap",
    "bond length deviation",
    "bond angle deviation",
    "mass density",
    "total energy",
    "total energy_soc",
    "cohesive energy",
    "exfoliation energy",
    "born effective charge tensor",
    "born effective charge q_xy",
    "born effective charge q_z",
    "dielectric constant XY",
    "dielectric constant Z",
    "bader charge",
    "density of states at fermi",
    "effective mass",
    "vbm",
    "cbm",
    "band gap",
    "vbm soc",
    "cbm soc",
    "band gap soc",
    "layered?",
    "component layers",
    "KPath",
    "band locations",
    "band soc location",
    "dos location"
]

conn = psycopg.connect(
    dbname="fastapi_psycopg3",
    user="postgres",
    password="",
    host="localhost"
)

for root, dirs, files in os.walk("./backend/json/"):
    for file in files:
        # Only accept valid json files
        if not file.endswith(".json"):
            print(f"WARNING: skipping {file}")
            continue

        with open(os.path.join(root, file), 'r') as f:
            raw: Dict = json.load(f)
            data_blob: str = json.dumps(raw, sort_keys=True, indent=2)
            hash: str = md5(data_blob.encode("utf-8")).hexdigest() # For checking duplicates

            with conn.transaction():
                with conn.cursor() as cur:

                    # 1. Try to insert a hash (avoid duplicates)
                    cur.execute("""
                        INSERT INTO material_keys (hash) VALUES (%s)
                        ON CONFLICT (hash) DO NOTHING
                        RETURNING id;
                    """, (hash,))

                    result = cur.fetchone()
                    if result:
                        id: int = result[0]
                    else:
                        # Get existing id if conflict
                        cur.execute("SELECT id FROM material_keys WHERE hash = %s;", (hash,))
                        result = cur.fetchone()
                        if result:
                            id = result[0]
                        else: 
                            print("ERROR: Could not return id from fetch.")

                    # 2. Great: we have an ID of a match or new entry, time to populate the columns
                    for _, (key, value) in enumerate(raw.items()):

                        # Use a whitelist
                        if key not in valid_columns:
                            print(f"WARMING: skipped unknown key in --- {file} --- {key}")
                            continue

                        # Make sure certain types fit the schema (mostly convert missing/nan/inf to None)
                        blob: Any = value
                        if isinstance(value, str) and value.strip().upper() == "UNKNOWN":
                            blob = None
                        elif isinstance(value, list) and len(value) == 0:
                            blob = None
                        elif isinstance(value, float):
                            if isnan(value) or isinf(value):
                                blob = None
                        elif isinstance(value, list) and is_str_number_mix(value):
                            blob = json.dumps(value, sort_keys=True, indent=2)
                        elif isinstance(value, dict):
                            blob = json.dumps(value, sort_keys=True, indent=2)

                        # 3. Insert JSON blob if not exists
                        cur.execute("SELECT 1 FROM material_data WHERE id = %s;", (id,)) # Check if exists at the id
                        if cur.fetchone() is None:
                            query: Query = cast(Query, f'INSERT INTO material_data (id, "{key}") VALUES (%s, %s);')
                            cur.execute(query, (id, blob))
                        else:
                            query: Query = cast(Query, f'UPDATE material_data SET "{key}" = %s WHERE id = %s;')
                            cur.execute(query, (blob, id))


# changes from v4 -> v5: 
# 1) Push band structure and dos vectors to a secondary table in the database
# 2) Make hash of the primary table entries gettable
# 3) Declare whitelist with the associated type to have a decent experience inserting data

from hashlib import md5
import os
import json
import re
from typing import Any, Dict, Optional
import numpy as np
from ase import Atoms
from ase.build import make_supercell
from ase.neighborlist import NeighborList
from ase.data import covalent_radii

import psycopg

from math import isnan, isinf

DATA_COLUMN_TYPES = {
    "MP-ID": str,
    "formula": str,
    "chemical_symbols": list,
    "spacegroup": str,
    "cell": dict,
    "symbols": list,
    "connectivity": list,
    "positions": list,
    "vdw gap": float,
    "bond length deviation": dict,
    "bond angle deviation": dict,
    "mass density": float,
    "total energy": float,
    "total energy_soc": float,
    "cohesive energy": float,
    "exfoliation energy": float,
    "born effective charge tensor": float,
    "born effective charge q_xy": float,
    "born effective charge q_z": float,
    "dielectric constant XY": float,
    "dielectric constant Z": float,
    "bader charge": dict,
    "density of states at fermi": float,
    "effective mass": float,
    "vbm": list,
    "cbm": list,
    "band gap": float,
    "vbm soc": list,
    "cbm soc": list,
    "band gap soc": float,
    "layered?": bool,
    "component layers": list,
    "KPath": list,
    "band locations": str,
    "band soc location": str,
    "dos location": str
}

DOS_BANDS_COLUMN_TYPES = {
    "bands": list,
    "band distances": list,
    "KPoints": dict,
    "bands soc": list,
    "band distances soc": list,
    "density of states energies": list,
    "total density of states": list,
    "projected density of states": dict,
    "fermi energy": float
}

def cast_value(value: Any, target_type: type) -> Optional[Any]:
    """Cast value to target Python type, return None for invalid values."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip().upper() == "UNKNOWN":
        return None
    if isinstance(value, list) and len(value) == 0:
        return None
    if isinstance(value, float) and (isnan(value) or isinf(value)):
        return None

    try:
        if target_type == str:
            return str(value)
        elif target_type == bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'y')
            return bool(value)
        elif target_type == float:
            return float(value)
        elif target_type == int:
            return int(value)
        elif target_type == list:
            if isinstance(value, list):
                return value
            return [value]
        elif target_type == dict:
            if isinstance(value, (dict, list)):
                return json.dumps(value, sort_keys=True)
            return json.dumps({"value": value}, sort_keys=True)
        else:
            return value
    except (ValueError, TypeError, OverflowError):
        return None

def get_or_create_hash_id(cur, hash_str: str) -> int:
    cur.execute(
        """
        INSERT INTO hashtable (hash)
        VALUES (%s)
        ON CONFLICT (hash) DO NOTHING
        RETURNING id;
        """,
        (hash_str,),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("SELECT id FROM hashtable WHERE hash = %s;", (hash_str,))
    row = cur.fetchone()
    if row:
        return row[0]
    raise RuntimeError("Could not obtain hash id")

# Connection (adjust credentials as needed)
conn = psycopg.connect(
    dbname="fastapi_psycopg3", user="postgres", password="", host="localhost"
)

for root, dirs, files in os.walk("./backend/json/"):
    for idx, file in enumerate(files):
        if not file.endswith(".json"):
            print(f"WARNING: skipping {file}")
            continue

        with open(os.path.join(root, file), "r") as f:
            try:
                raw: Dict = json.load(f)
            except Exception as e:
                print(f"Failed to parse JSON {file}: {e}")
                continue

            data_blob: str = json.dumps(raw, sort_keys=True, indent=2)
            hash_str: str = md5(data_blob.encode("utf-8")).hexdigest()

            try:
                with conn.transaction():
                    with conn.cursor() as cur:
                        # 1. Insert/get hash ID
                        material_id = get_or_create_hash_id(cur, hash_str)

                        # 2. Upsert into data table (main)
                        try:
                            cols = ['id', 'hash']
                            vals = [material_id, hash_str]
                            updates = ['hash = EXCLUDED.hash']

                            for key, target_type in DATA_COLUMN_TYPES.items():
                                if key not in raw:
                                    continue
                                casted_value = cast_value(raw[key], target_type)
                                if casted_value is None:
                                    continue
                                cols.append(f'"{key}"')
                                vals.append(casted_value)
                                updates.append(f'"{key}" = EXCLUDED."{key}"')

                            col_list = ", ".join(cols)
                            placeholder_list = ", ".join(["%s"] * len(cols))
                            update_clause = ", ".join(updates)

                            cur.execute(
                                f"""
                                INSERT INTO data ({col_list})
                                VALUES ({placeholder_list})
                                ON CONFLICT (id) DO UPDATE SET {update_clause};
                                """,
                                vals
                            )
                        except Exception as e:
                            print(f"Error upserting main data for {file}: {e}")

                        # Special handling for chemical symbols from formula (overwrites if present)
                        try:
                            if "formula" in raw and raw["formula"]:
                                formula = raw["formula"].lower()
                                elements = re.findall(r"[a-z]+", formula)
                                if elements:
                                    cur.execute(
                                        """
                                        INSERT INTO data (id, "chemical_symbols")
                                        VALUES (%s, %s)
                                        ON CONFLICT (id) DO UPDATE SET "chemical_symbols" = EXCLUDED."chemical_symbols";
                                        """,
                                        (material_id, elements),
                                    )
                        except Exception as e:
                            print(f"Failed to split chemical composition for {file}: {e}")

                        # Build connectivity matrix if possible (will also upsert connectivity separately)
                        try:
                            if all(k in raw for k in ["symbols", "positions", "cell"]):
                                atoms = Atoms(
                                    symbols=raw["symbols"],
                                    positions=raw["positions"],
                                    cell=raw["cell"]["array"],
                                    pbc=True
                                )

                                P = np.diag([2, 2, 1])
                                supercell_atoms = make_supercell(atoms, P)

                                cutoffs = [
                                    covalent_radii[supercell_atoms.get_atomic_numbers()[i]] * 1.3
                                    for i in range(len(supercell_atoms))
                                ]
                                nl = NeighborList(cutoffs, self_interaction=False, bothways=True)
                                nl.update(supercell_atoms)

                                n_sites = len(supercell_atoms)
                                bond_matrix = np.zeros((n_sites, n_sites), dtype=int)

                                radii = covalent_radii
                                for i in range(n_sites):
                                    indices, offsets = nl.get_neighbors(i)
                                    for j, offset in zip(indices, offsets):
                                        if np.all(offset == 0) and j > i:
                                            distance = supercell_atoms.get_distance(i, j, mic=True)
                                            threshold = 1.25 * (
                                                radii[supercell_atoms.numbers[i]] +
                                                radii[supercell_atoms.numbers[j]]
                                            )
                                            if distance <= threshold:
                                                bond_matrix[i, j] = 1
                                                bond_matrix[j, i] = 1

                                # Upsert connectivity explicitly to ensure it's captured
                                cur.execute(
                                    """
                                    INSERT INTO data (id, "connectivity")
                                    VALUES (%s, %s)
                                    ON CONFLICT (id) DO UPDATE SET "connectivity" = EXCLUDED."connectivity";
                                    """,
                                    (material_id, bond_matrix.tolist()),
                                )
                        except Exception as e:
                            print(f"Failed to precompute connectivity for {file} --- {e} --- in {raw.get('formula', 'unknown')}")

                        # 3. Process DOS/bands data
                        try:
                            dos_bands_data = {}
                            for key, value in raw.items():
                                if key in DOS_BANDS_COLUMN_TYPES:
                                    target_type = DOS_BANDS_COLUMN_TYPES[key]
                                    casted_value = cast_value(value, target_type)
                                    if casted_value is not None:
                                        dos_bands_data[key] = casted_value

                            if dos_bands_data:
                                cols = ['id', 'hash']
                                vals = [material_id, hash_str]
                                updates = ['hash = EXCLUDED.hash']

                                for key, val in dos_bands_data.items():
                                    cols.append(f'"{key}"')
                                    vals.append(val)
                                    updates.append(f'"{key}" = EXCLUDED."{key}"')

                                col_list = ", ".join(cols)
                                placeholder_list = ", ".join(["%s"] * len(cols))
                                update_clause = ", ".join(updates)

                                cur.execute(
                                    f"""
                                    INSERT INTO dos_bands ({col_list})
                                    VALUES ({placeholder_list})
                                    ON CONFLICT (id) DO UPDATE SET {update_clause};
                                    """,
                                    vals
                                )
                        except Exception as e:
                            print(f"Error in adding DOS and Bands for {file}: {e}")
            except Exception as e:
                print(f"Transaction failed for {file}: {e}")

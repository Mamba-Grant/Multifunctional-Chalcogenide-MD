# changes from v3 -> v4: 
# 1) include precomputed connectivity matrix

from hashlib import md5
import os
import json
import re
from typing import Any, Dict, cast
# from ase.visualize import view
import numpy as np
from ase import Atoms
from ase.build import make_supercell
from ase.neighborlist import NeighborList
from ase.data import covalent_radii

import psycopg
from psycopg.abc import Query

from math import isnan, isinf
from numbers import Number

import matplotlib.pyplot as plt
plt.switch_backend('WebAgg')  # Use non-interactive backend

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
    "dos location",
]

conn = psycopg.connect(
    dbname="fastapi_psycopg3", user="postgres", password="", host="localhost"
)

for root, dirs, files in os.walk("./backend/json/"):
    for idx, file in enumerate(files):
        # Only accept valid json files
        if not file.endswith(".json"):
            print(f"WARNING: skipping {file}")
            continue

        with open(os.path.join(root, file), "r") as f:
            raw: Dict = json.load(f)
            data_blob: str = json.dumps(raw, sort_keys=True, indent=2)
            hash: str = md5(
                data_blob.encode("utf-8")
            ).hexdigest()  # For checking duplicates

            with conn.transaction():
                with conn.cursor() as cur:
                    # 1. Try to insert a hash (avoid duplicates)
                    cur.execute(
                        """
                        INSERT INTO material_keys (hash) VALUES (%s)
                        ON CONFLICT (hash) DO NOTHING
                        RETURNING id;
                    """,
                        (hash,),
                    )

                    result = cur.fetchone()
                    if result:
                        id: int = result[0]
                    else:
                        # Get existing id if conflict
                        cur.execute(
                            "SELECT id FROM material_keys WHERE hash = %s;", (hash,)
                        )
                        result = cur.fetchone()
                        if result:
                            id = result[0]
                        else:
                            print("ERROR: Could not return id from fetch.")

                    # 2. Great: we have an ID of a match or new entry, time to populate the columns
                    # At this stage, iterate over all key. value pairs in the json and try to add them
                    try:
                        for _, (key, value) in enumerate(raw.items()):
                            # Use a whitelist
                            if key not in valid_columns:
                                print(
                                    f"WARMING: skipped unknown key in --- {file} --- {key}"
                                )
                                continue

                            # Make sure certain types fit the schema (mostly convert missing/nan/inf to None)
                            blob: Any = value
                            if (
                                isinstance(value, str)
                                and value.strip().upper() == "UNKNOWN"
                            ):
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
                            cur.execute(
                                "SELECT 1 FROM material_data WHERE id = %s;", (id,)
                            )  # Check if exists at the id
                            if cur.fetchone() is None:
                                query: Query = cast(
                                    Query,
                                    f'INSERT INTO material_data (id, "{key}") VALUES (%s, %s);',
                                )
                                cur.execute(query, (id, blob))
                            else:
                                query: Query = cast(
                                    Query,
                                    f'UPDATE material_data SET "{key}" = %s WHERE id = %s;',
                                )
                                cur.execute(query, (blob, id))
                    except Exception as e:
                        print(f"Error in parsing JSON for migration: {e}")

                    # For the sake of searching, it will also be good to include data on elemental composition, i.e. what elements are in the material.
                    try:
                        formula = raw["formula"].lower()
                        # print(f"{formula}\n")
                        elements = re.findall(
                            r"[a-z]*", formula
                        )  # split by numeric, i.e. MnBi2Te4 -> [Mn, Bi, Te]
                        elements[:] = [
                            elm for elm in elements if elm
                        ]  # drop empty strings
                        query: Query = cast(
                            Query,
                            'UPDATE material_data SET "chemical_symbols" = %s WHERE id = %s;',
                        )
                        cur.execute(query, (elements, id))
                    except Exception as e:
                        print(f"Failed to split chemical composition: {e}")


                    # Try to build a bonding matrix:
                    #   This is a 2x2 supercell matrix, where each row and column represent each atom in the lattice. 
                    #   This is simplified such that a 1 represents a bond between the two atoms, a 0 no bond. 
                    #   The supercell is built at a significant performance cost, but is necessary to calculate inter-cell bonds.
                    # Could be improved: crystals with large numbers of atoms don't get very good lattices yet
                    try:
                        atoms = Atoms(
                            symbols=raw["symbols"],
                            positions=raw["positions"],
                            cell=raw["cell"]["array"],
                            pbc=True
                        )

                        # Build supercell
                        P = np.diag([2, 2, 1])  # supercell scaling matrix
                        supercell_atoms = make_supercell(atoms, P)

                        # Create neighbor list with cutoff distances for each atom
                        cutoffs = [covalent_radii[supercell_atoms.get_atomic_numbers()[i]] * 1.3 for i in range(len(supercell_atoms))]
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
                                    threshold = 1.25 * (radii[supercell_atoms.numbers[i]] + radii[supercell_atoms.numbers[j]]) # toss out long bonds
                                    if distance <= threshold:
                                        bond_matrix[i, j] = 1
                                        bond_matrix[j, i] = 1

                        # if raw["formula"] == "Bi2MnTe4":
                        #     np.set_printoptions(threshold=9999)
                        #     print(bond_matrix)
                        #     print(bond_matrix.shape)

                        query: Query = cast(
                            Query,
                            'UPDATE material_data SET "connectivity" = %s WHERE id = %s'
                        )
                        cur.execute(query, (bond_matrix.tolist(), id))

                    except Exception as e:
                        print(F"Failed to precompute cell and bond neighbors --- {e} --- in chemical {raw["formula"]}")

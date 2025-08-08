# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Direct Database Access for Devs
# author: Grant Saggars,
# credits: Grant Saggars,
# maintainer: Grant Saggars,
# email: g293s490@ku.edu
#
# Note: querying is designed with the web in mind, and these queries can be done for real with the web API (recommended, see `app/routers/vX_api.py`). This notebook seeks to demonstrate how basic queries are done with the minimal python involved, and output may not be very human-readable, especially compared to the web output.

# %%
# As usual, do imports
from typing import Any, List, Optional
from dotenv import load_dotenv
import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


# %% [markdown]
# Now, we may define a class (inheriting from pydantic BaseModel to be used as a row factory) having every parameter we want to grab from the query. Simply commenting a line out will cause it to not appear when queried.

# %%
class Material(BaseModel):
    """Class exposing the parameters for queries on our material."""
    id: Optional[int] = None
    search_vector: Any
    MP_ID: Optional[str] = Field(alias="MP-ID")
    formula: Optional[str]
    spacegroup: Optional[str]
    cell: Optional[dict]  # JSONB
    symbols: Optional[List[str]]
    positions: Optional[List[List[float]]]
    vdw_gap: Optional[float] = Field(alias="vdw gap")
    bond_length_deviation: Optional[Any] = Field(alias="bond length deviation")  # JSONB
    bond_angle_deviation: Optional[Any] = Field(alias="bond angle deviation")    # JSONB
    mass_density: Optional[float] = Field(alias="mass density")
    total_energy: Optional[float] = Field(alias="total energy")
    total_energy_soc: Optional[float] = Field(alias="total energy_soc")
    cohesive_energy: Optional[float] = Field(alias="cohesive energy")
    exfoliation_energy: Optional[float] = Field(alias="exfoliation energy")
    born_effective_charge_tensor: Optional[float] = Field(alias="born effective charge tensor")
    born_effective_charge_q_xy: Optional[float] = Field(alias="born effective charge q_xy")
    born_effective_charge_q_z: Optional[float] = Field(alias="born effective charge q_z")
    dielectric_constant_XY: Optional[float] = Field(alias="dielectric constant XY")
    dielectric_constant_Z: Optional[float] = Field(alias="dielectric constant Z")
    bader_charge: Optional[Any] = Field(alias="bader charge")  # JSONB
    density_of_states_at_fermi: Optional[float] = Field(alias="density of states at fermi")
    effective_mass: Optional[float] = Field(alias="effective mass")
    vbm: Optional[float]
    cbm: Optional[float]
    band_gap: Optional[float] = Field(alias="band gap")
    vbm_soc: Optional[float] = Field(alias="vbm soc")
    cbm_soc: Optional[float] = Field(alias="cbm soc")
    band_gap_soc: Optional[float] = Field(alias="band gap soc")
    layered: Optional[bool] = Field(alias="layered?")
    component_layers: Optional[List[str]] = Field(alias="component layers")
    KPath: Optional[List[str]]
    band_locations: Optional[str] = Field(alias="band locations")
    band_soc_location: Optional[str] = Field(alias="band soc location")
    dos_location: Optional[str] = Field(alias="dos location")


# %% [markdown]
# We query the database with simple PSQL. In the future, more complex queries may be implemented (namely searching with filtering). Please refer to the [postgres documentation](https://www.postgresql.org/docs/current/app-psql.html) for more information on the syntax and available commands!

# %%
def get_all(conninfo: str) -> list[Material]:
    with psycopg.connect(conninfo) as conn, conn.cursor(
        row_factory=class_row(Material)
    ) as cur:
        cur.execute("select * from material_data")
        records = cur.fetchall()
        return records

def search_contains(conninfo: str, query: str, limit: int = 20) -> Any:
    with psycopg.connect(conninfo) as conn, conn.cursor(
        row_factory=class_row(Material)
    ) as cur:
        cur.execute("""
            SELECT *,
                   CASE 
                       WHEN formula = %s THEN 100
                       WHEN formula ILIKE %s THEN 100
                       WHEN "MP-ID" = %s THEN 90
                       WHEN "MP-ID" ILIKE %s THEN 70
                       WHEN "spacegroup" = %s THEN 100
                       WHEN "spacegroup" ILIKE %s THEN 70
                       ELSE 50
                   END as relevance_score
            FROM material_data 
            WHERE formula ILIKE %s 
               OR "MP-ID" ILIKE %s
               OR "spacegroup" ILIKE %s
            ORDER BY relevance_score DESC, formula
            LIMIT %s
        """, [
                  query, query, query, query, query, query,  # relevance scoring
                  f'%{query}%', f'%{query}%', f'%{query}%',  # where conditions
                  limit
              ])

        records = cur.fetchall()
        return records

def get(conninfo: str, id: int) -> Material | None:
    with psycopg.connect(conninfo) as conn, conn.cursor(
        row_factory=class_row(Material)
    ) as cur:
        cur.execute("select * from material_data where id=%s", [id])
        record = cur.fetchone()
        return record

def delete(conninfo: str, id: int):
    with psycopg.connect(conninfo) as conn:
        conn.execute("delete from material_data where id=%s", [id])


# %% [markdown]
# For the sake of security, I'll grab our psql connection settings from the .env file:

# %%
class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_port: str
    db_name: str

    class Config:
        env_file = ".env"

load_dotenv() # force load the .env file

# settings defined in our .env for this; obfuscated for security.
settings: Settings = Settings()  # type: ignore
conninfo = f"user={settings.db_user} password={settings.db_password} host={settings.db_host} port={settings.db_port} dbname={settings.db_name}"

# %% [markdown]
# Now, to showcase some of these things:

# %%
print(search_contains(conninfo, "Bi"))

# %%
print(get(conninfo, 32))  # Get the 32nd item in our database

# %%
print(get_all(conninfo))

# %%

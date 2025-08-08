from typing import Any, List, Optional, cast
from fastapi import APIRouter, HTTPException, Query, Request
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field, Json
from psycopg.rows import class_row

from db import get_async_pool

router = APIRouter(prefix="/v1/material_data")


class Material(BaseModel):
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
    bond_angle_deviation: Optional[Any] = Field(alias="bond angle deviation")  # JSONB
    mass_density: Optional[float] = Field(alias="mass density")
    total_energy: Optional[float] = Field(alias="total energy")
    total_energy_soc: Optional[float] = Field(alias="total energy_soc")
    cohesive_energy: Optional[float] = Field(alias="cohesive energy")
    exfoliation_energy: Optional[float] = Field(alias="exfoliation energy")
    born_effective_charge_tensor: Optional[float] = Field(
        alias="born effective charge tensor"
    )
    born_effective_charge_q_xy: Optional[float] = Field(
        alias="born effective charge q_xy"
    )
    born_effective_charge_q_z: Optional[float] = Field(
        alias="born effective charge q_z"
    )
    dielectric_constant_XY: Optional[float] = Field(alias="dielectric constant XY")
    dielectric_constant_Z: Optional[float] = Field(alias="dielectric constant Z")
    bader_charge: Optional[Any] = Field(alias="bader charge")  # JSONB
    density_of_states_at_fermi: Optional[float] = Field(
        alias="density of states at fermi"
    )
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


@router.get("")
async def get_all() -> list[Material]:
    pool = get_async_pool()
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=class_row(Material)) as cur,
    ):
        await cur.execute("select * from material_data")
        records = await cur.fetchall()
        return records


@router.get("/query")
async def get_by_formula(formula: Optional[str] = None) -> Any:
    pool = get_async_pool()
    if not formula:
        return {"message": "No search query provided."}

    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=class_row(Material)) as cur,
    ):
        await cur.execute(
            "SELECT * FROM material_data WHERE formula ILIKE %s", [f"%{formula}%"]
        )
        records = await cur.fetchall()
        if not records:
            return {"message": "No materials found matching the query."}
        return records


@router.get("/search_contains")
async def search_contains(query: str, limit: int = 20) -> Any:
    """Substring search --- good for searching formula or text-based parameters. Just does many ILIKE checks, nothing fancy."""

    pool = get_async_pool()
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=class_row(Material)) as cur,
    ):
        await cur.execute(
            """
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
        """,
            [
                query,
                query,
                query,
                query,
                query,
                query,  # relevance scoring
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",  # where conditions
                limit,
            ],
        )

        records = await cur.fetchall()
        return records


@router.get("/{id}")
async def get(id: int) -> Material:
    pool = get_async_pool()
    async with (
        pool.connection() as conn,
        conn.cursor(row_factory=class_row(Material)) as cur,
    ):
        await cur.execute("select * from material_data where id=%s", [id])
        record = await cur.fetchone()
        if not record:
            raise HTTPException(404)
        return record


@router.delete("/{id}")
async def delete(id: int):
    pool = get_async_pool()
    async with pool.connection() as conn:
        await conn.execute("delete from material_data where id=%s", [id])

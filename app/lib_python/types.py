from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Material(BaseModel):
    id: Optional[int] = None
    search_vector: Any
    MP_ID: Optional[str] = Field(alias="MP-ID")
    connectivity: Optional[Any]
    chemical_symbols: Optional[List[str]]
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
    vbm: Optional[list[float] | list[list[float]]]
    cbm: Optional[list[float] | list[list[float]]]
    band_gap: Optional[float] = Field(alias="band gap")
    vbm_soc: Optional[list[float] | list[list[float]]] = Field(alias="vbm soc")
    cbm_soc: Optional[list[float] | list[list[float]]] = Field(alias="cbm soc")
    band_gap_soc: Optional[float] = Field(alias="band gap soc")
    layered: Optional[bool] = Field(alias="layered?")
    component_layers: Optional[List[str]] = Field(alias="component layers")
    KPath: Optional[List[str]]
    band_locations: Optional[str] = Field(alias="band locations")
    band_soc_location: Optional[str] = Field(alias="band soc location")
    dos_location: Optional[str] = Field(alias="dos location")
    hash: Optional[str]

class BandDOS(BaseModel):
    bands: Optional[List] = Field(default=None, alias="bands")
    band_distances: Optional[List] = Field(default=None, alias="band distances")
    kpoints: Optional[Dict] = Field(default=None, alias="KPoints")
    bands_soc: Optional[List] = Field(default=None, alias="bands soc")
    band_distances_soc: Optional[List] = Field(default=None, alias="band distances soc")
    density_of_states_energies: Optional[List] = Field(default=None, alias="density of states energies")
    total_density_of_states: Optional[List] = Field(default=None, alias="total density of states")
    projected_density_of_states: Optional[List[List]] = Field(default=None, alias="projected density of states")
    fermi_energy: Optional[float] = Field(default=None, alias="fermi energy")


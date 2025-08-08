-- Trigram extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS hashtable;
CREATE TABLE hashtable (
    id bigserial PRIMARY key,
    hash TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

DROP TABLE IF EXISTS data;
CREATE TABLE data (
    id INTEGER PRIMARY KEY REFERENCES hashtable(id) ON DELETE CASCADE,
    search_vector tsvector,
    hash TEXT UNIQUE,
    "MP-ID" TEXT,
    "formula" TEXT,
    "chemical_symbols" TEXT[],
    "spacegroup" TEXT,
    "cell" JSONB,
    "symbols" TEXT[],
    "connectivity" int[][],
    "positions" DOUBLE PRECISION[],
    "vdw gap" DOUBLE PRECISION,
    "bond length deviation" JSONB,
    "bond angle deviation" JSONB,
    "mass density" DOUBLE PRECISION,
    "total energy" DOUBLE PRECISION,
    "total energy_soc" DOUBLE PRECISION,
    "cohesive energy" DOUBLE PRECISION,
    "exfoliation energy" DOUBLE PRECISION,
    "born effective charge tensor" DOUBLE PRECISION,
    "born effective charge q_xy" DOUBLE PRECISION,
    "born effective charge q_z" DOUBLE PRECISION,
    "dielectric constant XY" DOUBLE PRECISION,
    "dielectric constant Z" DOUBLE PRECISION,
    "bader charge" JSONB,
    "density of states at fermi" DOUBLE PRECISION,
    "effective mass" DOUBLE PRECISION,
    "vbm" DOUBLE PRECISION[],
    "cbm" DOUBLE PRECISION[],
    "band gap" DOUBLE PRECISION,
    "vbm soc" DOUBLE PRECISION[],
    "cbm soc" DOUBLE PRECISION[],
    "band gap soc" DOUBLE PRECISION,
    "layered?" BOOLEAN,
    "component layers" TEXT[],
    "KPath" TEXT[],
    "band locations" TEXT,
    "band soc location" TEXT,
    "dos location" TEXT
);

DROP TABLE IF EXISTS dos_bands;
CREATE TABLE dos_bands (
    id INTEGER PRIMARY KEY REFERENCES hashtable(id) ON DELETE CASCADE,
    hash TEXT UNIQUE,
    "bands" DOUBLE PRECISION[],
    "band distances" DOUBLE PRECISION[],
    "KPoints" JSONB,
    "bands soc" DOUBLE PRECISION[],
    "band distances soc" DOUBLE PRECISION[],
    "density of states energies" DOUBLE PRECISION[],
    "total density of states" DOUBLE PRECISION[],
    "projected density of states" JSONB,
    "fermi energy" DOUBLE PRECISION
);

-- Create a function to update the search vector
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW."MP-ID", '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.formula, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.spacegroup, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.symbols, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update search vector
CREATE TRIGGER update_search_vector_trigger
    BEFORE INSERT OR UPDATE ON data
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Create GIN index for fast searching
CREATE INDEX idx_material_search ON data USING GIN(search_vector);

-- Create trigram index on formula
CREATE INDEX idx_formula_trgm ON data USING GIN (formula gin_trgm_ops);

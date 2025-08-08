-- Trigram extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE material_data (
    id SERIAL PRIMARY KEY,
    search_vector tsvector,
    "MP-ID" TEXT,
    "formula" TEXT,
    "spacegroup" TEXT,
    "cell" JSONB,
    "symbols" TEXT[],
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
    "vbm" DOUBLE PRECISION,
    "cbm" DOUBLE PRECISION,
    "band gap" DOUBLE PRECISION,
    "vbm soc" DOUBLE PRECISION,
    "cbm soc" DOUBLE PRECISION,
    "band gap soc" DOUBLE PRECISION,
    "layered?" BOOLEAN,
    "component layers" TEXT[],
    "KPath" TEXT[],
    "band locations" TEXT,
    "band soc location" TEXT,
    "dos location" TEXT
);

create table material_keys (
    id bigserial PRIMARY key,
    hash TEXT UNIQUE
);

-- Create a function to update the search vector
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.formula, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW."MP-ID", '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.spacegroup, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.symbols, ' '), '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update search vector
CREATE TRIGGER update_search_vector_trigger
    BEFORE INSERT OR UPDATE ON material_data
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Create GIN index for fast searching
CREATE INDEX idx_material_search ON material_data USING GIN(search_vector);

-- Create trigram index on formula
CREATE INDEX idx_formula_trgm ON material_data USING GIN (formula gin_trgm_ops);

create table material_data (
    id bigserial PRIMARY key,
    data JSONB UNIQUE
);

create table material_keys (
    id bigserial PRIMARY key,
    data_hash TEXT UNIQUE
);

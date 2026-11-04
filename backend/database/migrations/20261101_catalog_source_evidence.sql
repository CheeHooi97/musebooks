CREATE TABLE catalog_source_evidence (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(24) NOT NULL CHECK (entity_type IN ('work', 'edition', 'person', 'work_credit', 'work_image', 'edition_image')),
    entity_id VARCHAR(240) NOT NULL,
    field_key VARCHAR(180) NOT NULL,
    source_id VARCHAR(80) NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    captured_at TIMESTAMPTZ NOT NULL,
    grant_field VARCHAR(64) NOT NULL,
    scope VARCHAR(32) NOT NULL CHECK (scope IN ('bibliography', 'product_images')),
    source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT catalog_source_evidence_capture_unique UNIQUE (entity_type, entity_id, field_key, source_id, captured_at)
);

CREATE INDEX catalog_source_evidence_source_scope_idx
    ON catalog_source_evidence (source_id, scope, grant_field);

CREATE INDEX catalog_source_evidence_entity_idx
    ON catalog_source_evidence (entity_type, entity_id);

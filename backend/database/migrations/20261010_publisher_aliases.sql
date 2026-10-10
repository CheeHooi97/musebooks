-- Preserve the source values while normalizing publisher identities.
CREATE TABLE IF NOT EXISTS publisher_name_repairs (
 edition_id text PRIMARY KEY REFERENCES editions(id),
 original_publisher text NOT NULL,
 canonical_publisher text NOT NULL,
 repaired_at timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION musebooks_canonical_publisher(value text)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
 SELECT CASE
  WHEN btrim(value) IN ('尖端','尖端出版','尖端出版 / 尖端出版')
   OR btrim(value) ~ '^尖端[[:space:]]+作者[：:]'
  THEN '尖端出版'
  ELSE value
 END;
$$;

CREATE OR REPLACE FUNCTION musebooks_normalize_publisher() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 NEW.publisher := musebooks_canonical_publisher(NEW.publisher);
 RETURN NEW;
END; $$;
-- PostgreSQL runs same-event triggers alphabetically, before identity creation.
DROP TRIGGER IF EXISTS musebooks_edition_00_publisher ON editions;
CREATE TRIGGER musebooks_edition_00_publisher BEFORE INSERT OR UPDATE OF publisher ON editions
 FOR EACH ROW EXECUTE FUNCTION musebooks_normalize_publisher();

INSERT INTO publisher_name_repairs(edition_id,original_publisher,canonical_publisher)
 SELECT id,publisher,musebooks_canonical_publisher(publisher) FROM editions
 WHERE publisher IS DISTINCT FROM musebooks_canonical_publisher(publisher)
 ON CONFLICT(edition_id) DO NOTHING;
UPDATE editions SET publisher=musebooks_canonical_publisher(publisher)
 WHERE publisher IS DISTINCT FROM musebooks_canonical_publisher(publisher);
UPDATE product_lines SET publisher_company_id=musebooks_catalog_identity('publisher','尖端出版')
 WHERE publisher_company_id IN (
  SELECT id FROM companies WHERE canonical_name IS DISTINCT FROM musebooks_canonical_publisher(canonical_name)
 );

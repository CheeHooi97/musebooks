-- One model is often credited under several names in works.featured_names
-- ("岸明日香,Asuka Kishi"). Each alias is recorded against the canonical person,
-- and the credit trigger resolves it only when that person's main name is
-- credited on the same work, so a short shared alias ("葵", "Nanami") is never
-- folded into a model who is not listed.
CREATE TABLE IF NOT EXISTS person_aliases (
 alias_slug varchar(100) NOT NULL,
 person_id bigint NOT NULL REFERENCES people(id) ON DELETE CASCADE,
 alias_name text NOT NULL,
 source varchar(40) NOT NULL DEFAULT 'credit_list',
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY (alias_slug, person_id)
);
CREATE INDEX IF NOT EXISTS idx_person_aliases_person ON person_aliases(person_id);

-- Roles that can read people (the API and importers) also need the aliases,
-- because the credit trigger runs with the invoking role's privileges.
DO $$
DECLARE grantee text;
BEGIN
 FOR grantee IN SELECT DISTINCT g.grantee FROM information_schema.role_table_grants g
  WHERE g.table_schema='public' AND g.table_name='people' AND g.privilege_type='SELECT' AND g.grantee <> current_user AND g.grantee <> 'PUBLIC' LOOP
  EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE person_aliases TO %I', grantee);
 END LOOP;
END $$;

CREATE OR REPLACE FUNCTION musebooks_sync_work_credits() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE credited text; person_slug text; linked_person bigint; listed text[];
BEGIN
 DELETE FROM work_people WHERE work_id=NEW.id AND credit_source='legacy_credit';
 SELECT COALESCE(array_agg(musebooks_catalog_identity('model',btrim(value))), '{}') INTO listed
  FROM regexp_split_to_table(COALESCE(NEW.featured_names,''), ',') AS value WHERE btrim(value)<>'';
 -- Credit in listed order so the canonical (first) name becomes the credited name.
 FOR credited IN SELECT btrim(t.value) FROM regexp_split_to_table(COALESCE(NEW.featured_names,''), ',') WITH ORDINALITY AS t(value, position)
  WHERE btrim(t.value)<>'' ORDER BY t.position LOOP
  person_slug := musebooks_catalog_identity('model',credited);
  linked_person := NULL;
  SELECT pa.person_id INTO linked_person FROM person_aliases pa JOIN people p ON p.id=pa.person_id
   WHERE pa.alias_slug=person_slug AND p.slug=ANY(listed) AND p.slug<>person_slug
   ORDER BY array_position(listed, p.slug), pa.person_id LIMIT 1;
  IF linked_person IS NULL THEN
   INSERT INTO people(slug,canonical_public_name,original_name,profile_source_confidence,created_at,updated_at)
   VALUES(person_slug,credited,credited,'catalog_credit',now(),now()) ON CONFLICT(slug) DO NOTHING;
   SELECT id INTO linked_person FROM people WHERE slug=person_slug;
  END IF;
  INSERT INTO work_people(work_id,person_id,role,credited_name,credit_source,created_at,updated_at)
  VALUES(NEW.id,linked_person,'featured',credited,'legacy_credit',now(),now()) ON CONFLICT DO NOTHING;
 END LOOP;
 IF COALESCE(btrim(NEW.cover_url),'')<>'' THEN
  INSERT INTO catalog_media(entity_type,entity_id,media_type,original_url,storage_url,is_primary,created_at,updated_at)
  VALUES('work',NEW.id,'cover',NEW.cover_url,NEW.cover_url,true,now(),now())
  ON CONFLICT(entity_type,entity_id,media_type) DO UPDATE SET original_url=EXCLUDED.original_url,storage_url=EXCLUDED.storage_url,updated_at=now();
 END IF;
 RETURN NEW;
END; $$;

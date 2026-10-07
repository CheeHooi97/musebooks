-- Run while connected to musebooks as a PostgreSQL administrator.
-- Existing data is preserved. Changes apply only to the public schema in musebooks.
BEGIN;
DO $$
DECLARE object record;
BEGIN
  IF current_database() <> 'musebooks' THEN
    RAISE EXCEPTION 'Connect to musebooks before running this script';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tcguser') THEN
    RAISE EXCEPTION 'The tcguser role must already exist';
  END IF;
  FOR object IN
    SELECT n.nspname, c.relname
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p')
      AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid = 'pg_class'::regclass AND d.objid = c.oid AND d.deptype = 'e')
  LOOP
    EXECUTE format('ALTER TABLE %I.%I OWNER TO tcguser', object.nspname, object.relname);
  END LOOP;
  FOR object IN
    SELECT n.nspname, c.relname
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'S'
      AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid = 'pg_class'::regclass AND d.objid = c.oid AND d.deptype = 'e')
  LOOP
    EXECUTE format('ALTER SEQUENCE %I.%I OWNER TO tcguser', object.nspname, object.relname);
  END LOOP;
END $$;
GRANT CONNECT ON DATABASE musebooks TO tcguser;
GRANT USAGE, CREATE ON SCHEMA public TO tcguser;
COMMIT;

UPDATE catalog_media
SET permission_scope = 'unreviewed',
    permission_evidence_url = '',
    permission_basis = '',
    permission_reviewed_at = NULL
WHERE permission_scope IS NULL OR btrim(permission_scope) = '';

ALTER TABLE catalog_media
    ADD CONSTRAINT catalog_media_permission_scope_check
    CHECK (permission_scope IN ('unreviewed', 'revoked', 'remote_display', 'display_and_copy'));

ALTER TABLE catalog_media
    ADD CONSTRAINT catalog_media_permission_evidence_check
    CHECK (
        permission_scope NOT IN ('remote_display', 'display_and_copy')
        OR (
            COALESCE(permission_evidence_url LIKE 'https://%', FALSE)
            AND COALESCE(btrim(permission_basis) <> '', FALSE)
            AND permission_reviewed_at IS NOT NULL
            AND COALESCE(source_url LIKE 'https://%', FALSE)
            AND COALESCE(original_url LIKE 'https://%', FALSE)
            AND COALESCE(storage_url LIKE 'https://%', FALSE)
            AND COALESCE(permission_scope = 'display_and_copy' OR original_url = storage_url, FALSE)
        )
    );

CREATE OR REPLACE FUNCTION musebooks_reset_changed_media_permission() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF ROW(NEW.entity_type, NEW.entity_id, NEW.media_type, NEW.original_url, NEW.storage_url, NEW.source_url)
       IS DISTINCT FROM
       ROW(OLD.entity_type, OLD.entity_id, OLD.media_type, OLD.original_url, OLD.storage_url, OLD.source_url) THEN
        NEW.permission_scope := 'unreviewed';
        NEW.permission_evidence_url := '';
        NEW.permission_basis := '';
        NEW.permission_reviewed_at := NULL;
    END IF;
    RETURN NEW;
END; $$;

CREATE TRIGGER catalog_media_reset_permission_before_identity_change
    BEFORE UPDATE ON catalog_media
    FOR EACH ROW EXECUTE FUNCTION musebooks_reset_changed_media_permission();

-- Additive normalization. Existing works, editions, listing IDs and observations
-- remain canonical; triggers keep normalized records current for every importer.
CREATE OR REPLACE FUNCTION musebooks_catalog_identity(kind text, value text)
RETURNS text LANGUAGE sql IMMUTABLE STRICT AS $$
 SELECT kind || '-' || encode(sha256(convert_to(lower(btrim(value)), 'UTF8')), 'hex');
$$;

INSERT INTO markets(country_code,slug,catalog_status,created_at,updated_at)
 SELECT upper(code),lower(code),'active',now(),now() FROM origins
 ON CONFLICT (country_code) DO NOTHING;

CREATE OR REPLACE FUNCTION musebooks_sync_source() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 INSERT INTO marketplaces(code,name,region,created_at,updated_at)
 VALUES(NEW.id,NEW.name,NEW.region,now(),now())
 ON CONFLICT(code) DO UPDATE SET name=EXCLUDED.name,region=EXCLUDED.region,updated_at=now();
 SELECT id INTO NEW.marketplace_id FROM marketplaces WHERE code=NEW.id;
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_source_identity BEFORE INSERT OR UPDATE ON sources
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_source();
UPDATE sources SET name=name;

CREATE OR REPLACE FUNCTION musebooks_sync_work_market() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 INSERT INTO markets(country_code,slug,catalog_status,created_at,updated_at)
 VALUES(upper(NEW.origin_code),lower(NEW.origin_code),'active',now(),now()) ON CONFLICT(country_code) DO NOTHING;
 SELECT id INTO NEW.origin_market_id FROM markets WHERE country_code=upper(NEW.origin_code);
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_work_market BEFORE INSERT OR UPDATE ON works
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_work_market();

CREATE OR REPLACE FUNCTION musebooks_sync_work_credits() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE credited text; person_slug text; linked_person bigint;
BEGIN
 DELETE FROM work_people WHERE work_id=NEW.id AND credit_source='legacy_credit';
 FOR credited IN SELECT DISTINCT btrim(value) FROM regexp_split_to_table(COALESCE(NEW.featured_names,''), ',') AS value WHERE btrim(value)<>'' LOOP
  person_slug := musebooks_catalog_identity('model',credited);
  INSERT INTO people(slug,canonical_public_name,original_name,profile_source_confidence,created_at,updated_at)
  VALUES(person_slug,credited,credited,'catalog_credit',now(),now()) ON CONFLICT(slug) DO NOTHING;
  SELECT id INTO linked_person FROM people WHERE slug=person_slug;
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
CREATE TRIGGER musebooks_work_credits AFTER INSERT OR UPDATE OF featured_names,cover_url ON works
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_work_credits();
UPDATE works SET featured_names=featured_names;

CREATE OR REPLACE FUNCTION musebooks_sync_edition_identity() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE company_key text; series_key text;
BEGIN
 IF COALESCE(btrim(NEW.publisher),'')<>'' THEN
  company_key := musebooks_catalog_identity('publisher',NEW.publisher);
  INSERT INTO companies(id,slug,name,canonical_name,status,verification_status,created_date_time,updated_date_time)
  VALUES(company_key,company_key,btrim(NEW.publisher),btrim(NEW.publisher),true,'catalog_credit',now(),now()) ON CONFLICT(id) DO NOTHING;
  NEW.publisher_company_id:=company_key;
 ELSE
  NEW.publisher_company_id:=NULL;
 END IF;
 IF COALESCE(btrim(NEW.series_name),'')<>'' THEN
  series_key:=musebooks_catalog_identity('series',COALESCE(company_key,'') || ':' || NEW.series_name);
  INSERT INTO product_lines(slug,canonical_name,publisher_company_id,created_at,updated_at)
  VALUES(series_key,btrim(NEW.series_name),company_key,now(),now()) ON CONFLICT(slug) DO NOTHING;
  SELECT id INTO NEW.product_line_id FROM product_lines WHERE slug=series_key;
 ELSE
  NEW.product_line_id:=NULL;
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_edition_identity BEFORE INSERT OR UPDATE OF publisher,series_name ON editions
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_edition_identity();

CREATE OR REPLACE FUNCTION musebooks_sync_edition_media() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF COALESCE(btrim(NEW.cover_url),'')<>'' THEN
  INSERT INTO catalog_media(entity_type,entity_id,media_type,original_url,storage_url,source_url,is_primary,created_at,updated_at)
  VALUES('edition',NEW.id,'cover',COALESCE(NULLIF(NEW.original_cover_url,''),NEW.cover_url),
   COALESCE(NULLIF(NEW.cover_object_key,''),NEW.cover_url),NEW.metadata_source_url,true,now(),now())
  ON CONFLICT(entity_type,entity_id,media_type) DO UPDATE SET original_url=EXCLUDED.original_url,storage_url=EXCLUDED.storage_url,source_url=EXCLUDED.source_url,updated_at=now();
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_edition_media AFTER INSERT OR UPDATE OF cover_url,original_cover_url,cover_object_key,metadata_source_url ON editions
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_edition_media();
UPDATE editions SET publisher=publisher,cover_url=cover_url;

CREATE UNIQUE INDEX ux_active_listing_marketplace_external ON active_listings(marketplace_id,external_listing_id);
CREATE UNIQUE INDEX ux_sold_listing_marketplace_external ON sold_listings(marketplace_id,external_listing_id);
CREATE INDEX idx_work_people_person ON work_people(person_id,work_id) WHERE role='featured';
CREATE INDEX idx_active_listing_recent ON active_listings(observed_at DESC,source_listing_id) WHERE is_active;
CREATE INDEX idx_sold_listing_recent ON sold_listings(observed_at DESC,source_listing_id) WHERE review_status='linked';
ALTER TABLE active_listings ADD CONSTRAINT active_listing_format CHECK(format IN ('physical','digital'));
ALTER TABLE sold_listings ADD CONSTRAINT sold_listing_physical CHECK(format='physical');
ALTER TABLE active_listings ADD CONSTRAINT active_listing_source FOREIGN KEY(source_listing_id) REFERENCES listings(id);
ALTER TABLE sold_listings ADD CONSTRAINT sold_listing_source FOREIGN KEY(source_listing_id) REFERENCES listings(id);
ALTER TABLE listing_matches ADD CONSTRAINT listing_match_source FOREIGN KEY(source_listing_id) REFERENCES listings(id);

CREATE OR REPLACE FUNCTION musebooks_sync_listing() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE market_id bigint; actual_format text; source_kind text;
BEGIN
 SELECT marketplace_id,kind INTO market_id,source_kind FROM sources WHERE id=NEW.source_id;
 actual_format:=CASE WHEN NEW.format_candidate IN ('physical','digital') THEN NEW.format_candidate
  WHEN NEW.price_type='digital' THEN 'digital'
  WHEN source_kind IN ('marketplace','marketplace_c2c','auction','flea_market') THEN 'physical'
  ELSE NULL END;
 IF NEW.edition_id IS NOT NULL AND NEW.edition_id<>'' AND NEW.status<>'excluded' THEN
  INSERT INTO listing_matches(source_listing_id,edition_id,match_method,review_status,created_at,updated_at)
  VALUES(NEW.id,NEW.edition_id,'legacy_edition_link','linked',now(),now())
  ON CONFLICT(source_listing_id) DO UPDATE SET edition_id=EXCLUDED.edition_id,review_status='linked',updated_at=now();
 ELSE
  UPDATE listing_matches SET review_status='unmatched',updated_at=now() WHERE source_listing_id=NEW.id;
 END IF;
 IF NEW.status='active' AND actual_format IS NOT NULL AND market_id IS NOT NULL THEN
  INSERT INTO active_listings(source_listing_id,marketplace_id,source_id,external_listing_id,edition_id,original_url,title,
   format,price_minor,original_currency_code,price_type,condition,seller_location,shipping_text,observed_at,last_seen_at,
   is_active,active_at,created_at,updated_at)
  VALUES(NEW.id,market_id,NEW.source_id,NEW.external_id,NULLIF(NEW.edition_id,''),NEW.url,NEW.title,
   actual_format,NULLIF(NEW.price_minor,0),NEW.currency,NEW.price_type,NEW.condition,NEW.seller_location,NEW.shipping_text,
   NEW.observed_at,NEW.last_seen_at,true,NEW.observed_at,NEW.created_at,now())
  ON CONFLICT(source_listing_id) DO UPDATE SET edition_id=EXCLUDED.edition_id,format=EXCLUDED.format,original_url=EXCLUDED.original_url,title=EXCLUDED.title,
   price_minor=EXCLUDED.price_minor,original_currency_code=EXCLUDED.original_currency_code,price_type=EXCLUDED.price_type,
   condition=EXCLUDED.condition,seller_location=EXCLUDED.seller_location,shipping_text=EXCLUDED.shipping_text,
   observed_at=EXCLUDED.observed_at,last_seen_at=EXCLUDED.last_seen_at,is_active=true,inactive_at=NULL,inactive_reason='',updated_at=now();
 ELSE
  UPDATE active_listings SET is_active=false,inactive_at=NEW.observed_at,inactive_reason=NEW.status,
   edition_id=NULLIF(NEW.edition_id,''),last_seen_at=NEW.last_seen_at,updated_at=now() WHERE source_listing_id=NEW.id;
 END IF;
 IF NEW.status='completed' AND actual_format='physical' AND source_kind IN ('marketplace','marketplace_c2c','auction','flea_market') AND market_id IS NOT NULL THEN
  INSERT INTO sold_listings(source_listing_id,marketplace_id,source_id,external_listing_id,edition_id,original_url,title,
   format,price_minor,original_currency_code,price_type,condition,seller_location,shipping_text,observed_at,last_seen_at,
   review_status,created_at,updated_at)
  VALUES(NEW.id,market_id,NEW.source_id,NEW.external_id,NULLIF(NEW.edition_id,''),NEW.url,NEW.title,
   'physical',NULLIF(NEW.price_minor,0),NEW.currency,NEW.price_type,NEW.condition,NEW.seller_location,NEW.shipping_text,
   NEW.observed_at,NEW.last_seen_at,'linked',NEW.created_at,now())
  ON CONFLICT(source_listing_id) DO UPDATE SET edition_id=EXCLUDED.edition_id,price_minor=EXCLUDED.price_minor,
   original_currency_code=EXCLUDED.original_currency_code,observed_at=EXCLUDED.observed_at,review_status='linked',updated_at=now();
 ELSIF NEW.status='excluded' OR actual_format='digital' THEN
  UPDATE sold_listings SET review_status='excluded',updated_at=now() WHERE source_listing_id=NEW.id;
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_listing_lifecycle AFTER INSERT OR UPDATE ON listings
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_listing();
UPDATE listings SET status=status;

CREATE OR REPLACE FUNCTION musebooks_sync_sale_evidence() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.status='completed' AND NEW.format='physical' THEN
  UPDATE sold_listings SET status_evidence=NEW.status_evidence,sold_at=NEW.source_timestamp,updated_at=now()
   WHERE source_listing_id=NEW.listing_id AND observed_at<=NEW.observed_at;
 END IF;
 RETURN NEW;
END; $$;
CREATE TRIGGER musebooks_sale_evidence AFTER INSERT ON listing_observations
 FOR EACH ROW EXECUTE FUNCTION musebooks_sync_sale_evidence();
UPDATE sold_listings AS sales SET status_evidence=evidence.status_evidence,sold_at=evidence.source_timestamp
 FROM (SELECT DISTINCT ON(listing_id) listing_id,status_evidence,source_timestamp
  FROM listing_observations WHERE status='completed' AND format='physical' ORDER BY listing_id,observed_at DESC,id DESC) AS evidence
 WHERE sales.source_listing_id=evidence.listing_id;

ALTER TABLE works
    ADD COLUMN IF NOT EXISTS issue_date timestamptz,
    ADD COLUMN IF NOT EXISTS issue_date_precision varchar(16) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS issue_date_source_url varchar(1000) NOT NULL DEFAULT '';

ALTER TABLE editions
    ADD COLUMN IF NOT EXISTS publication_date timestamptz,
    ADD COLUMN IF NOT EXISTS publication_date_precision varchar(16) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS publication_date_source_url varchar(1000) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS store_release_date timestamptz,
    ADD COLUMN IF NOT EXISTS store_release_date_precision varchar(16) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS store_release_date_source_url varchar(1000) NOT NULL DEFAULT '';

ALTER TABLE listings
    ADD COLUMN IF NOT EXISTS price_basis varchar(24) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS price_components jsonb NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE listing_observations
    ADD COLUMN IF NOT EXISTS price_basis varchar(24) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS price_components jsonb NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE active_listings
    ADD COLUMN IF NOT EXISTS price_basis varchar(24) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS price_components jsonb NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE sold_listings
    ADD COLUMN IF NOT EXISTS price_basis varchar(24) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS price_components jsonb NOT NULL DEFAULT '[]'::jsonb;

UPDATE listings SET price_components = '[]'::jsonb WHERE price_components IS NULL;
UPDATE listing_observations SET price_components = '[]'::jsonb WHERE price_components IS NULL;
UPDATE active_listings SET price_components = '[]'::jsonb WHERE price_components IS NULL;
UPDATE sold_listings SET price_components = '[]'::jsonb WHERE price_components IS NULL;
UPDATE listings SET price_basis = '' WHERE price_basis IS NULL;
UPDATE listing_observations SET price_basis = '' WHERE price_basis IS NULL;
UPDATE active_listings SET price_basis = '' WHERE price_basis IS NULL;
UPDATE sold_listings SET price_basis = '' WHERE price_basis IS NULL;

ALTER TABLE listings ALTER COLUMN price_basis SET DEFAULT '', ALTER COLUMN price_basis SET NOT NULL,
    ALTER COLUMN price_components SET DEFAULT '[]'::jsonb, ALTER COLUMN price_components SET NOT NULL;
ALTER TABLE listing_observations ALTER COLUMN price_basis SET DEFAULT '', ALTER COLUMN price_basis SET NOT NULL,
    ALTER COLUMN price_components SET DEFAULT '[]'::jsonb, ALTER COLUMN price_components SET NOT NULL;
ALTER TABLE active_listings ALTER COLUMN price_basis SET DEFAULT '', ALTER COLUMN price_basis SET NOT NULL,
    ALTER COLUMN price_components SET DEFAULT '[]'::jsonb, ALTER COLUMN price_components SET NOT NULL;
ALTER TABLE sold_listings ALTER COLUMN price_basis SET DEFAULT '', ALTER COLUMN price_basis SET NOT NULL,
    ALTER COLUMN price_components SET DEFAULT '[]'::jsonb, ALTER COLUMN price_components SET NOT NULL;

UPDATE active_listings AS a SET price_basis = l.price_basis, price_components = l.price_components
FROM listings AS l WHERE a.source_listing_id = l.id;
UPDATE sold_listings AS s SET price_basis = l.price_basis, price_components = l.price_components
FROM listings AS l WHERE s.source_listing_id = l.id;

UPDATE works SET issue_date_precision = '', issue_date_source_url = ''
WHERE issue_date_precision IS NULL OR issue_date_source_url IS NULL;
UPDATE editions SET publication_date_precision = '', publication_date_source_url = '',
    store_release_date_precision = '', store_release_date_source_url = ''
WHERE publication_date_precision IS NULL OR publication_date_source_url IS NULL
    OR store_release_date_precision IS NULL OR store_release_date_source_url IS NULL;
ALTER TABLE works ALTER COLUMN issue_date_precision SET DEFAULT '', ALTER COLUMN issue_date_precision SET NOT NULL,
    ALTER COLUMN issue_date_source_url SET DEFAULT '', ALTER COLUMN issue_date_source_url SET NOT NULL;
ALTER TABLE editions ALTER COLUMN publication_date_precision SET DEFAULT '', ALTER COLUMN publication_date_precision SET NOT NULL,
    ALTER COLUMN publication_date_source_url SET DEFAULT '', ALTER COLUMN publication_date_source_url SET NOT NULL,
    ALTER COLUMN store_release_date_precision SET DEFAULT '', ALTER COLUMN store_release_date_precision SET NOT NULL,
    ALTER COLUMN store_release_date_source_url SET DEFAULT '', ALTER COLUMN store_release_date_source_url SET NOT NULL;

DO $$ BEGIN
    ALTER TABLE works ADD CONSTRAINT works_issue_date_precision_check
        CHECK (issue_date_precision IN ('', 'day', 'month', 'year'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE editions ADD CONSTRAINT editions_publication_date_precision_check
        CHECK (publication_date_precision IN ('', 'day', 'month', 'year'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE editions ADD CONSTRAINT editions_store_release_date_precision_check
        CHECK (store_release_date_precision IN ('', 'day', 'month', 'year'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE listings ADD CONSTRAINT listings_price_basis_check
        CHECK (price_basis IN ('', 'list', 'sale', 'coupon', 'used_asking', 'completed_sale'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE listing_observations ADD CONSTRAINT listing_observations_price_basis_check
        CHECK (price_basis IN ('', 'list', 'sale', 'coupon', 'used_asking', 'completed_sale'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE active_listings ADD CONSTRAINT active_listings_price_basis_check
        CHECK (price_basis IN ('', 'list', 'sale', 'coupon', 'used_asking'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE sold_listings ADD CONSTRAINT sold_listings_price_basis_check
        CHECK (price_basis IN ('', 'completed_sale'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

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
   format,price_minor,original_currency_code,price_type,price_basis,price_components,condition,seller_location,shipping_text,observed_at,last_seen_at,
   is_active,active_at,created_at,updated_at)
  VALUES(NEW.id,market_id,NEW.source_id,NEW.external_id,NULLIF(NEW.edition_id,''),NEW.url,NEW.title,
   actual_format,NULLIF(NEW.price_minor,0),NEW.currency,NEW.price_type,NEW.price_basis,NEW.price_components,NEW.condition,NEW.seller_location,NEW.shipping_text,
   NEW.observed_at,NEW.last_seen_at,true,NEW.observed_at,NEW.created_at,now())
  ON CONFLICT(source_listing_id) DO UPDATE SET edition_id=EXCLUDED.edition_id,format=EXCLUDED.format,original_url=EXCLUDED.original_url,title=EXCLUDED.title,
   price_minor=EXCLUDED.price_minor,original_currency_code=EXCLUDED.original_currency_code,price_type=EXCLUDED.price_type,
   price_basis=EXCLUDED.price_basis,price_components=EXCLUDED.price_components,condition=EXCLUDED.condition,seller_location=EXCLUDED.seller_location,shipping_text=EXCLUDED.shipping_text,
   observed_at=EXCLUDED.observed_at,last_seen_at=EXCLUDED.last_seen_at,is_active=true,inactive_at=NULL,inactive_reason='',updated_at=now();
 ELSE
  UPDATE active_listings SET is_active=false,inactive_at=NEW.observed_at,inactive_reason=NEW.status,
   edition_id=NULLIF(NEW.edition_id,''),last_seen_at=NEW.last_seen_at,updated_at=now() WHERE source_listing_id=NEW.id;
 END IF;
 IF NEW.status='completed' AND actual_format='physical' AND source_kind IN ('marketplace','marketplace_c2c','auction','flea_market') AND market_id IS NOT NULL THEN
  INSERT INTO sold_listings(source_listing_id,marketplace_id,source_id,external_listing_id,edition_id,original_url,title,
   format,price_minor,original_currency_code,price_type,price_basis,price_components,condition,seller_location,shipping_text,observed_at,last_seen_at,
   review_status,created_at,updated_at)
  VALUES(NEW.id,market_id,NEW.source_id,NEW.external_id,NULLIF(NEW.edition_id,''),NEW.url,NEW.title,
   'physical',NULLIF(NEW.price_minor,0),NEW.currency,NEW.price_type,NEW.price_basis,NEW.price_components,NEW.condition,NEW.seller_location,NEW.shipping_text,
   NEW.observed_at,NEW.last_seen_at,'linked',NEW.created_at,now())
  ON CONFLICT(source_listing_id) DO UPDATE SET edition_id=EXCLUDED.edition_id,price_minor=EXCLUDED.price_minor,
   original_currency_code=EXCLUDED.original_currency_code,price_type=EXCLUDED.price_type,price_basis=EXCLUDED.price_basis,price_components=EXCLUDED.price_components,
   observed_at=EXCLUDED.observed_at,review_status='linked',updated_at=now();
 ELSIF NEW.status='excluded' OR actual_format='digital' THEN
  UPDATE sold_listings SET review_status='excluded',updated_at=now() WHERE source_listing_id=NEW.id;
 END IF;
 RETURN NEW;
END; $$;

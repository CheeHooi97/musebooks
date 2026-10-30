-- Repairs catalog records whose text was stored as question marks, and retires one
-- true duplicate. Written for review; NOT yet applied. Table names follow the GORM
-- models and have not been checked against the production schema: any mismatch
-- makes the script fail and roll back with no change.
--
-- Sources (checked 31 October 2026):
--   Google Play id=GPGZEQAAQBAJ: 《芷為你而閃亮-蕭芷渲數位寫真書》, 蕭芷渲, 滾石移動, August 2022
--   Ruten item 22640770348621: 《盛夏 •謝艾娜》寫真書 (seller listing; no publisher stated)
--   Wrongly merged person "???": the two books feature different people.
--
-- Run: sudo -u postgres psql -d musebooks -v ON_ERROR_STOP=1 -f data-repair-2026-10-31.sql
-- Then trigger the catalog-updated deploy so pages are rebuilt.
BEGIN;

UPDATE works SET original_title = '芷為你而閃亮-蕭芷渲數位寫真書', featured_names = '蕭芷渲',
  summary = '蕭芷渲的寫真作品；各版本內容以版次資料為準。', updated_at = now()
WHERE slug = 'work-tw-0ce0baf59439bac3fc2e1fab' AND original_title LIKE '%??%';

UPDATE works SET original_title = '盛夏・謝艾娜', featured_names = '謝艾娜',
  summary = '謝艾娜的寫真作品；各版本內容以版次資料為準。', updated_at = now()
WHERE slug = 'work-tw-fc7889583bc8a0b216c21b83' AND original_title LIKE '%??%';

UPDATE editions SET edition_label = '數位版', publisher = '滾石移動', updated_at = now(),
  publisher_company_id = (SELECT id FROM companies WHERE slug = 'publisher-a2a088a021c8f0cfef48be65eee51bc451da7f9e32ada2f7d99146002c13ffd2' LIMIT 1)
WHERE id = 'edition-5871149dac6f4129287d7149' AND edition_label LIKE '%??%';

UPDATE editions SET edition_label = '精裝版', updated_at = now()
WHERE id = 'edition-09a8c75456f5ca86a2d805a8' AND edition_label LIKE '%??%';

-- Move each book from the shared "???" person to the existing correct person.
UPDATE work_people SET credited_name = '蕭芷渲', updated_at = now(),
  person_id = (SELECT id FROM people WHERE slug = 'model-061d740bbc251e905143be47d966b1c187b24b25fa6561d1f4414abdf1870def')
WHERE work_id = (SELECT id FROM works WHERE slug = 'work-tw-0ce0baf59439bac3fc2e1fab')
  AND person_id = (SELECT id FROM people WHERE slug = 'model-a03b221c6c6eae7122ca51695d456d5222e524889136394944b2f9763b483615');

UPDATE work_people SET credited_name = '謝艾娜', updated_at = now(),
  person_id = (SELECT id FROM people WHERE slug = 'model-ea8c48da10027655a41dab74eec06e1b82314ad1a6bea6d1a413878879c34327')
WHERE work_id = (SELECT id FROM works WHERE slug = 'work-tw-fc7889583bc8a0b216c21b83')
  AND person_id = (SELECT id FROM people WHERE slug = 'model-a03b221c6c6eae7122ca51695d456d5222e524889136394944b2f9763b483615');

-- Remove the empty damaged person and publisher only when nothing references them.
DELETE FROM people p WHERE p.slug = 'model-a03b221c6c6eae7122ca51695d456d5222e524889136394944b2f9763b483615'
  AND NOT EXISTS (SELECT 1 FROM work_people c WHERE c.person_id = p.id);
DELETE FROM companies c WHERE c.slug = 'publisher-5d04c6a96439100ad3cb4672ef2fdc219dae8aaa655c9a3095c9e7ad25f4d96c'
  AND NOT EXISTS (SELECT 1 FROM editions e WHERE e.publisher_company_id = c.id);

-- True duplicate: same title and date (Shueisha, 2023-04-24). Keep the record with
-- a cover and listing, add the second credited person, retire the other.
INSERT INTO work_people (work_id, person_id, role, credited_name, credit_source, created_at, updated_at)
SELECT w.id, c.person_id, 'featured', c.credited_name, c.credit_source, now(), now()
FROM works w
JOIN work_people c ON c.work_id = (SELECT id FROM works WHERE slug = 'korea-pyo-eunji-icha-icha-joshikai-2023') AND c.role = 'featured'
WHERE w.slug = 'work-jp-77adbceb787e2e859f900905'
ON CONFLICT DO NOTHING;
UPDATE works SET status = 'superseded', updated_at = now() WHERE slug = 'korea-pyo-eunji-icha-icha-joshikai-2023';

-- Stop here if the repair did not take effect.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM works WHERE slug IN ('work-tw-0ce0baf59439bac3fc2e1fab', 'work-tw-fc7889583bc8a0b216c21b83') AND original_title LIKE '%??%') THEN
    RAISE EXCEPTION 'titles still damaged';
  END IF;
END $$;
COMMIT;

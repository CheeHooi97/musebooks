ALTER TABLE works
    ADD CONSTRAINT works_publication_type_valid
    CHECK (publication_type IN ('photobook', 'magazine_issue'));

ALTER TABLE works
    ADD CONSTRAINT works_issue_month_matches_type
    CHECK (
        (publication_type = 'magazine_issue' AND issue_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$')
        OR (publication_type = 'photobook' AND COALESCE(issue_month, '') = '')
    );

CREATE INDEX idx_work_people_cover_model
    ON work_people(person_id, work_id)
    WHERE role = 'cover_model';

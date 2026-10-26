-- Existing catalog/admin records are not proof of email ownership.
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified boolean NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash text NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_subject text NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_code_hash text NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires_at timestamptz;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at timestamptz;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_attempts integer NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_code_hash text NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires_at timestamptz;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_sent_at timestamptz;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_attempts integer NOT NULL DEFAULT 0;
-- A duplicate legacy address must be reconciled explicitly; never silently
-- merge identities or choose an arbitrary account during sign-in.
CREATE UNIQUE INDEX IF NOT EXISTS users_auth_email_unique ON users (lower(trim(email))) WHERE trim(email) <> '';
CREATE UNIQUE INDEX IF NOT EXISTS users_google_subject_unique ON users (google_subject) WHERE google_subject <> '';
CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash varchar(64) PRIMARY KEY,
    user_id text NOT NULL,
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires_at ON auth_sessions (expires_at);

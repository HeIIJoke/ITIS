BEGIN;

INSERT INTO public.roles (name)
VALUES ('guest'), ('student'), ('teacher'), ('admin')
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS public.auth_sessions (
    id uuid PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    refresh_token_hash varchar(64) NOT NULL UNIQUE,
    expires_at timestamptz NOT NULL
);

CREATE INDEX IF NOT EXISTS auth_sessions_expiry_idx ON public.auth_sessions (expires_at);

COMMIT;

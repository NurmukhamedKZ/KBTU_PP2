-- TSIS1 Stored Procedures and Functions
-- Adapted from Practice 8 for the new schema (contacts + phones tables)
-- Plus three new server-side objects required by TSIS1 (3.4)

-- ─────────────────────────────────────────────────────────────────────────────
-- Adapted from Practice 8: upsert a single contact
-- Usage: CALL upsert_contact(1, 'Alice', '+77001112233', 'mobile');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_user_id  INTEGER,
    p_name     VARCHAR,
    p_phone    VARCHAR,
    p_type     VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    INSERT INTO contacts (user_id, name)
    VALUES (p_user_id, p_name)
    ON CONFLICT (user_id, name) DO NOTHING
    RETURNING id INTO v_contact_id;

    IF v_contact_id IS NULL THEN
        SELECT id INTO v_contact_id FROM contacts
        WHERE user_id = p_user_id AND name = p_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type)
    ON CONFLICT DO NOTHING;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- Adapted from Practice 8: bulk insert with phone validation
-- Invalid entries (bad phone format) are returned via INOUT p_invalid.
-- Usage:
--   CALL bulk_insert_contacts(
--       1,
--       ARRAY['Ali', 'Bad'],
--       ARRAY['+77001112233', 'abc'],
--       ARRAY[]::TEXT[]
--   );
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_user_id INTEGER,
    p_names   VARCHAR[],
    p_phones  VARCHAR[],
    INOUT p_invalid TEXT[] DEFAULT ARRAY[]::TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i            INTEGER;
    v_name       VARCHAR;
    v_phone      VARCHAR;
    v_contact_id INTEGER;
BEGIN
    p_invalid := ARRAY[]::TEXT[];

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name  := p_names[i];
        v_phone := p_phones[i];

        IF v_phone !~ '^\+?[0-9]{7,15}$' THEN
            p_invalid := array_append(p_invalid, v_name || ': ' || v_phone);
        ELSE
            INSERT INTO contacts (user_id, name)
            VALUES (p_user_id, v_name)
            ON CONFLICT (user_id, name) DO NOTHING
            RETURNING id INTO v_contact_id;

            IF v_contact_id IS NULL THEN
                SELECT id INTO v_contact_id FROM contacts
                WHERE user_id = p_user_id AND name = v_name;
            END IF;

            INSERT INTO phones (contact_id, phone, type)
            VALUES (v_contact_id, v_phone, 'mobile')
            ON CONFLICT DO NOTHING;
        END IF;
    END LOOP;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- Adapted from Practice 8: delete contact by name or phone
-- Usage: CALL delete_contact(1, p_name := 'Alice');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE delete_contact(
    p_user_id INTEGER,
    p_name    VARCHAR DEFAULT NULL,
    p_phone   VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM contacts
        WHERE user_id = p_user_id AND name = p_name;

    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM contacts
        WHERE user_id = p_user_id
          AND id IN (
              SELECT contact_id FROM phones WHERE phone = p_phone
          );
    END IF;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- Adapted from Practice 8: paginated contacts query
-- Usage: SELECT * FROM get_contacts_paginated(1, 1, 5);
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_user_id   INTEGER,
    p_page      INTEGER DEFAULT 1,
    p_page_size INTEGER DEFAULT 5
)
RETURNS TABLE(id INTEGER, name VARCHAR, email VARCHAR, birthday DATE) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id, c.name, c.email, c.birthday
        FROM contacts c
        WHERE c.user_id = p_user_id
        ORDER BY c.name
        LIMIT  p_page_size
        OFFSET (p_page - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql;


-- ─────────────────────────────────────────────────────────────────────────────
-- NEW (TSIS1 3.4 #1): add_phone
-- Adds a phone number to an existing contact (looked up by name).
-- Usage: CALL add_phone('Alice', '+77001112233', 'work');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- NEW (TSIS1 3.4 #2): move_to_group
-- Moves a contact to a group; creates the group if it does not exist.
-- Usage: CALL move_to_group('Alice', 'Work');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    UPDATE contacts SET group_id = v_group_id WHERE name = p_contact_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
END;
$$;


-- ─────────────────────────────────────────────────────────────────────────────
-- NEW (TSIS1 3.4 #3): search_contacts — extends Practice 8 pattern-search
-- Now searches: contact name, email, AND all phone numbers in phones table.
-- Returns: (id, name, email, phones aggregated as text)
-- Usage: SELECT * FROM search_contacts(1, 'gmail');
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION search_contacts(p_user_id INTEGER, p_pattern TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, email VARCHAR, phones TEXT) AS $$
BEGIN
    RETURN QUERY
        SELECT c.id,
               c.name,
               c.email,
               STRING_AGG(ph.phone || ' (' || COALESCE(ph.type, '?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE c.user_id = p_user_id
          AND (
              c.name  ILIKE '%' || p_pattern || '%'
           OR c.email ILIKE '%' || p_pattern || '%'
           OR EXISTS (
                  SELECT 1 FROM phones p2
                  WHERE p2.contact_id = c.id
                    AND p2.phone ILIKE '%' || p_pattern || '%'
              )
          )
        GROUP BY c.id, c.name, c.email
        ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;

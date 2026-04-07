
-- Procedure 1: Upsert a single contact
--   If the name already exists for this user → update phone
--   Otherwise → insert a new row
-- Usage: CALL upsert_contact(1, 'Aisha', '+77001112233');
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_user_id INTEGER,
    p_name    VARCHAR,
    p_phone   VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM phonebook
        WHERE user_id = p_user_id AND name = p_name
    ) THEN
        UPDATE phonebook
           SET phone = p_phone
         WHERE user_id = p_user_id AND name = p_name;
    ELSE
        INSERT INTO phonebook (user_id, name, phone)
        VALUES (p_user_id, p_name, p_phone);
    END IF;
END;
$$;


-- Procedure 2: Bulk insert contacts with phone validation
--   Loops through parallel arrays of names and phones.
--   Valid phone format: optional leading +, then 7-15 digits.
--   Valid entries are upserted; invalid entries are collected and
--   returned via the INOUT parameter p_invalid as "name: phone" strings.
-- Usage:
--   CALL bulk_insert_contacts(
--       1,
--       ARRAY['Ali', 'Bad'],
--       ARRAY['+77001112233', 'abc'],
--       ARRAY[]::TEXT[]
--   );
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_user_id INTEGER,
    p_names   VARCHAR[],
    p_phones  VARCHAR[],
    INOUT p_invalid TEXT[] DEFAULT ARRAY[]::TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i       INTEGER;
    v_name  VARCHAR;
    v_phone VARCHAR;
BEGIN
    p_invalid := ARRAY[]::TEXT[];

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name  := p_names[i];
        v_phone := p_phones[i];

        -- Validate: optional +, followed by exactly 7-15 digits, nothing else
        IF v_phone !~ '^\+?[0-9]{7,15}$' THEN
            p_invalid := array_append(p_invalid, v_name || ': ' || v_phone);
        ELSE
            IF EXISTS (
                SELECT 1 FROM phonebook
                WHERE user_id = p_user_id AND name = v_name
            ) THEN
                UPDATE phonebook
                   SET phone = v_phone
                 WHERE user_id = p_user_id AND name = v_name;
            ELSE
                INSERT INTO phonebook (user_id, name, phone)
                VALUES (p_user_id, v_name, v_phone);
            END IF;
        END IF;
    END LOOP;
END;
$$;


-- Procedure 3: Delete a contact by username OR phone number
--   Pass the value you have; the other stays NULL.
-- Usage by name:  CALL delete_contact(1, p_name := 'Aisha');
-- Usage by phone: CALL delete_contact(1, p_phone := '+77001112233');
CREATE OR REPLACE PROCEDURE delete_contact(
    p_user_id INTEGER,
    p_name    VARCHAR DEFAULT NULL,
    p_phone   VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM phonebook
        WHERE user_id = p_user_id AND name = p_name;

    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook
        WHERE user_id = p_user_id AND phone = p_phone;
    END IF;
END;
$$;

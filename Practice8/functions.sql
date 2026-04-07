-- Function 1: Search contacts by pattern (name or phone)
-- Usage: SELECT * FROM search_contacts(1, 'Ali');
CREATE OR REPLACE FUNCTION search_contacts(p_user_id INTEGER, p_pattern VARCHAR)
RETURNS TABLE(id INTEGER, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM phonebook pb
        WHERE pb.user_id = p_user_id
          AND (pb.name  ILIKE '%' || p_pattern || '%'
               OR pb.phone ILIKE '%' || p_pattern || '%')
        ORDER BY pb.name;
END;
$$ LANGUAGE plpgsql;


-- Function 2: Paginated contacts query
-- Usage: SELECT * FROM get_contacts_paginated(1, page := 1, page_size := 5);
-- Page numbering starts at 1.
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_user_id  INTEGER,
    p_page     INTEGER DEFAULT 1,
    p_page_size INTEGER DEFAULT 5
)
RETURNS TABLE(id INTEGER, name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM phonebook pb
        WHERE pb.user_id = p_user_id
        ORDER BY pb.name
        LIMIT  p_page_size
        OFFSET (p_page - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql;

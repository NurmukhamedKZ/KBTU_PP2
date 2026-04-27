"""TSIS1 — Extended PhoneBook console application."""

import csv
import json

from connect import get_connection, init_db

user_id = None  # set after login

# ── AUTH ──────────────────────────────────────────────────────────────────────

def register(email: str, password: str) -> bool:
    from argon2 import PasswordHasher
    hashed = PasswordHasher().hash(password)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed),
        )
        conn.commit()
        print(f"✅ Registered: {email}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        cur.close(); conn.close()


def login(email: str, password: str):
    from argon2 import PasswordHasher
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        if row is None:
            print("❌ Email not found")
            return None
        PasswordHasher().verify(row[1], password)
        return row[0]
    except Exception as e:
        print(f"❌ {e}")
        return None
    finally:
        cur.close(); conn.close()

# ── DISPLAY HELPERS ───────────────────────────────────────────────────────────

def _print_full(rows):
    """rows: (id, name, email, birthday, group_name, phones_str)"""
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} Phones")
    print("─" * 100)
    for cid, name, email, birthday, grp, phones in rows:
        print(
            f"{cid:<5} {str(name):<20} {str(email or ''):<25} "
            f"{str(birthday or ''):<12} {str(grp or ''):<10} {phones or ''}"
        )


def _print_search(rows):
    """rows: (id, name, email, phones_str) — from search_contacts()"""
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} Phones")
    print("─" * 80)
    for cid, name, email, phones in rows:
        print(f"{cid:<5} {str(name):<20} {str(email or ''):<25} {phones or ''}")

# ── CONTACT CRUD ──────────────────────────────────────────────────────────────

def _resolve_group(cur, group_name: str):
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def add_contact(uid: int, name: str, phone: str = None, phone_type: str = "mobile",
                email: str = None, birthday: str = None, group_name: str = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        group_id = _resolve_group(cur, group_name)

        cur.execute(
            """
            INSERT INTO contacts (user_id, name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, name) DO UPDATE
                SET email    = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
            RETURNING id
            """,
            (uid, name, email or None, birthday or None, group_id),
        )
        contact_id = cur.fetchone()[0]

        if phone:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, phone, phone_type),
            )

        conn.commit()
        print(f"✅ Saved: {name}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()


def add_phone_to_contact(contact_name: str, phone: str, phone_type: str):
    """Delegates to the add_phone stored procedure."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
        conn.commit()
        print(f"✅ Phone added to '{contact_name}'")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()


def move_contact_to_group(contact_name: str, group_name: str):
    """Delegates to the move_to_group stored procedure."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
        conn.commit()
        print(f"✅ '{contact_name}' moved to group '{group_name}'")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()


def delete_contact(uid: int, by_name: str = None, by_phone: str = None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if by_name:
            cur.execute(
                "DELETE FROM contacts WHERE user_id = %s AND name = %s",
                (uid, by_name),
            )
        elif by_phone:
            cur.execute(
                """DELETE FROM contacts
                   WHERE user_id = %s
                     AND id IN (SELECT contact_id FROM phones WHERE phone = %s)""",
                (uid, by_phone),
            )
        conn.commit()
        print("✅ Deleted")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()

# ── SEARCH & FILTER ───────────────────────────────────────────────────────────

def search_contacts(uid: int, pattern: str):
    """Extended search via DB function: name, email, all phones."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM search_contacts(%s, %s)", (uid, pattern))
        rows = cur.fetchall()
        if not rows:
            print("📭 No matches found")
            return []
        print(f"\n🔍 Results for '{pattern}':")
        _print_search(rows)
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close(); conn.close()


def filter_by_group(uid: int, group_name: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups  g ON g.id = c.group_id
            LEFT JOIN phones  p ON p.contact_id = c.id
            WHERE c.user_id = %s AND g.name ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
            """,
            (uid, group_name),
        )
        rows = cur.fetchall()
        if not rows:
            print(f"📭 No contacts in group '{group_name}'")
            return []
        print(f"\n👥 Group: {group_name}")
        _print_full(rows)
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close(); conn.close()


def search_by_email(uid: int, email_pattern: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups  g ON g.id = c.group_id
            LEFT JOIN phones  p ON p.contact_id = c.id
            WHERE c.user_id = %s AND c.email ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
            """,
            (uid, f"%{email_pattern}%"),
        )
        rows = cur.fetchall()
        if not rows:
            print(f"📭 No contacts matching email '{email_pattern}'")
            return []
        print(f"\n📧 Email search: '{email_pattern}'")
        _print_full(rows)
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close(); conn.close()


def list_contacts_sorted(uid: int, sort_by: str = "name"):
    order_map = {"name": "c.name", "birthday": "c.birthday", "date": "c.created_at"}
    order_col = order_map.get(sort_by, "c.name")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups  g ON g.id = c.group_id
            LEFT JOIN phones  p ON p.contact_id = c.id
            WHERE c.user_id = %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER BY {order_col} NULLS LAST
            """,
            (uid,),
        )
        rows = cur.fetchall()
        if not rows:
            print("📭 No contacts found")
            return []
        print(f"\n📒 All contacts (sorted by {sort_by}):")
        _print_full(rows)
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close(); conn.close()

# ── PAGINATED NAVIGATION ──────────────────────────────────────────────────────

def paginated_navigation(uid: int, page_size: int = 5):
    """Interactive page browser: next / prev / quit."""
    page = 1
    while True:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday, g.name,
                       STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
                FROM contacts c
                LEFT JOIN groups  g ON g.id = c.group_id
                LEFT JOIN phones  p ON p.contact_id = c.id
                WHERE c.user_id = %s
                GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
                ORDER BY c.name
                LIMIT %s OFFSET %s
                """,
                (uid, page_size, (page - 1) * page_size),
            )
            rows = cur.fetchall()
        finally:
            cur.close(); conn.close()

        if not rows and page == 1:
            print("📭 No contacts")
            break

        print(f"\n📒 Page {page} (size {page_size}):")
        if rows:
            _print_full(rows)
        else:
            print("  (no more contacts on this page)")

        cmd = input("  [n]ext / [p]rev / [q]uit: ").strip().lower()
        if cmd == "n":
            if rows:
                page += 1
            else:
                print("  Already at last page")
        elif cmd == "p":
            if page > 1:
                page -= 1
            else:
                print("  Already at first page")
        elif cmd == "q":
            break

# ── IMPORT / EXPORT ───────────────────────────────────────────────────────────

def export_to_json(uid: int, filepath: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday::TEXT, g.name, c.created_at::TEXT
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.user_id = %s
            ORDER BY c.name
            """,
            (uid,),
        )
        contacts_rows = cur.fetchall()

        result = []
        for cid, name, email, birthday, grp, created_at in contacts_rows:
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = %s", (cid,)
            )
            phones = [{"phone": ph, "type": tp} for ph, tp in cur.fetchall()]
            result.append(
                {
                    "name": name,
                    "email": email,
                    "birthday": birthday,
                    "group": grp,
                    "phones": phones,
                    "created_at": created_at,
                }
            )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ Exported {len(result)} contacts to '{filepath}'")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()


def import_from_json(uid: int, filepath: str):
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Cannot read file: {e}")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        for entry in data:
            name = (entry.get("name") or "").strip()
            if not name:
                continue

            cur.execute(
                "SELECT id FROM contacts WHERE user_id = %s AND name = %s",
                (uid, name),
            )
            existing = cur.fetchone()

            if existing:
                action = input(
                    f"  Contact '{name}' already exists. [s]kip or [o]verwrite? "
                ).strip().lower()
                if action != "o":
                    print(f"  ↷ Skipped '{name}'")
                    continue
                contact_id = existing[0]
                group_id = _resolve_group(cur, entry.get("group"))
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                    (entry.get("email"), entry.get("birthday"), group_id, contact_id),
                )
                cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            else:
                group_id = _resolve_group(cur, entry.get("group"))
                cur.execute(
                    """INSERT INTO contacts (user_id, name, email, birthday, group_id)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (uid, name, entry.get("email"), entry.get("birthday"), group_id),
                )
                contact_id = cur.fetchone()[0]

            for ph in entry.get("phones", []):
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, ph.get("phone"), ph.get("type")),
                )

            print(f"  ✅ Imported: {name}")

        conn.commit()
        print("✅ JSON import complete")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()


def import_from_csv(uid: int, filepath: str):
    """Extended CSV importer — supports: name, phone, phone_type, email, birthday, group."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(filepath, encoding="utf-8") as f:
            count = 0
            for row in csv.DictReader(f):
                name = (row.get("name") or "").strip()
                if not name:
                    print(f"  ⚠️  Skipping row with no name: {row}")
                    continue

                phone      = (row.get("phone")      or "").strip() or None
                phone_type = (row.get("phone_type") or "mobile").strip()
                email      = (row.get("email")      or "").strip() or None
                birthday   = (row.get("birthday")   or "").strip() or None
                group_name = (row.get("group")      or "").strip() or None

                group_id = _resolve_group(cur, group_name)

                cur.execute(
                    """
                    INSERT INTO contacts (user_id, name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, name) DO UPDATE
                        SET email    = EXCLUDED.email,
                            birthday = EXCLUDED.birthday,
                            group_id = EXCLUDED.group_id
                    RETURNING id
                    """,
                    (uid, name, email, birthday, group_id),
                )
                contact_id = cur.fetchone()[0]

                if phone:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, phone, phone_type),
                    )

                count += 1

        conn.commit()
        print(f"✅ Imported {count} contacts from CSV")
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close(); conn.close()

# ── MENU ──────────────────────────────────────────────────────────────────────

MENU = """
───────────────────────────────────────────
 1 : Add / update contact
 2 : Add phone to existing contact
 3 : Move contact to group
 4 : Search contacts (name / email / phone)
 5 : Filter by group
 6 : Search by email
 7 : List all contacts (sorted)
 8 : Browse contacts (paginated)
 9 : Delete contact
10 : Import from CSV
11 : Import from JSON
12 : Export to JSON
13 : Exit
───────────────────────────────────────────"""


if __name__ == "__main__":
    init_db()

    # ── Auth loop ────────────────────────────────────────────────────────────
    while True:
        action = input("Register or Login (r/l): ").strip().lower()
        if action == "r":
            email    = input("Email: ").strip()
            password = input("Password: ").strip()
            register(email, password)
        elif action == "l":
            email    = input("Email: ").strip()
            password = input("Password: ").strip()
            user_id  = login(email, password)
            if user_id:
                print(f"✅ Welcome, {email}")
                break
            print("❌ Incorrect credentials, try again")
        else:
            print("Enter  r  or  l")

    # ── Main loop ────────────────────────────────────────────────────────────
    while True:
        print(MENU)
        choice = input("Choice: ").strip()

        if choice == "1":
            name  = input("Name: ").strip()
            phone = input("Phone (blank to skip): ").strip() or None
            ptype = "mobile"
            if phone:
                ptype = input("Phone type (home/work/mobile) [mobile]: ").strip() or "mobile"
            email    = input("Email (blank to skip): ").strip() or None
            birthday = input("Birthday YYYY-MM-DD (blank to skip): ").strip() or None
            print("Available groups: Family / Work / Friend / Other")
            group = input("Group (blank to skip): ").strip() or None
            add_contact(user_id, name, phone, ptype, email, birthday, group)

        elif choice == "2":
            name  = input("Contact name: ").strip()
            phone = input("Phone: ").strip()
            ptype = input("Phone type (home/work/mobile) [mobile]: ").strip() or "mobile"
            add_phone_to_contact(name, phone, ptype)

        elif choice == "3":
            name  = input("Contact name: ").strip()
            group = input("Group name: ").strip()
            move_contact_to_group(name, group)

        elif choice == "4":
            pattern = input("Search pattern (name / email / phone): ").strip()
            search_contacts(user_id, pattern)

        elif choice == "5":
            print("Available groups: Family / Work / Friend / Other")
            group = input("Group name: ").strip()
            filter_by_group(user_id, group)

        elif choice == "6":
            pattern = input("Email pattern: ").strip()
            search_by_email(user_id, pattern)

        elif choice == "7":
            print("Sort by: name / birthday / date")
            sort = input("Sort by [name]: ").strip() or "name"
            list_contacts_sorted(user_id, sort)

        elif choice == "8":
            try:
                size = int(input("Page size [5]: ").strip() or "5")
            except ValueError:
                size = 5
            paginated_navigation(user_id, size)

        elif choice == "9":
            by = input("Delete by (n)ame or (p)hone? ").strip().lower()
            if by == "n":
                name = input("Name: ").strip()
                delete_contact(user_id, by_name=name)
            elif by == "p":
                phone = input("Phone: ").strip()
                delete_contact(user_id, by_phone=phone)
            else:
                print("Enter  n  or  p")

        elif choice == "10":
            path = input("CSV file path: ").strip()
            import_from_csv(user_id, path)

        elif choice == "11":
            path = input("JSON file path: ").strip()
            import_from_json(user_id, path)

        elif choice == "12":
            path = input("Export path [contacts.json]: ").strip() or "contacts.json"
            export_to_json(user_id, path)

        elif choice == "13":
            print("Bye!")
            break

        else:
            print("Please enter a number 1–13")

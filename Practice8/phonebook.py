from argon2 import PasswordHasher
import csv

from connect import get_connection

user_id = None

# ── AUTH ──────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return PasswordHasher().hash(password)

def register(email: str, password: str) -> bool:
    hashed = hash_password(password)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed)
        )
        conn.commit()
        print(f"✅ Registered: {email}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def login(email: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, password FROM users WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if row is None:
            print("❌ Email not found")
            return None
        PasswordHasher().verify(row[1], password)
        return row[0]
    except Exception as e:
        print(e)
        return None
    finally:
        cur.close()
        conn.close()

# ── PHONEBOOK — calls DB functions / procedures ───────────────────────────────

def upsert_contact(user_id: int, name: str, phone: str):
    """Insert or update a contact via the upsert_contact procedure."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL upsert_contact(%s, %s, %s)", (user_id, name, phone))
        conn.commit()
        print(f"✅ Saved contact: {name} — {phone}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def bulk_insert_contacts(user_id: int, names: list, phones: list):
    """
    Insert many contacts via the bulk_insert_contacts procedure.
    Prints which entries had invalid phone numbers.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "CALL bulk_insert_contacts(%s, %s, %s, %s)",
            (user_id, names, phones, [])
        )
        # The procedure returns its INOUT parameter as the only result column
        result = cur.fetchone()
        conn.commit()

        invalid = result[0] if result else []
        if invalid:
            print(f"⚠️  Invalid entries ({len(invalid)}):")
            for entry in invalid:
                print(f"   • {entry}")
        else:
            print("✅ All entries inserted successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def search_contacts(user_id: int, pattern: str):
    """Search contacts by partial name or phone using the DB function."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM search_contacts(%s, %s)",
            (user_id, pattern)
        )
        rows = cur.fetchall()
        if not rows:
            print("📭 No matches found")
            return []
        print(f"\n🔍 Results for '{pattern}':")
        print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")
        print("-" * 40)
        for row_id, name, phone in rows:
            print(f"{row_id:<5} {name:<20} {phone:<15}")
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def get_contacts_paginated(user_id: int, page: int = 1, page_size: int = 5):
    """Retrieve contacts page by page using the DB function."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s, %s)",
            (user_id, page, page_size)
        )
        rows = cur.fetchall()
        if not rows:
            print("📭 No contacts on this page")
            return []
        print(f"\n📒 Page {page} (size {page_size}):")
        print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")
        print("-" * 40)
        for row_id, name, phone in rows:
            print(f"{row_id:<5} {name:<20} {phone:<15}")
        return rows
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def delete_contact(user_id: int, by_name: str = None, by_phone: str = None):
    """Delete a contact by name or phone via the delete_contact procedure."""
    if not by_name and not by_phone:
        print("❌ Provide a name or phone to delete")
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "CALL delete_contact(%s, %s, %s)",
            (user_id, by_name, by_phone)
        )
        conn.commit()
        label = by_name or by_phone
        print(f"✅ Deleted contact: {label}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def import_from_csv(user_id: int, filepath: str):
    """Read a CSV file and bulk-insert via the DB procedure."""
    names, phones = [], []
    try:
        with open(filepath, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                name  = row.get('name',  '').strip()
                phone = row.get('phone', '').strip()
                if name and phone:
                    names.append(name)
                    phones.append(phone)
                else:
                    print(f"⚠️  Skipping incomplete row: {row}")
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return

    if names:
        bulk_insert_contacts(user_id, names, phones)

# ── MENU ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Login / register
    while True:
        r_l = input("Register or Login (r/l): ").lower()
        if r_l == "r":
            email    = input("Email: ")
            password = input("Password: ")
            if register(email, password):
                print("Registered. Now login.")
        elif r_l == "l":
            email    = input("Email: ")
            password = input("Password: ")
            user_id  = login(email, password)
            if user_id is None:
                print("❌ Incorrect, try again")
            else:
                print(f"✅ Welcome, {email}")
                break
        else:
            print("Enter r or l")

    # Main menu
    while True:
        choice = input(
            "\n───────────────────────────────────\n"
            "1: Add / update contact (upsert)\n"
            "2: Bulk insert from list\n"
            "3: Import from CSV\n"
            "4: Search contacts\n"
            "5: View contacts (paginated)\n"
            "6: Delete contact\n"
            "7: Exit\n"
            "───────────────────────────────────\n"
            "Choice: "
        )

        if choice == "1":
            name  = input("Name: ")
            phone = input("Phone: ")
            upsert_contact(user_id, name, phone)

        elif choice == "2":
            print("Enter contacts one per line as  name,phone  (blank line to finish):")
            names, phones = [], []
            while True:
                line = input("  > ").strip()
                if not line:
                    break
                parts = line.split(",", 1)
                if len(parts) == 2:
                    names.append(parts[0].strip())
                    phones.append(parts[1].strip())
                else:
                    print("  ⚠️  Format: name,phone")
            if names:
                bulk_insert_contacts(user_id, names, phones)

        elif choice == "3":
            filepath = input("CSV file path: ")
            import_from_csv(user_id, filepath)

        elif choice == "4":
            pattern = input("Search (name or phone): ")
            search_contacts(user_id, pattern)

        elif choice == "5":
            try:
                page      = int(input("Page number (default 1): ") or 1)
                page_size = int(input("Page size  (default 5): ") or 5)
            except ValueError:
                page, page_size = 1, 5
            get_contacts_paginated(user_id, page, page_size)

        elif choice == "6":
            sub = input("Delete by (n)ame or (p)hone? ").lower()
            if sub == "n":
                name = input("Name: ")
                delete_contact(user_id, by_name=name)
            elif sub == "p":
                phone = input("Phone: ")
                delete_contact(user_id, by_phone=phone)
            else:
                print("Enter n or p")

        elif choice == "7":
            print("Bye!")
            break
        else:
            print("Enter a number 1-7")

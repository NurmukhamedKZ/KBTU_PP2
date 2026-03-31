from argon2 import PasswordHasher
import csv

from connect import get_connection

user_id = None

# USER Functions
def hash_password(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)

def check_password(password_from_db: str,password: str) -> bool:
    ph = PasswordHasher()
    return ph.verify(password_from_db, password)

def register(email: str, password: str) -> bool:
    """Add a new user to the DB"""
    hashed = hash_password(password)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (email, password)
            VALUES (%s, %s)
        """, (email, hashed))
        conn.commit()
        print(f"✅ Added new user: {email}\nPassword hash: {hashed}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        return False

    finally:
        cur.close()
        conn.close()

def login(email: str, password: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, password FROM users
            WHERE email = %s
        """, (email,))  # comma makes it a tuple, required by psycopg2
        
        row = cur.fetchone()  # returns one row or None
        
        if row is None:
            print("❌ Email not found")
            return None
        
        user_id = row[0]
        hashed = row[1]
        
        ph = PasswordHasher()
        ph.verify(hashed, password)  # raises exception if wrong
        return user_id
        
    except Exception as e:
        print(e)
        return None
    finally:
        cur.close()
        conn.close()

# PHONEBOOK Functions
def add_new_phone(user_id: int, name: str, phone: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO phonebook (user_id, name, phone)
            VALUES (%s, %s, %s)""",
            (user_id, name, phone))
        conn.commit()
        print(f"✅ Added contact: {name} — {phone}")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")

    finally:
        cur.close()
        conn.close()

def get_all_phones(user_id: int) -> list:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, phone FROM phonebook
            WHERE user_id = %s""",
            (user_id,))

        rows = cur.fetchall()
        # rows = [("Aisha", "Bekova", "+77009876543"), ("Damir", None, "+77771112233")]

        if not rows:
            print("📭 No contacts found")
            return []

        print(f"\n📒 Phonebook for user {user_id}:")
        print(f"{"ID":<3} {'Name':<20} {'Phone':<15}")
        print("-" * 35)
        for id, name, phone in rows:
            print(f"{id:<3} {name:<20} {phone:<15}")

        return rows
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def update_phone_by_name(user_id: int, name: str, new_phone: str):
    """Find contact by name, update their phone number"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE phonebook
            SET phone = %s
            WHERE user_id = %s AND name = %s
        """, (new_phone, user_id, name))
        conn.commit()

        if cur.rowcount == 0:  # no rows were updated
            print(f"❌ Contact '{name}' not found")
        else:
            print(f"✅ Updated phone for {name} → {new_phone}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def update_name_by_phone(user_id: int, phone: str, new_name: str):
    """Find contact by phone, update their name"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE phonebook
            SET name = %s
            WHERE user_id = %s AND phone = %s
        """, (new_name, user_id, phone))
        conn.commit()

        if cur.rowcount == 0:
            print(f"❌ Phone '{phone}' not found")
        else:
            print(f"✅ Updated name for {phone} → {new_name}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def update_phone_name_by_id(user_id: int, contact_id: int, new_name: str, new_phone: str):
    """Find contact by its own id, update both name and phone"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE phonebook
            SET name = %s, phone = %s
            WHERE user_id = %s AND id = %s
        """, (new_name, new_phone, user_id, contact_id))
        conn.commit()

        if cur.rowcount == 0:
            print(f"❌ Contact with id '{contact_id}' not found")
        else:
            print(f"✅ Updated contact {contact_id} → {new_name}, {new_phone}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

def delete_phone(user_id: int, contact_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM phonebook
            WHERE user_id = %s AND id = %s
        """, (user_id, contact_id))
        
        conn.commit()
       
        if cur.rowcount == 0:
            print(f"❌ Contact with id '{contact_id}' not found")
        else:
            print(f"✅ Contact {contact_id} deleted")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()


def import_from_csv(user_id: int, filepath: str):
    """Import contacts from a CSV file into the phonebook."""
    conn = get_connection()
    cur = conn.cursor()
    
    added = 0
    skipped = 0
    
    try:
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)  # expects columns: name, phone
            
            for row in reader:
                name = row.get('name', '').strip()
                phone = row.get('phone', '').strip()

                print(name)
                print(phone)
                
                if not name or not phone:
                    print(f"⚠️  Skipping incomplete row: {row}")
                    skipped += 1
                    continue
                
                try:
                    cur.execute("""
                        INSERT INTO phonebook (user_id, name, phone)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, phone) DO NOTHING
                    """, (user_id, name, phone))
                    
                    if cur.rowcount == 1:
                        added += 1
                    else:
                        print(f"⚠️  Duplicate skipped: {name} — {phone}")
                        skipped += 1
                        
                except Exception as e:
                    print(f"❌ Error on row {row}: {e}")
                    skipped += 1
        
        conn.commit()
        print(f"✅ Import done: {added} added, {skipped} skipped")
        
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Import failed: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("Hello!")
    while True:
        r_l = input("Register or Login (r/l): ").lower()
        if r_l == "r":
            email = input("Email: ")
            password = input("Password: ")
            status = register(email, password)
            if status:
                print("Registered succesfully, now Login to the accound")
            else:
                print("❌ Try again")
        elif r_l == "l":
            email = input("Email: ")
            password = input("Password: ")
            user_id = login(email, password)
            if user_id is None:
                print("❌ Incorrect, Try again")
            else:
                print(f"✅ Welcome, {email}")
                break
        else:
            print("Only r or l")
        
    print(f"USER_ID: {user_id}")
    
    while True:
        user_input = input(
            "\n-----------------------------------\n"
            "1: add phone\n"
            "2: update phone\n"
            "3: get all phones\n"
            "4: delete phone\n"
            "5: exit\n"
            "-----------------------------------\n"
            "Choise: "
        )
        try:
            user_choice = int(user_input)
        except:
            print("Enter a number")
            continue

        if user_choice == 1:
            sub = input("1: manual entry\n2: import from CSV\nChoice: ")
    
            if sub == '1':
                name = input("Name: ")
                phone = input("Phone: ")
                add_new_phone(user_id, name, phone)
            
            elif sub == '2':
                filepath = input("CSV file path (e.g. contacts.csv): ")
                import_from_csv(user_id, filepath)

        elif user_choice == 2:
            update_choise = input(
                "1: update phone by name\n"
                "2: update name by phone\n"
                "3: update both by contact id\n"
                "Choise: ")
            try:
                user_choice = int(update_choise)
            except:
                print("Enter a number")
                continue
            
            if user_choice == 1:
                name = input("Name to find: ")
                new_phone = input("New phone: ")
                update_phone_by_name(user_id, name, new_phone)
            elif user_choice == 2:
                phone = input("Phone to find: ")
                new_name = input("New name: ")
                update_name_by_phone(user_id, phone, new_name)
            elif user_choice == 3:
                contact_id = int(input("Contact ID: "))
                new_name = input("New name: ")
                new_phone = input("New phone: ")
                update_phone_name_by_id(user_id, contact_id, new_name, new_phone)
            else:
                print("Input a number [1, 2, 3]!")

        elif user_choice == 3:
            get_all_phones(user_id)

        elif user_choice == 4:
            contact_id = int(input("Contact ID:"))
            delete_phone(user_id, contact_id)

        elif user_choice == 5:
            print("Bye")
            break
        
        
            
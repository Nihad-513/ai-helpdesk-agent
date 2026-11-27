
"""Database operations for the Bean & Brew AI Helpdesk."""

import sqlite3
from pathlib import Path
import uuid
import bcrypt
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(
           os.getenv("BEAN_BREW_DB_PATH", Path(__file__).parent / "bean_brew.db")
)


@contextmanager
def get_connection():
    """Create, manage, and close a database connection."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()



def init_db():
    """Create tables and safely migrate the existing database."""

    with get_connection() as connection:

        # Customer accounts
        connection.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Staff accounts: administrators and support agents
        connection.execute("""
            CREATE TABLE IF NOT EXISTS staff_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('admin', 'agent')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Conversations
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
                    ON DELETE SET NULL
            )
        """)

        # Chat messages
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

        # Support tickets
        connection.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                customer_id INTEGER,
                issue TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
                    ON DELETE SET NULL
            )
        """)

        # Migrate conversation columns
        conversation_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        }

        if "customer_id" not in conversation_columns:
            connection.execute("""
                ALTER TABLE conversations
                ADD COLUMN customer_id INTEGER
                REFERENCES customers(id) ON DELETE SET NULL
            """)

        # Migrate support ticket columns
        ticket_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(support_tickets)"
            ).fetchall()
        }

        if "customer_id" not in ticket_columns:
            connection.execute("""
                ALTER TABLE support_tickets
                ADD COLUMN customer_id INTEGER
                REFERENCES customers(id) ON DELETE SET NULL
            """)

        if "priority" not in ticket_columns:
            connection.execute("""
                ALTER TABLE support_tickets
                ADD COLUMN priority TEXT NOT NULL DEFAULT 'Normal'
            """)

        if "is_escalated" not in ticket_columns:
            connection.execute("""
                ALTER TABLE support_tickets
                ADD COLUMN is_escalated INTEGER NOT NULL DEFAULT 0
            """)

        if "resolution_notes" not in ticket_columns:
            connection.execute("""
                ALTER TABLE support_tickets
                ADD COLUMN resolution_notes TEXT
            """)

        if "assigned_agent_id" not in ticket_columns:
            connection.execute("""
                ALTER TABLE support_tickets
                ADD COLUMN assigned_agent_id INTEGER
                REFERENCES staff_accounts(id) ON DELETE SET NULL
            """)

        # Ticket replies
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_pk INTEGER NOT NULL,
                sender_role TEXT NOT NULL
                    CHECK (sender_role IN ('customer', 'agent')),
                sender_id INTEGER,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_pk)
                    REFERENCES support_tickets(id)
                    ON DELETE CASCADE
            )
        """)

        # Indexes
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_customer
            ON support_tickets(customer_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_customer
            ON conversations(customer_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticket_replies_ticket
            ON ticket_replies(ticket_pk)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_assigned_agent
            ON support_tickets(assigned_agent_id)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_staff_email
            ON staff_accounts(email)
        """)

    print("Database initialized successfully.")





def create_conversation(
    session_id: str,
    customer_id: int | None = None,
) -> int:
    """Create a conversation, optionally linked to a customer."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO conversations (session_id, customer_id)
            VALUES (?, ?)
            """,
            (session_id, customer_id),
        )

        return cursor.lastrowid



def save_message(
    conversation_id: int,
    role: str,
    content: str,
) -> None:
    """Save a message to a conversation."""

    if role not in ("user", "assistant"):
        raise ValueError("Role must be 'user' or 'assistant'")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )


def get_conversation_history(session_id: str) -> list[dict]:
    """Retrieve all messages belonging to a conversation."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT messages.role, messages.content, messages.created_at
            FROM messages
            JOIN conversations
                ON messages.conversation_id = conversations.id
            WHERE conversations.session_id = ?
            ORDER BY messages.id ASC
            """,
            (session_id,),
        ).fetchall()

        return [dict(row) for row in rows]

def get_customer_conversations(customer_id: int) -> list[dict]:
    """Retrieve all conversations belonging to a customer."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                conversations.id,
                conversations.session_id,
                conversations.created_at,
                COUNT(messages.id) AS message_count,
                (
                    SELECT content
                    FROM messages
                    WHERE messages.conversation_id = conversations.id
                      AND messages.role = 'user'
                    ORDER BY messages.id ASC
                    LIMIT 1
                ) AS first_message
            FROM conversations
            LEFT JOIN messages
                ON conversations.id = messages.conversation_id
            WHERE conversations.customer_id = ?
            GROUP BY conversations.id
            HAVING COUNT(messages.id) > 0
            ORDER BY conversations.id DESC
            """,
            (customer_id,),
        ).fetchall()

        return [dict(row) for row in rows]

def get_conversation_by_id(
    conversation_id: int,
    customer_id: int,
) -> dict | None:
    """Retrieve a conversation belonging to a specific customer."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, session_id, created_at
            FROM conversations
            WHERE id = ? AND customer_id = ?
            """,
            (conversation_id, customer_id),
        ).fetchone()

        return dict(row) if row else None



def create_support_ticket(
    issue: str,
    customer_name: str | None = None,
    customer_email: str | None = None,
) -> str:
    """Create a support ticket and return its unique ticket ID."""

    ticket_id = f"BB-{uuid.uuid4().hex[:8].upper()}"

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO support_tickets (
                ticket_id,
                customer_name,
                customer_email,
                issue
            )
            VALUES (?, ?, ?, ?)
            """,
            (ticket_id, customer_name, customer_email, issue),
        )

    return ticket_id


def create_customer_ticket(
    customer_id: int,
    issue: str,
) -> str:
    """Create a support ticket linked to a registered customer."""

    with get_connection() as connection:
        customer = connection.execute(
            """
            SELECT name, email
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        ).fetchone()

        if not customer:
            raise ValueError("Customer account not found.")

        ticket_id = f"BB-{uuid.uuid4().hex[:8].upper()}"

        connection.execute(
            """
            INSERT INTO support_tickets (
                ticket_id,
                customer_name,
                customer_email,
                customer_id,
                issue,
                is_escalated
            )
            VALUES (?, ?, ?, ?, ?,?)
            """,
            (
                ticket_id,
                customer["name"],
                customer["email"],
                customer_id,
                issue,
                1
            ),
        )

        return ticket_id



def get_support_ticket(ticket_id: str) -> dict | None:
    """Retrieve a support ticket using its ticket ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM support_tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

        return dict(row) if row else None


def get_customer_tickets(customer_id: int) -> list[dict]:
    """Retrieve all support tickets belonging to a customer."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT ticket_id, issue, status, created_at
            FROM support_tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
            """,
            (customer_id,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_all_tickets() -> list[dict]:
    """Retrieve all support tickets for the staff dashboard."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                t.id,
                t.ticket_id,
                t.customer_name,
                t.customer_email,
                t.issue,
                t.status,
                t.priority,
                t.is_escalated,
                t.assigned_agent_id,
                s.name AS assigned_agent_name,
                t.resolution_notes,
                t.created_at
            FROM support_tickets AS t
            LEFT JOIN staff_accounts AS s
                ON t.assigned_agent_id = s.id
            ORDER BY
                CASE
                    WHEN t.is_escalated = 1 THEN 0
                    ELSE 1
                END,
                t.created_at DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]





def update_ticket_status(ticket_id: str, status: str) -> bool:
    """Update a support ticket's status."""

    allowed_statuses = ("Open", "In Progress", "Resolved")

    if status not in allowed_statuses:
        raise ValueError(
            f"Status must be one of: {', '.join(allowed_statuses)}"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET status = ?
            WHERE ticket_id = ?
            """,
            (status, ticket_id),
        )

        return cursor.rowcount > 0

def update_agent_ticket_status(
    ticket_id: str,
    agent_id: int,
    new_status: str,
) -> bool:
    """Allow an assigned agent to progress or resolve their ticket."""

    allowed_statuses = ("In Progress", "Resolved")

    if new_status not in allowed_statuses:
        raise ValueError(
            "Agents can only set tickets to In Progress or Resolved."
        )

    with get_connection() as connection:
        ticket = connection.execute(
            """
            SELECT status
            FROM support_tickets
            WHERE ticket_id = ?
            AND assigned_agent_id = ?
            """,
            (ticket_id, agent_id),
        ).fetchone()

        if not ticket:
            raise PermissionError(
                "This ticket is not assigned to you."
            )

        if ticket["status"] == "Resolved":
            raise ValueError(
                "Resolved tickets can only be reopened by an admin."
            )

        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET status = ?
            WHERE ticket_id = ?
            AND assigned_agent_id = ?
            """,
            (new_status, ticket_id, agent_id),
        )

        return cursor.rowcount > 0


def update_ticket_priority(ticket_id: str, priority: str) -> bool:
    """Update the priority of a support ticket."""

    allowed_priorities = ("Normal", "High", "Urgent")

    if priority not in allowed_priorities:
        raise ValueError(
            f"Priority must be one of: {', '.join(allowed_priorities)}"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET priority = ?
            WHERE ticket_id = ?
            """,
            (priority, ticket_id),
        )

        return cursor.rowcount > 0

def update_ticket_escalation(ticket_id: str, is_escalated: bool) -> bool:
    """Update the escalation status of a support ticket."""

    if not isinstance(is_escalated, bool):
        raise ValueError("Escalation status must be True or False.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET is_escalated = ?
            WHERE ticket_id = ?
            """,
            (int(is_escalated), ticket_id),
        )

        return cursor.rowcount > 0


def update_ticket_resolution_notes(ticket_id: str, notes: str) -> bool:
    """Save resolution notes for a support ticket."""

    notes = notes.strip()

    if not notes:
        raise ValueError("Resolution notes cannot be empty.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET resolution_notes = ?
            WHERE ticket_id = ?
            """,
            (notes, ticket_id),
        )

        return cursor.rowcount > 0



def get_active_agents() -> list[dict]:
    """Retrieve all active support agents."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, email
            FROM staff_accounts
            WHERE role = 'agent'
            AND is_active = 1
            ORDER BY name
            """
        ).fetchall()

        return [dict(row) for row in rows]


def assign_ticket_to_agent(ticket_id: str, agent_id: int) -> bool:
    """Assign a support ticket to an active support agent."""

    with get_connection() as connection:
        agent = connection.execute(
            """
            SELECT id
            FROM staff_accounts
            WHERE id = ?
            AND role = 'agent'
            AND is_active = 1
            """,
            (agent_id,),
        ).fetchone()

        if not agent:
            raise ValueError("Active support agent not found.")

        cursor = connection.execute(
            """
            UPDATE support_tickets
            SET assigned_agent_id = ?
            WHERE ticket_id = ?
            """,
            (agent_id, ticket_id),
        )

        return cursor.rowcount > 0



def register_customer(
    name: str,
    email: str,
    password: str,
) -> int:
    """Register a customer and return their database ID."""

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        raise ValueError("Name, email and password are required.")

    if "@" not in email:
        raise ValueError("Please enter a valid email address.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must not exceed 72 bytes.")

    password_hash = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO customers (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name, email, password_hash),
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists.")


def authenticate_customer(
    email: str,
    password: str,
) -> dict | None:
    """Authenticate a customer and return their public details."""

    email = email.strip().lower()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, password_hash
            FROM customers
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if not row:
        return None

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        row["password_hash"].encode("utf-8"),
    ):
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
    }
def get_agent_tickets(agent_id: int) -> list[dict]:
    """Retrieve tickets assigned to a specific support agent."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                t.ticket_id,
                t.customer_name,
                t.customer_email,
                t.issue,
                t.status,
                t.priority,
                t.is_escalated,
                t.resolution_notes,
                t.created_at,
                s.name AS assigned_agent_name
            FROM support_tickets AS t
            LEFT JOIN staff_accounts AS s
                ON t.assigned_agent_id = s.id
            WHERE t.assigned_agent_id = ?
            ORDER BY
                CASE
                    WHEN t.is_escalated = 1 THEN 0
                    ELSE 1
                END,
                t.created_at DESC
            """,
            (agent_id,),
        ).fetchall()

        return [dict(row) for row in rows]


def get_ticket_replies(ticket_id: str) -> list[dict]:
    """Retrieve all replies for a support ticket."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                tr.sender_role,
                tr.sender_id,
                tr.message,
                tr.created_at,
                CASE
                    WHEN tr.sender_role = 'agent'
                    THEN s.name
                    ELSE c.name
                END AS sender_name
            FROM ticket_replies AS tr
            JOIN support_tickets AS t
                ON tr.ticket_pk = t.id
            LEFT JOIN staff_accounts AS s
                ON tr.sender_role = 'agent'
                AND tr.sender_id = s.id
            LEFT JOIN customers AS c
                ON tr.sender_role = 'customer'
                AND tr.sender_id = c.id
            WHERE t.ticket_id = ?
            ORDER BY tr.created_at ASC, tr.id ASC
            """,
            (ticket_id,),
        ).fetchall()

        return [dict(row) for row in rows]

def get_customer_ticket_replies(
    ticket_id: str,
    customer_id: int,
) -> list[dict]:
    """Retrieve replies only if the ticket belongs to the customer."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                tr.sender_role,
                tr.sender_id,
                tr.message,
                tr.created_at,
                CASE
                    WHEN tr.sender_role = 'agent'
                    THEN s.name
                    ELSE c.name
                END AS sender_name
            FROM ticket_replies AS tr
            JOIN support_tickets AS t
                ON tr.ticket_pk = t.id
            LEFT JOIN staff_accounts AS s
                ON tr.sender_role = 'agent'
                AND tr.sender_id = s.id
            LEFT JOIN customers AS c
                ON tr.sender_role = 'customer'
                AND tr.sender_id = c.id
            WHERE t.ticket_id = ?
            AND t.customer_id = ?
            ORDER BY tr.created_at ASC, tr.id ASC
            """,
            (ticket_id, customer_id),
        ).fetchall()

        return [dict(row) for row in rows]



def add_ticket_reply(
    ticket_id: str,
    sender_role: str,
    sender_id: int,
    message: str,
) -> bool:
    """Add a reply after verifying the sender's permission."""

    message = message.strip()

    if not message:
        raise ValueError("Reply cannot be empty.")

    if sender_role not in ("customer", "agent"):
        raise ValueError("Invalid sender role.")

    with get_connection() as connection:
        ticket = connection.execute(
            """
            SELECT id, customer_id, assigned_agent_id
            FROM support_tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

        if not ticket:
            raise ValueError("Ticket not found.")

        if sender_role == "customer":
            if ticket["customer_id"] != sender_id:
                raise PermissionError("You cannot reply to this ticket.")

        elif sender_role == "agent":
            if ticket["assigned_agent_id"] != sender_id:
                raise PermissionError(
                    "You can only reply to tickets assigned to you."
                )

        connection.execute(
            """
            INSERT INTO ticket_replies (
                ticket_pk,
                sender_role,
                sender_id,
                message
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket["id"],
                sender_role,
                sender_id,
                message,
            ),
        )

        return True



def get_customer_by_email(email: str) -> dict | None:
    """Retrieve customer details without exposing their password hash."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, email, created_at
            FROM customers
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

        return dict(row) if row else None


def create_staff_account(
    name: str,
    email: str,
    password: str,
    role: str,
) -> int:
    """Create an administrator or support agent account."""

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        raise ValueError("All fields are required.")

    if "@" not in email:
        raise ValueError("Enter a valid email address.")

    if role not in ("admin", "agent"):
        raise ValueError("Role must be admin or agent.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes.")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO staff_accounts (
                    name, email, password_hash, role
                )
                VALUES (?, ?, ?, ?)
                """,
                (name, email, password_hash, role),
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("A staff account with this email already exists.")


def authenticate_staff(email: str, password: str) -> dict | None:
    """Authenticate an active administrator or support agent."""

    email = email.strip().lower()

    with get_connection() as connection:
        staff = connection.execute(
            """
            SELECT id, name, email, password_hash, role, is_active
            FROM staff_accounts
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if not staff or not staff["is_active"]:
        return None

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        staff["password_hash"].encode("utf-8"),
    ):
        return None

    return {
        "id": staff["id"],
        "name": staff["name"],
        "email": staff["email"],
        "role": staff["role"],
    }


def get_staff_by_email(email: str) -> dict | None:
    """Retrieve public staff account details."""

    with get_connection() as connection:
        staff = connection.execute(
            """
            SELECT id, name, email, role, is_active, created_at
            FROM staff_accounts
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

        return dict(staff) if staff else None


if __name__ == "__main__":
    init_db()

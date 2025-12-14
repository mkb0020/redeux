import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def ConnectToDB():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="portfolio_site",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# ============================================ CONTACT SUBMISSIONS ============================================
def NewContactSubmission(data):
    """Add a new contact form submission"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact_me 
            (name, email, message)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (
            data.get('HumanName'),
            data.get('EmailAddy'),
            data.get('message')
        ))
        submission_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Contact submission {submission_id} saved to database")
        return True
    except Exception as e:
        print(f"❌ Error saving contact submission: {e}")
        print(f"   Data received: {data}")
        conn.rollback()
        conn.close()
        return False


def GetContactSubmissions():
    """Get all contact submissions (for dashboard)"""
    conn = ConnectToDB()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM contact_me 
            ORDER BY timestamp DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Error fetching contact submissions: {e}")
        conn.close()
        return []

def UpdateContactStatus(submission_id, new_status):
    """Update the status of a contact submission"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contact_me 
            SET status = %s 
            WHERE id = %s
        """, (new_status, submission_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated contact submission {submission_id} to {new_status}")
        return True
    except Exception as e:
        print(f"❌ Error updating contact status: {e}")
        conn.rollback()
        conn.close()
        return False


# ============================================ SUPPORT TICKETS ============================================
def NewSupportTicket(data):
    """Add a new support ticket"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO support (name, email, page, issue)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('name'),
            data.get('email'),
            data.get('page'),
            data.get('issue')
        ))
        ticket_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Support ticket {ticket_id} saved to database")
        return True
    except Exception as e:
        print(f"❌ Error saving support ticket: {e}")
        conn.rollback()
        conn.close()
        return False

def GetSupportTickets():
    """Get all support tickets (for dashboard)"""
    conn = ConnectToDB()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM support 
            ORDER BY timestamp DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Error fetching support tickets: {e}")
        conn.close()
        return []

def update_support_status(ticket_id, new_status):
    """Update the status of a support ticket"""
    conn = ConnectToDB()
    if not conn:
        print(f"❌ Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        # First check if the ticket exists
        cursor.execute("SELECT id FROM support WHERE id = %s", (ticket_id,))
        if not cursor.fetchone():
            print(f"❌ Support ticket {ticket_id} not found")
            cursor.close()
            conn.close()
            return False
        
        # Update the status
        cursor.execute("""
            UPDATE support 
            SET status = %s 
            WHERE id = %s
        """, (new_status, ticket_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            print(f"✅ Updated support ticket {ticket_id} to {new_status}")
            return True
        else:
            print(f"⚠️ No rows updated for ticket {ticket_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating support status: {e}")
        print(f"   Ticket ID: {ticket_id}, New Status: {new_status}")
        if conn:
            conn.rollback()
            conn.close()
        return False

# ============================================ GAME FEEDBACK ============================================
def NewGameFeedback(data):
    """Add new CATastrophe game feedback"""
    conn = ConnectToDB()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO game_feedback (name, email, stars, review)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            data.get("name"),
            data.get("email"),
            data.get("stars"),
            data.get("review")
        ))

        feedback_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        print(f"⭐ Game feedback {feedback_id} saved!")
        return True

    except Exception as e:
        print(f"❌ Error saving game feedback: {e}")
        conn.rollback()
        conn.close()
        return False


def GetGameFeedback():
    """Get all game feedback (admin/dashboard use)"""
    conn = ConnectToDB()
    if not conn:
        return []

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM game_feedback
            ORDER BY timestamp DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    except Exception as e:
        print(f"❌ Error fetching game feedback: {e}")
        conn.close()
        return []

def update_feedback_status(feedback_id, new_status):
    """Update the status of game feedback"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE game_feedback 
            SET status = %s 
            WHERE id = %s
        """, (new_status, feedback_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated game feedback {feedback_id} to {new_status}")
        return True
    except Exception as e:
        print(f"❌ Error updating feedback status: {e}")
        conn.rollback()
        conn.close()
        return False

def get_feedback_by_id(feedback_id):
    """Get a specific feedback by ID"""
    conn = ConnectToDB()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM game_feedback 
            WHERE id = %s
        """, (feedback_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Error fetching feedback: {e}")
        conn.close()
        return None


# ============================================ APP/WEBSITE REQUESTS ============================================
def submit_app_request(name, email, phone, request_type, timeline, budget, additional_info):
    """Submit a new app/website request"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_requests 
            (name, email, phone, type, project_timeline, project_details, status, time_submitted)
            VALUES (%s, %s, %s, %s, %s, %s, 'new', NOW())
            RETURNING id
        """, (name, email, phone, request_type, timeline, additional_info))
        
        request_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ App request {request_id} saved to database")
        return True
    except Exception as e:
        print(f"❌ Error saving app request: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_app_requests():
    """Get all app/website requests"""
    conn = ConnectToDB()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT * FROM app_requests 
            WHERE archived = FALSE
            ORDER BY time_submitted DESC
        """)
        
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        return requests
    except Exception as e:
        print(f"❌ Error fetching app requests: {e}")
        conn.close()
        return []

def get_app_request_stats():
    """Get statistics for app requests"""
    conn = ConnectToDB()
    if not conn:
        return {'total_requests': 0, 'new_requests': 0, 'recent_requests': []}
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as total FROM app_requests WHERE archived = FALSE")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as new FROM app_requests WHERE status = 'new' AND archived = FALSE")
        new = cursor.fetchone()['new']
        
        cursor.execute("""
            SELECT * FROM app_requests 
            WHERE archived = FALSE
            ORDER BY time_submitted DESC 
            LIMIT 5
        """)
        recent = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'total_requests': total,
            'new_requests': new,
            'recent_requests': recent
        }
    except Exception as e:
        print(f"❌ Error fetching app request stats: {e}")
        conn.close()
        return {'total_requests': 0, 'new_requests': 0, 'recent_requests': []}

def update_app_request_status(request_id, status):
    """Update the status of an app request"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE app_requests 
            SET status = %s 
            WHERE id = %s
        """, (status, request_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated app request {request_id} to {status}")
        return True
    except Exception as e:
        print(f"❌ Error updating app request status: {e}")
        conn.rollback()
        conn.close()
        return False

def update_app_request_notes(request_id, notes):
    """Update notes for an app request"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE app_requests 
            SET notes = %s 
            WHERE id = %s
        """, (notes, request_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated notes for app request {request_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating app request notes: {e}")
        conn.rollback()
        conn.close()
        return False

def archive_app_request_db(request_id):
    """Archive an app request"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE app_requests 
            SET archived = TRUE 
            WHERE id = %s
        """, (request_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Archived app request {request_id}")
        return True
    except Exception as e:
        print(f"❌ Error archiving app request: {e}")
        conn.rollback()
        conn.close()
        return False

# ============================================ WISHLIST ============================================
def NewWishlistItem(data):
    """Add a new enhancement/improvement to wishlist"""
    conn = ConnectToDB()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO wishlist 
            (source, enhancement_type, details, status, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING wishlist_id
        """, (
            data.get('source'),
            data.get('enhancement_type'),
            data.get('details'),
            data.get('status', 'not_started'),
            data.get('notes', '')
        ))
        wishlist_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Wishlist item {wishlist_id} saved to database")
        return True
    except Exception as e:
        print(f"❌ Error saving wishlist item: {e}")
        conn.rollback()
        conn.close()
        return False

def GetWishlist(filter_status=None):
    """Get all wishlist items, optionally filtered by status"""
    conn = ConnectToDB()
    if not conn:
        return []
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if filter_status:
            cursor.execute("""
                SELECT * FROM wishlist 
                WHERE status = %s AND archived = FALSE
                ORDER BY created_at DESC
            """, (filter_status,))
        else:
            cursor.execute("""
                SELECT * FROM wishlist 
                WHERE archived = FALSE
                ORDER BY created_at DESC
            """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Error fetching wishlist: {e}")
        conn.close()
        return []

def update_wishlist_status(wishlist_id, new_status):
    """Update the status of a wishlist item"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE wishlist 
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE wishlist_id = %s
        """, (new_status, wishlist_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated wishlist item {wishlist_id} to {new_status}")
        return True
    except Exception as e:
        print(f"❌ Error updating wishlist status: {e}")
        conn.rollback()
        conn.close()
        return False

def update_wishlist_notes(wishlist_id, notes):
    """Add/update notes for a wishlist item"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE wishlist 
            SET notes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE wishlist_id = %s
        """, (notes, wishlist_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Updated notes for wishlist item {wishlist_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating wishlist notes: {e}")
        conn.rollback()
        conn.close()
        return False

def archive_wishlist_item_db(wishlist_id):
    """Archive a wishlist item"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE wishlist 
            SET archived = TRUE, updated_at = NOW()
            WHERE wishlist_id = %s
        """, (wishlist_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Archived wishlist item {wishlist_id}")
        return True
    except Exception as e:
        print(f"❌ Error archiving wishlist item: {e}")
        conn.rollback()
        conn.close()
        return False

def delete_wishlist_item_db(wishlist_id):
    """Permanently delete a wishlist item"""
    conn = ConnectToDB()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM wishlist 
            WHERE wishlist_id = %s
        """, (wishlist_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Deleted wishlist item {wishlist_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting wishlist item: {e}")
        conn.rollback()
        conn.close()
        return False
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from functools import wraps
import uuid
import subprocess

from db_helpers import (
    NewContactSubmission, 
    UpdateContactStatus,
    GetContactSubmissions, 
    NewWishlistItem,
    GetWishlist,
    update_wishlist_status,
    update_wishlist_notes,
    delete_wishlist_item_db,
    archive_wishlist_item_db,
    submit_app_request,
    update_app_request_notes,
    update_app_request_status,
    get_all_app_requests,
    get_app_request_stats,
    archive_app_request_db,
    NewSupportTicket,
    GetSupportTickets,
    NewGameFeedback,
    GetGameFeedback
)

app = Flask(__name__)

# ============================================ ENVIRONMENTAL VARIABLES ============================================
app.secret_key = os.environ.get("SECRET_KEY")  
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")  
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  
RECEIVE_INBOX = os.environ.get("RECEIVE_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# ============================================ ADMIN DECORATOR ============================================
def AdminRequired(f):
    @wraps(f)
    def Decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return Decorated

# ============================================ EMAIL FUNCTIONS ============================================
def SendSMTP(message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(message["From"], message["To"], message.as_string())
        server.quit()
        return True, None
    except Exception as e1:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(message["From"], message["To"], message.as_string())
            server.quit()
            return True, None
        except Exception as e2:
            return False, f"587 error: {e1}; 465 error: {e2}"

def SendContactEmail(UserInput):
    """Send email for contact form submissions"""
    try:
        print(f"DEBUG: Starting contact email send for {UserInput.get('HumanName')}...")
        if not SENDER_EMAIL or not EMAIL_PASSWORD:
            raise RuntimeError("Email settings not configured")

        message = MIMEMultipart("alternative")
        subject = f"📬 CONTACT FORM: {UserInput.get('HumanName')}"
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVE_INBOX

        text = (
            f"📬 NEW CONTACT FORM SUBMISSION!\n\n"
            f"Name: {UserInput.get('HumanName')}\n"
            f"Email: {UserInput.get('EmailAddy')}\n\n"
            f"Message:\n{UserInput.get('message')}\n\n"
            f"Timestamp: {UserInput.get('timestamp')}\n"
        )
        part = MIMEText(text, "plain")
        message.attach(part)

        ok, err = SendSMTP(message)
        if ok:
            print(f"✅ Contact email sent successfully for {UserInput.get('HumanName')}")
        else:
            print(f"❌ Contact Email Error: {err}")
    except Exception as e:
        print(f"❌ Contact Email Error: {type(e).__name__}: {e}")


def SendSupportEmail(support_data):
    """Send email for support tickets"""
    try:
        print(f"DEBUG: Starting support email send for {support_data.get('name')}...")
        if not SENDER_EMAIL or not EMAIL_PASSWORD:
            raise RuntimeError("Email settings not configured")

        message = MIMEMultipart("alternative")
        subject = f"🆘 SUPPORT REQUEST: {support_data.get('page', 'Unknown Page')}"
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVE_INBOX

        text = (
            f"🆘 NEW SUPPORT REQUEST!\n\n"
            f"Name: {support_data.get('name')}\n"
            f"Email: {support_data.get('email', 'Not provided')}\n"
            f"Affected Page: {support_data.get('page')}\n\n"
            f"Issue Description:\n{support_data.get('issue')}\n\n"
            f"Timestamp: {support_data.get('timestamp')}\n"
        )
        part = MIMEText(text, "plain")
        message.attach(part)

        ok, err = SendSMTP(message)
        if ok:
            print(f"✅ Support email sent successfully for {support_data.get('name')}")
        else:
            print(f"❌ Support Email Error: {err}")
    except Exception as e:
        print(f"❌ Support Email Error: {type(e).__name__}: {e}")


def SendGameFeedbackEmail(feedback_data):
    """Send email for game feedback/reviews"""
    try:
        print(f"DEBUG: Starting game feedback email send for {feedback_data.get('name')}...")
        if not SENDER_EMAIL or not EMAIL_PASSWORD:
            raise RuntimeError("Email settings not configured")

        message = MIMEMultipart("alternative")
        stars_visual = "⭐" * feedback_data.get('stars', 0)
        subject = f"🎮 GAME REVIEW: {stars_visual} from {feedback_data.get('name')}"
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVE_INBOX

        text = (
            f"🎮 NEW CATASTROPHE GAME REVIEW!\n\n"
            f"Name: {feedback_data.get('name')}\n"
            f"Email: {feedback_data.get('email', 'Not provided')}\n"
            f"Rating: {stars_visual} ({feedback_data.get('stars')}/5)\n\n"
            f"Review:\n{feedback_data.get('review')}\n\n"
            f"Timestamp: {feedback_data.get('timestamp')}\n"
        )
        part = MIMEText(text, "plain")
        message.attach(part)

        ok, err = SendSMTP(message)
        if ok:
            print(f"✅ Game feedback email sent successfully for {feedback_data.get('name')}")
        else:
            print(f"❌ Game Feedback Email Error: {err}")
    except Exception as e:
        print(f"❌ Game Feedback Email Error: {type(e).__name__}: {e}")


# Async wrappers
def SendContactEmailAsync(submission):
    thread = Thread(target=SendContactEmail, args=(submission,))
    thread.daemon = True
    thread.start()

def SendSupportEmailAsync(support_data):
    thread = Thread(target=SendSupportEmail, args=(support_data,))
    thread.daemon = True
    thread.start()

def SendGameFeedbackEmailAsync(feedback_data):
    thread = Thread(target=SendGameFeedbackEmail, args=(feedback_data,))
    thread.daemon = True
    thread.start()





# ============================================ PUBLIC PAGE ROUTES ============================================
@app.route("/")
def home():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

# ============================================ CONTACT FORM ============================================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        NewRequest = {
            "HumanName": request.form.get("HumanName"),
            "EmailAddy": request.form.get("EmailAddy"),
            "message": request.form.get("message"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if NewContactSubmission(NewRequest):
            SendContactEmailAsync(NewRequest)
            flash("Message sent successfully!", "success")
            return redirect(url_for("contact"))
        else:
            flash("Error saving contact submission", "error")
            return redirect(url_for("contact"))
    
    return render_template("contact.html")


# ============================================ SUPPORT FORM ============================================
@app.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        new_support = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "page": request.form.get("page"),
            "issue": request.form.get("issue"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if NewSupportTicket(new_support):
            SendSupportEmailAsync(new_support)
            flash("Support request submitted! We'll get back to you soon.", "success")
            return redirect(url_for("support"))
        else:
            flash("Error submitting support request", "error")
            return redirect(url_for("support"))
    
    return render_template("support.html")


# ============================================ GAME FEEDBACK/REVIEWS ============================================
@app.route("/review", methods=["GET", "POST"])
def review():
    if request.method == "POST":
        feedback = {
            "name": request.form.get("name"),
            "email": request.form.get("email", ""),
            "stars": int(request.form.get("stars")),
            "review": request.form.get("review"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if NewGameFeedback(feedback):
            SendGameFeedbackEmailAsync(feedback)
            flash("⭐ Thanks for your feedback! You're pawsome!", "success")
            return redirect(url_for("review"))
        else:
            flash("❌ Error submitting feedback. Please try again.", "error")
            return redirect(url_for("review"))

    return render_template("review.html")


# ============================================ ADMIN PAGES ============================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid password", "error")
            return render_template("admin_login.html")
    
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('home'))

@app.route("/admin")
@AdminRequired
def admin_dashboard():
    contacts = GetContactSubmissions()
    support_tickets = GetSupportTickets()
    game_feedback = GetGameFeedback()
    
    unread_contacts = sum(1 for c in contacts if c.get('status') == 'unread')
    new_support = sum(1 for s in support_tickets if s.get('status') == 'new')
    new_feedback = sum(1 for f in game_feedback if f.get('status') == 'new')
    
    stats = {
        'unread_contacts': unread_contacts,
        'recent_contacts': contacts[:5],
        'new_support_tickets': new_support,
        'recent_support': support_tickets[:5],
        'new_game_feedback': new_feedback,
        'recent_feedback': game_feedback[:5]
    }

    return render_template("admin_dashboard.html", stats=stats)

# ===== MESSAGES AND SUGGESTIONS =====
@app.route('/admin/messages-suggestions')
@AdminRequired
def admin_messages_suggestions():
    try:
        contacts = GetContactSubmissions()
        unread_contacts = sum(1 for c in contacts if c['status'] == 'unread')
        
        return render_template('admin_messages_suggestions.html', 
                             contacts=contacts, 
                             unread_contacts=unread_contacts)
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/contact/update-status/<int:submission_id>/<status>", methods=["POST"])
@AdminRequired
def update_contact_submission_status(submission_id, status):
    if UpdateContactStatus(submission_id, status):
        flash(f"Contact marked as {status}", "success")
        return redirect(request.referrer or url_for('admin_messages_suggestions'))
    else:
        flash("Error updating status", "error")
        return redirect(request.referrer or url_for('admin_messages_suggestions'))


# ===== SUPPORT REQUESTS =====
@app.route('/admin/support')
@AdminRequired
def admin_support():
    try:
        tickets = GetSupportTickets()
        new_count = sum(1 for t in tickets if t.get('status') == 'new')
        
        return render_template('admin_support.html', 
                             tickets=tickets,
                             new_count=new_count)
    except Exception as e:
        flash(f'Error loading support tickets: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/support/<int:ticket_id>/status/<status>', methods=['POST'])
@AdminRequired
def update_support_status(ticket_id, status):
    """Update support ticket status"""
    try:
        from db_helpers import update_support_status as update_status_db
        update_status_db(ticket_id, status)
        flash(f'Ticket marked as {status.replace("_", " ")}!', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('admin_support'))


# ===== GAME FEEDBACK =====
@app.route('/admin/game-feedback')
@AdminRequired
def admin_game_feedback():
    try:
        feedback = GetGameFeedback()
        new_count = sum(1 for f in feedback if f.get('status') == 'new')
        
        return render_template('admin_game_feedback.html',
                             feedback=feedback,
                             new_count=new_count)
    except Exception as e:
        flash(f'Error loading game feedback: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/feedback/<int:feedback_id>/status/<status>', methods=['POST'])
@AdminRequired
def update_feedback_status(feedback_id, status):
    """Update game feedback status"""
    try:
        from db_helpers import update_feedback_status as update_status_db
        update_status_db(feedback_id, status)
        flash(f'Review marked as {status.replace("_", " ")}!', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('admin_game_feedback'))

@app.route('/admin/feedback/<int:feedback_id>/add-to-wishlist', methods=['POST'])
@AdminRequired
def add_feedback_to_wishlist(feedback_id):
    """Add game feedback suggestion to wishlist"""
    try:
        from db_helpers import get_feedback_by_id, update_feedback_status as update_status_db, NewWishlistItem
        
        feedback = get_feedback_by_id(feedback_id)
        if feedback:
            wishlist_item = {
                'source': f"{feedback['name']} (Game Review)",
                'enhancement_type': 'Game Feature',
                'details': f"⭐ {feedback['stars']}/5 - {feedback['review']}",
                'status': 'not_started',
                'notes': f"From review by {feedback['name']} on {feedback['timestamp'].strftime('%m-%d-%Y')}"
            }
            
            if NewWishlistItem(wishlist_item):
                update_status_db(feedback_id, 'added_to_wishlist')
                flash('✨ Added to wishlist successfully!', 'success')
            else:
                flash('❌ Error adding to wishlist', 'error')
        else:
            flash('❌ Feedback not found', 'error')
    except Exception as e:
        print(f"❌ Error adding feedback to wishlist: {e}")
        flash(f'❌ Error: {str(e)}', 'error')
    
    return redirect(url_for('admin_game_feedback'))


# ===== APP REQUESTS (PLACEHOLDER) =====
@app.route('/admin/app_requests')
@AdminRequired
def admin_app_requests():
    flash('App/Website requests feature coming soon!', 'info')
    return redirect(url_for('admin_dashboard'))


# ======= WISHLIST ======
@app.route("/admin/wishlist")
@AdminRequired
def admin_wishlist():
    filter_status = request.args.get('filter_status')
    
    wishlist_items = GetWishlist(filter_status)
    
    all_items = GetWishlist()
    all_count = len(all_items)
    not_started_count = sum(1 for item in all_items if item['status'] == 'not_started')
    in_progress_count = sum(1 for item in all_items if item['status'] == 'in_progress')
    completed_count = sum(1 for item in all_items if item['status'] == 'completed')
    revisiting_count = sum(1 for item in all_items if item['status'] == 'revisiting')
    
    return render_template("admin_wishlist.html", 
                         wishlist_items=wishlist_items,
                         filter_status=filter_status,
                         all_count=all_count,
                         not_started_count=not_started_count,
                         in_progress_count=in_progress_count,
                         completed_count=completed_count,
                         revisiting_count=revisiting_count)

@app.route("/admin/wishlist/add", methods=["POST"])
@AdminRequired
def add_wishlist_item_route():
    new_item = {
        'source': request.form.get('source', 'Me'),
        'enhancement_type': request.form.get('enhancement_type'),
        'details': request.form.get('details'),
        'status': 'not_started',
        'notes': request.form.get('notes', '')
    }
    
    if NewWishlistItem(new_item):
        flash("Wishlist item added!", "success")
        return redirect(url_for('admin_wishlist'))
    else:
        flash("Error adding wishlist item", "error")
        return redirect(url_for('admin_wishlist'))

@app.route("/admin/wishlist/update-status/<int:wishlist_id>/<status>", methods=["POST"])
@AdminRequired
def update_wishlist_status_route(wishlist_id, status):
    if update_wishlist_status(wishlist_id, status):
        flash(f"Wishlist item marked as {status}", "success")
        return redirect(request.referrer or url_for('admin_wishlist'))
    else:
        flash("Error updating status", "error")
        return redirect(request.referrer or url_for('admin_wishlist'))

@app.route("/admin/wishlist/update-notes/<int:wishlist_id>", methods=["POST"])
@AdminRequired
def update_wishlist_notes_route(wishlist_id):
    notes = request.form.get('notes', '')
    
    if update_wishlist_notes(wishlist_id, notes):
        flash("Notes updated!", "success")
        return redirect(request.referrer or url_for('admin_wishlist'))
    else:
        flash("Error updating notes", "error")
        return redirect(request.referrer or url_for('admin_wishlist'))

@app.route('/admin/wishlist/<int:wishlist_id>/archive', methods=['POST'])
@AdminRequired
def archive_wishlist_item(wishlist_id):
    try:
        archive_wishlist_item_db(wishlist_id)
        flash('Wishlist item archived successfully!', 'success')
    except Exception as e:
        flash(f'Error archiving item: {str(e)}', 'error')
    
    return redirect(url_for('admin_wishlist'))

@app.route('/admin/wishlist/<int:wishlist_id>/delete', methods=['POST'])
@AdminRequired
def delete_wishlist_item(wishlist_id):
    try:
        delete_wishlist_item_db(wishlist_id)
        flash('Wishlist item permanently deleted!', 'success')
    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('admin_wishlist'))


# ============================================ AUDIO CONVERTER ============================================
@app.route("/audio-converter")
def audio_converter():
    return render_template("audio_converter.html")

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("audio")
    if not file:
        flash("No file uploaded!", "error")
        return redirect(url_for('audio_converter'))
    
    filename = file.filename.lower() # CHECK FILE EXTENSION
    allowed_extensions = ['.m4a', '.wav', '.flac', '.ogg', '.aac', '.wma']
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        flash("Invalid file type. Please upload an audio file.", "error")
        return redirect(url_for('audio_converter'))
    
    input_ext = os.path.splitext(filename)[1] # UNIQUE FILE NAMES TO AVOID COLLISIONS
    input_name = f"{uuid.uuid4()}{input_ext}"
    output_name = f"{uuid.uuid4()}.mp3"
    
    UPLOAD_FOLDER = "uploads"
    OUTPUT_FOLDER = "outputs"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    input_path = os.path.join(UPLOAD_FOLDER, input_name)
    output_path = os.path.join(OUTPUT_FOLDER, output_name)
    
    try:
        file.save(input_path)
        
        subprocess.run([ # CONVERT USING FFmpeg
           "ffmpeg", "-i", input_path,
           "-vn", "-ab", "192k", output_path
           # r"C:\Users\mkb00\ffmpeg\bin\ffmpeg.exe", "-i", input_path,
           # "-vn", "-ab", "192k", output_path
        ], check=True, capture_output=True)
        
        response = send_file( # SERVE FILES FOR DOWNLOAD
            output_path, 
            as_attachment=True, 
            download_name=f"converted_{os.path.splitext(filename)[0]}.mp3"
        )
        
        @response.call_on_close # CLEAN UP TEMP FILES
        def cleanup():
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
        
        return response
        
    except subprocess.CalledProcessError as e:
        flash(f"Conversion failed: {e}", "error") # CLEANUP ON ERROR
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        return redirect(url_for('audio_converter'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('audio_converter'))

# ============================================ MAIN ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
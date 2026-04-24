#cd /Users/hiradkhademian/Desktop/MSGuidApp/backend
#cd /Users/hiradkhademian/Desktop/MSGuidApp/backend/instance

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import secrets
import requests
import random
from bs4 import BeautifulSoup
from flask_mail import Mail, Message
from flask import jsonify
from datetime import datetime, timedelta
from googlesearch import search
import difflib
from flask_socketio import SocketIO, emit
from twilio.rest import Client
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
import asyncio
import nest_asyncio
import base64
from requests_html import HTMLSession
import traceback
from email.mime.text import MIMEText
import smtplib
from email.message import EmailMessage










nest_asyncio.apply() 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app)


# Twilio Credentials (Replace with actual credentials)
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
CARETAKER_PHONE_NUMBER = "+1234567890"  # Replace with caregiver's number


# Replace these with your eBay API keys
EBAY_CLIENT_ID = ""  # Client ID (App ID)
EBAY_CLIENT_SECRET = ""  # Client Secret (Cert ID)
EBAY_OAUTH_URL = ""



app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587  # 587 for TLS, or 465 for SSL
app.config["MAIL_USE_TLS"] = True  # Enables TLS encryption
app.config["MAIL_USE_SSL"] = False  # Set False if using TLS
app.config["MAIL_USERNAME"] = ""  
app.config["MAIL_PASSWORD"] = ""  

PHONE_NUMBER = ""                # Caregiver's phone number (digits only)
CARRIER_GATEWAY = ""                # Dummy gateway domain for demo




mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ms_guid_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

# Define the ExercisePlan model (for exercise plans)
class ExercisePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional for custom plans

# Define the ExerciseProgress model (to track progress)
class ExerciseProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_plan_id = db.Column(db.Integer, db.ForeignKey('exercise_plan.id'), nullable=False)
    progress_date = db.Column(db.String(50), nullable=False)
    exercises_completed = db.Column(db.Text, nullable=False)
    mobility_improvement_score = db.Column(db.Integer, nullable=True)


class SymptomLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    fatigue_level = db.Column(db.Integer)
    pain_level = db.Column(db.Integer)
    mood = db.Column(db.String(50))
    notes = db.Column(db.Text)    

# Define the User model (Users table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    exercise_plans = db.relationship('ExercisePlan', backref='user', lazy=True)
    exercise_progress = db.relationship('ExerciseProgress', backref='user', lazy=True)
    user_groups = db.relationship('UserGroup', backref='user', lazy=True)


# Define the TelemedicineAppointment model (New table)
class TelemedicineAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.String(50), nullable=False)
    appointment_time = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text, nullable=False)

# Support Group model
class SupportGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    members = db.relationship('UserGroup', backref='support_group', lazy=True)

# Join table: Users <-> Support Groups
class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    support_group_id = db.Column(db.Integer, db.ForeignKey('support_group.id'), nullable=False)


class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    support_group_id = db.Column(db.Integer, db.ForeignKey('support_group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='messages')
    group = db.relationship('SupportGroup', backref='messages')


class AssistiveDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amazon_link = db.Column(db.String(200), nullable=True)  
    ebay_link = db.Column(db.String(200), nullable=True)  
    best_option = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<AssistiveDevice {self.device_name}>"
    

class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    specialty = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)  

    def __repr__(self):
        return f"<Mentor {self.name}>"
    


class EmergencyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default="Pending")  # Status: Pending, Resolved

    def __repr__(self):
        return f"<EmergencyRequest {self.id} - {self.status}>"


# Define Caregiver Inquiry model
class CaregiverInquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    inquiry = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<CaregiverInquiry {self.name}>"

# Create the database tables
with app.app_context():
    db.create_all()
   # Auto-add support groups
    predefined_groups = [
        {'group_name': 'MS Caregivers Support', 'description': 'Support for those caring for someone with MS.'},
        {'group_name': 'Living with MS', 'description': 'For individuals living with MS to share their stories.'},
        {'group_name': 'MS Research Updates', 'description': 'Stay informed on the latest MS research.'},
        {'group_name': 'MS Youth Support', 'description': 'Resources for young people affected by MS.'}
    ]
    
    for group_data in predefined_groups:
        existing = SupportGroup.query.filter_by(group_name=group_data['group_name']).first()
        if not existing:
            db.session.add(SupportGroup(**group_data))
    
    db.session.commit()


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return redirect(url_for('login'))



def get_ebay_access_token():
    """
    Retrieve an OAuth access token for eBay sandbox API.
    """
    # Create credentials string and encode in base64
    credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    # Set the data to request a client_credentials token
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(EBAY_OAUTH_URL, headers=headers, data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Successfully retrieved eBay OAuth Token:", token)
        return token
    else:
        print("ERROR: Unable to retrieve eBay token:", response.text)
        return None















@app.route('/request_mentorship/<int:mentor_id>', methods=['GET', 'POST'])
def request_mentorship(mentor_id):
    mentor = Mentor.query.get_or_404(mentor_id)

    if request.method == "POST":
        mentee_email = request.form["email"]
        message_body = request.form["message"]
        preferred_contact = request.form["preferred_contact"]

        # Create the email message
        msg = Message(
            subject="Mentorship Request",
            sender="your-email@example.com",  # Replace with your email
            recipients=[mentor.email],  # Ensure `mentor.email` exists in the database
            body=f"""Hello {mentor.name},

You have received a mentorship request from:

- Email: {mentee_email}
- Preferred Contact: {preferred_contact}

Message:
{message_body}

Please respond to them at your earliest convenience.

Best Regards,
MS Support Webpage
            """
        )

        # Send email
        mail.send(msg)

        flash("Your mentorship request has been sent successfully!", "success")
        return redirect(url_for("mentorship_page"))

    return render_template("request_mentorship.html", mentor=mentor)












@app.route('/caregiver_resources', methods=["GET", "POST"])
def caregiver_resources():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        inquiry = request.form["inquiry"]

        if not name or not email or not inquiry:
            flash("All fields are required!", "danger")
            return redirect(url_for("caregiver_resources"))

        # Save inquiry to database
        new_inquiry = CaregiverInquiry(name=name, email=email, inquiry=inquiry)
        db.session.add(new_inquiry)
        db.session.commit()

        # Send email notification
        msg = Message(
            subject="New Caregiver Inquiry",
            sender="hiradsekoya@gmail.com",
            recipients=["hiradnabilety17@gmail.com"],  # Admin notification
            body=f"New Inquiry from {name} ({email}):\n\n{inquiry}"
        )
        mail.send(msg)

        flash("Your inquiry has been submitted successfully!", "success")
        return redirect(url_for("caregiver_resources"))

    return render_template("caregiver_resources.html")


















@app.route('/assistive_technology', methods=["GET", "POST"])
def assistive_technology():
    amazon_products = []  # For holding Amazon scraping results (optional)
    ebay_products = []    # For holding eBay API results
    
    if request.method == "POST":
        device_name = request.form.get("device_name")
        if not device_name:
            flash("Device name is required!", "danger")
            return redirect(url_for("assistive_technology"))
        
        # ---------------------------
        # Optional: Amazon Scraping
        # ---------------------------
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        amazon_url = f"https://www.amazon.com/s?k={device_name.replace(' ', '+')}"
        response = requests.get(amazon_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        amazon_items = soup.select("div[data-component-type='s-search-result']")
        for item in amazon_items[:5]:
            title_elem = item.h2
            title = title_elem.text.strip() if title_elem else "No title"
            price_whole_elem = item.find("span", class_="a-price-whole")
            price_fraction_elem = item.find("span", class_="a-price-fraction")
            if price_whole_elem and price_fraction_elem:
                price = f"${price_whole_elem.text.strip()}{price_fraction_elem.text.strip()}"
            else:
                price = "Price not available"
            link_elem = item.find("a", class_="a-link-normal")
            link = f"https://www.amazon.com{link_elem.get('href')}" if (link_elem and link_elem.get("href")) else None
            if title and link:
                amazon_products.append({
                    "name": title,
                    "price": price,
                    "link": link
                })
        
        # ---------------------------
        # eBay API Search Using Sandbox OAuth Token with limit=3
        # ---------------------------
        ebay_access_token = get_ebay_access_token()
        if not ebay_access_token:
            flash("Error retrieving eBay API token. Try again later.", "danger")
            return redirect(url_for("assistive_technology"))
        
        ebay_headers = {
            "Authorization": f"Bearer {ebay_access_token}",
            "Content-Type": "application/json"
        }
        
        # Build the eBay sandbox URL with the search query and limit=3
        ebay_url = f"https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search?q={device_name.replace(' ', '+')}&limit=3"
        ebay_response = requests.get(ebay_url, headers=ebay_headers)
        print("DEBUG: eBay response status:", ebay_response.status_code)
        print("DEBUG: eBay response text:", ebay_response.text)
        
        try:
            ebay_data = ebay_response.json()
            ebay_items = ebay_data.get("itemSummaries", [])
            for item in ebay_items:
                ebay_products.append({
                    "name": item.get("title", "No title"),
                    "price": f"${item.get('price', {}).get('value', 'N/A')}",
                    "link": item.get("itemWebUrl")
                })
        except Exception as e:
            print("DEBUG: Error processing eBay response:", e)
        
        return render_template(
            "assistive_technology.html",
            amazon_products=amazon_products,
            ebay_products=ebay_products
        )
    
    return render_template("assistive_technology.html", amazon_products=[], ebay_products=[])

















# Helper function that generates the initial diet plan.
def generate_diet(diet, calories, allergies):
    plan = f"Recommended {diet.capitalize()} Plan:\n"
    if calories:
        plan += f"Target Calories: {calories}\n"
    if allergies:
        plan += f"Avoid: {allergies}\n"
    plan += (
        "\nMeal Suggestions:\n"
        "Breakfast: Oatmeal with fruits\n"
        "Lunch: Quinoa salad with lean protein\n"
        "Snack: Fresh veggies with hummus\n"
        "Dinner: Grilled fish (or tofu) with steamed veggies\n"
    )
    return plan

# Helper function that generates an alternative diet plan.
def generate_alternative_diet(diet, calories, allergies):
    alternatives = [
        "Breakfast: Smoothie bowl with berries and spinach\nLunch: Avocado toast with egg\nSnack: Greek yogurt with honey and nuts\nDinner: Stir-fried veggies with brown rice",
        "Breakfast: Scrambled eggs with spinach and toast\nLunch: Lentil soup with a side salad\nSnack: Apple slices with peanut butter\nDinner: Baked chicken (or tofu) with roasted broccoli",
        "Breakfast: Whole-grain cereal with almond milk and banana\nLunch: Chickpea salad with cucumbers, tomatoes, and feta\nSnack: Carrot sticks with guacamole\nDinner: Grilled salmon (or tempeh) with quinoa"
    ]
    plan = f"Alternative {diet.capitalize()} Plan:\n"
    if calories:
        plan += f"Target Calories: {calories}\n"
    if allergies:
        plan += f"Avoid: {allergies}\n"
    plan += "\nMeal Suggestions:\n" + random.choice(alternatives)
    return plan












@app.route('/nutrition_plans', methods=['GET', 'POST'])
def nutrition_plans():
    diet_plan = None
    # Initialize the favorites list in the session if not already present.
    favorites = session.get('favorites', [])
    
    if request.method == 'POST':
        # Use a hidden field value 'action' to determine which button was clicked.
        action = request.form.get('action')
        diet = request.form.get('diet')
        calories = request.form.get('calories')
        allergies = request.form.get('allergies')
        
        if not diet:
            flash("Please select a diet type.", "danger")
            return redirect(url_for('nutrition_plans'))
        
        if action == "get_diet":
            diet_plan = generate_diet(diet, calories, allergies)
        elif action == "generate_alternative":
            diet_plan = generate_alternative_diet(diet, calories, allergies)
        # The following branches use the hidden field 'current_diet_plan'
        elif action == "add_to_favorites":
            current_plan = request.form.get("current_diet_plan")
            if current_plan:
                favorites.append(current_plan)
                session['favorites'] = favorites
                flash("Diet plan added to favorites!", "success")
                diet_plan = current_plan
            else:
                flash("No diet plan available to add.", "warning")
        elif action == "add_alternative_to_favorites":
            current_plan = request.form.get("current_diet_plan")
            if current_plan:
                favorites.append(current_plan)
                session['favorites'] = favorites
                flash("Alternative diet plan added to favorites!", "success")
                diet_plan = current_plan
            else:
                flash("No alternative diet plan available to add.", "warning")
    
    return render_template('nutrition_plans.html', diet_plan=diet_plan, favorites=favorites)








@app.route('/api/faqs')
def get_faqs():
    return jsonify(faqs)





@app.route("/faqs")
def faqs_page():
    return render_template("faqs.html")





@app.route("/api/check-new-faqs")
def check_new_faqs():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get('https://www.nationalmssociety.org/About-the-Society/News', headers=headers, timeout=10)

        print("Status Code:", response.status_code)

        if response.status_code != 200:
            return jsonify({"articles": []})

        soup = BeautifulSoup(response.content, 'html.parser')

        # ✅ Updated selector based on current site structure
        article_elements = soup.find_all('li', class_='news-item')  # Was div.list_item
        recent_articles = []
        one_year_ago = datetime.now() - timedelta(days=365)

        for item in article_elements:
            title_tag = item.find('h3', class_='title')
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"

            date_tag = item.find('time')
            article_date = None

            if date_tag:
                try:
                    article_date = datetime.strptime(date_tag.get_text(strip=True), "%B %d, %Y")
                except ValueError:
                    print(f"Could not parse date from: {date_tag.get_text(strip=True)}")
                    pass  # Skip bad dates

            if not date_tag or article_date >= one_year_ago:
                print("Added:", title)
                recent_articles.append(title)

        print(f"Found {len(recent_articles)} recent articles")  # Debug output
        return jsonify({"articles": recent_articles})

    except Exception as e:
        print("Error fetching new FAQs:", e)
        return jsonify({"articles": []})








@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        new_user = User(phone_number=phone_number, name=name, surname=surname, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')







@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.name
            session['user_id'] = user.id 
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template('login.html')






@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))







@app.route('/track_symptoms', methods=['GET', 'POST'])
def track_symptoms():
    if 'username' not in session:
        flash("Please log in to track symptoms", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        date = request.form['date']
        fatigue_level = int(request.form.get('fatigue_level', 0))
        pain_level = int(request.form.get('pain_level', 0))
        mood = request.form.get('mood', '')
        notes = request.form.get('notes', '')

        new_log = SymptomLog(
            user_id=user_id,
            date=date,
            fatigue_level=fatigue_level,
            pain_level=pain_level,
            mood=mood,
            notes=notes
        )
        db.session.add(new_log)
        db.session.commit()
        flash("Symptom log saved!", "success")
        return redirect(url_for('view_symptoms'))

    return render_template('track_symptoms.html')












def send_sms_alert(message):
    """
    Send an emergency SMS notification via an email-to-SMS gateway.
    This function constructs an email message that the carrier's gateway converts to an SMS.
    """
    recipient = f"{PHONE_NUMBER}@{CARRIER_GATEWAY}"
    alert_body = f"🚨 Emergency Alert!\n\n{message}\n\nPlease respond immediately."
    
    # Create an EmailMessage object, which handles UTF-8 by default.
    msg = EmailMessage()
    msg.set_content(alert_body)
    msg["From"] = app.config["MAIL_USERNAME"]
    msg["To"] = recipient
    msg["Subject"] = ""  # SMS usually ignores the subject

    try:
        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            server.send_message(msg)
        print("Email-to-SMS sent successfully!")
    except Exception as e:
        print("Error sending Email-to-SMS:", e)

@app.route('/emergency_resources', methods=['GET', 'POST'])
def emergency_resources():
    emergency_guidelines = [
        "📌 Stay Calm: Try to remain as composed as possible during an emergency.",
        "📞 Call for Help: Dial emergency services (911 or your local equivalent).",
        "💊 Medication: If applicable, take prescribed emergency medication.",
        "🚨 Symptoms to Watch: Sudden weakness, difficulty breathing, severe dizziness.",
        "👥 Contact Support: Reach out to caregivers or a designated emergency contact.",
    ]
    if request.method == "POST":
        user_message = request.form.get("message")
        if user_message:
            new_request = EmergencyRequest(message=user_message)
            db.session.add(new_request)
            db.session.commit()
            send_sms_alert(user_message)
            flash("Emergency request submitted! A caregiver has been notified via SMS.", "success")
    emergency_requests = EmergencyRequest.query.order_by(EmergencyRequest.timestamp.desc()).all()
    return render_template('emergency_resources.html',
                           emergency_guidelines=emergency_guidelines,
                           emergency_requests=emergency_requests)









@app.route('/view_symptoms')
def view_symptoms():
    if 'username' not in session:
        flash("Please log in to view symptom logs", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    logs = SymptomLog.query.filter_by(user_id=user_id).order_by(SymptomLog.date.desc()).all()
    return render_template('view_symptoms.html', logs=logs)








@app.route('/exercise_plans')
def exercise_plans():
    if 'username' not in session:
        flash("Please log in to view your exercise plans", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']  # Assuming user_id is stored in session
    plans = ExercisePlan.query.filter_by(user_id=user_id).all()  # Retrieve exercise plans for the logged-in user

    # Retrieve exercise progress for each plan
    for plan in plans:
        plan.exercise_progress = ExerciseProgress.query.filter_by(exercise_plan_id=plan.id).all()

    return render_template('exercise_plans.html', plans=plans)







@app.route('/track_progress/<int:plan_id>', methods=['GET', 'POST'])
def track_progress(plan_id):
    if 'username' not in session:
        flash("Please log in to track progress", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']  # Assuming user_id is stored in session
    plan = ExercisePlan.query.filter_by(id=plan_id, user_id=user_id).first()

    if plan is None:
        flash("Exercise plan not found", "danger")
        return redirect(url_for('exercise_plans'))

    if request.method == 'POST':
        progress_date = request.form['progress_date']
        exercises_completed = request.form['exercises_completed']
        mobility_improvement_score = request.form.get('mobility_improvement_score', None)

        new_progress = ExerciseProgress(
            user_id=user_id,
            exercise_plan_id=plan_id,
            progress_date=progress_date,
            exercises_completed=exercises_completed,
            mobility_improvement_score=mobility_improvement_score
        )

        db.session.add(new_progress)
        db.session.commit()

        flash('Progress recorded successfully!', 'success')
        return redirect(url_for('exercise_plans'))

    # Get the latest progress for the plan
    latest_progress = ExerciseProgress.query.filter_by(exercise_plan_id=plan.id).order_by(ExerciseProgress.progress_date.desc()).first()

    return render_template('track_progress.html', plan=plan, latest_progress=latest_progress)


# Define the available support groups
support_groups = {
    'caregivers': 'MS Caregivers Support',
    'living_with_ms': 'Living with MS',
    'research_updates': 'MS Research Updates',
    'youth_support': 'MS Youth Support'
}







@app.route('/support_groups')
def support_groups_page():
    # Make sure user is logged in
    if 'user_id' not in session:
        flash("Please log in to view support groups", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Fetch all groups
    groups = SupportGroup.query.all()

    # Get IDs of groups user has already joined
    joined_group_ids = {ug.support_group_id for ug in UserGroup.query.filter_by(user_id=user_id).all()}

    # Pass both variables to the template
    return render_template('support_groups.html', groups=groups, joined_group_ids=joined_group_ids)






@app.route('/join_group/<int:group_id>')
def join_group(group_id):
    if 'user_id' not in session:
        flash("Please log in to join a group", "danger")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    existing = UserGroup.query.filter_by(user_id=user_id, support_group_id=group_id).first()
    
    if not existing:
        db.session.add(UserGroup(user_id=user_id, support_group_id=group_id))
        db.session.commit()
    
    group = SupportGroup.query.get_or_404(group_id)
    return redirect(url_for('chat_room', group_id=group.id))






@app.route('/mentorship')
def mentorship_page():
    mentors = Mentor.query.all()  # Fetch available mentors
    return render_template('mentorship.html', mentors=mentors)






@app.route('/become_mentor', methods=['GET', 'POST'])
def become_mentor():
    if request.method == 'POST':
        name = request.form['name']
        experience_years = request.form['experience_years']
        specialty = request.form['specialty']
        email = request.form['email']  # ✅ Make sure email is being retrieved

        if not email:  # ✅ Validate email before inserting
            flash("Email is required!", "danger")
            return redirect(url_for('become_mentor'))

        new_mentor = Mentor(name=name, experience_years=experience_years, specialty=specialty, email=email)
        db.session.add(new_mentor)
        db.session.commit()

        flash("You are now a mentor!", "success")
        return redirect(url_for('mentorship_page'))

    return render_template('become_mentor.html')






@app.route('/find_mentor')
def find_mentor():
    mentors = Mentor.query.all()
    return render_template('find_mentor.html', mentors=mentors)





@app.route('/chat_room/<int:group_id>')
def chat_room(group_id):
    if 'user_id' not in session:
        flash("Please log in to access the chat room", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    group = SupportGroup.query.get_or_404(group_id)

    # Fetch recent messages
    messages = GroupMessage.query.filter_by(support_group_id=group_id).order_by(GroupMessage.timestamp.desc()).limit(50).all()

    # Convert messages to JSON format
    messages_json = [{"message": msg.message, "user_id": msg.user_id} for msg in messages]

    return render_template('chat_room.html', group=group, messages=messages_json, current_user_id=user_id)






@app.route('/group_joined')
def group_joined():
    return render_template('group_joined.html')





@app.route('/book_telemedicine', methods=['GET', 'POST'])
def book_telemedicine():
    # Use the username stored in session (from your login route) to filter appointments
    username = session.get('username')
    
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        phone_number = request.form['phone_number']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        reason = request.form['reason']

        # Create a new appointment record
        new_appointment = TelemedicineAppointment(
            patient_name=patient_name,
            phone_number=phone_number,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason
        )

        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment booked successfully!", "success")

        # Retrieve appointments for the logged‑in user using the username
        appointments = TelemedicineAppointment.query.filter_by(
            patient_name=username
        ).order_by(TelemedicineAppointment.appointment_date).all()
        
        # Pass the new appointment as the confirmation variable
        return render_template('telemedicine.html', appointments=appointments, confirmation=new_appointment)
    
    # GET: retrieve existing appointments for the user
    appointments = TelemedicineAppointment.query.filter_by(
        patient_name=username
    ).order_by(TelemedicineAppointment.appointment_date).all()
    return render_template('telemedicine.html', appointments=appointments)




@app.route('/add_exercise_plan', methods=['GET', 'POST'])
def add_exercise_plan():
    if 'username' not in session:
        flash("Please log in to add an exercise plan", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        plan_name = request.form['plan_name']
        difficulty_level = request.form['difficulty_level']
        description = request.form['description']
        user_id = session['user_id']  # Assuming user_id is stored in session

        new_plan = ExercisePlan(
            plan_name=plan_name,
            difficulty_level=difficulty_level,
            description=description,
            user_id=user_id
        )

        db.session.add(new_plan)
        db.session.commit()

        flash('Exercise plan added successfully!', 'success')
        return redirect(url_for('exercise_plans'))

    return render_template('add_exercise_plan.html')


@app.route('/ms_info_hub')
def ms_info():
    return render_template('ms_info_hub.html')


@app.route('/research_updates')
def research_updates():
    return render_template('research_updates.html')

@app.route('/mental_health')
def mental_health():
    return render_template('mental_health.html')


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

def get_closest_match(query):
    matches = []
    for faq in faqs:
        q_score = difflib.SequenceMatcher(None, query.lower(), faq["question"].lower()).ratio()
        a_score = difflib.SequenceMatcher(None, query.lower(), faq["answer"].lower()).ratio()
        if q_score > 0.6 or a_score > 0.6:
            matches.append((faq, max(q_score, a_score)))
    if matches:
        return max(matches, key=lambda x: x[1])[0]
    return None

try:
    from googlesearch import search
except ImportError:
    search = None
    print("⚠️ Googlesearch module not found. Use: pip install googlesearch-python")



faqs = [
    {"question": "What is Multiple Sclerosis?", "answer": "MS is a chronic autoimmune disease where the immune system attacks the protective myelin sheath covering nerve fibers in the central nervous system, leading to communication issues between the brain and the rest of the body."},
    {"question": "What causes MS?", "answer": "The exact cause is unknown, but it's believed to result from a combination of genetic susceptibility and environmental factors, such as low vitamin D levels, smoking, and certain viral infections."},
    {"question": "Who is at risk of developing MS?", "answer": "MS is more common in women than men and typically diagnosed between ages 20 and 50. Factors like family history, certain infections, and geographic location may influence risk."},
    {"question": "What are common symptoms of MS?", "answer": "Symptoms vary but often include fatigue, numbness or tingling, vision problems, muscle weakness, balance issues, and cognitive changes."},
    {"question": "How is MS diagnosed?", "answer": "Diagnosis involves a combination of medical history, neurological exams, MRI scans, and sometimes spinal fluid analysis to rule out other conditions."},
    {"question": "Is MS contagious or fatal?", "answer": "MS is neither contagious nor directly fatal. While it can lead to disability, many people with MS have a normal or near-normal life expectancy with appropriate management."},
    {"question": "Is there a cure for MS?", "answer": "Currently, there's no cure, but various treatments can help manage symptoms, reduce relapses, and slow disease progression."},
    {"question": "What treatments are available?", "answer": "Treatment options include disease-modifying therapies (DMTs), corticosteroids for relapses, physical therapy, and lifestyle modifications to manage symptoms."},
    {"question": "Can lifestyle changes help?", "answer": "Yes, regular exercise, a balanced diet, stress management, and avoiding smoking can positively impact MS management."},
    {"question": "Can I have children if I have MS?", "answer": "Yes, many people with MS have healthy pregnancies. However, it's essential to discuss family planning with your healthcare provider to manage medications and monitor health."},
    {"question": "Is MS hereditary?", "answer": "While MS isn't directly inherited, having a close relative with MS slightly increases your risk."},
    {"question": "Will MS affect my ability to work or drive?", "answer": "Many individuals with MS continue to work and drive. However, adjustments may be necessary depending on symptom severity. It's important to consult with healthcare professionals and, if needed, occupational therapists."}
]

try:
    from googlesearch import search
except ImportError:
    search = None
    print("⚠️ Googlesearch module not found. Use: pip install googlesearch-python")

@app.route('/api/chat', methods=['POST'])
def answer_question():
    user_query = request.json.get("query", "").strip().lower()
    
    if not user_query:
        return jsonify({
            "question": "",
            "answer": "Please ask something."
        })

    # Check if the question matches any FAQ
    for faq in faqs:
        if user_query in faq["question"].lower() or user_query in faq["answer"].lower():
            return jsonify(faq)

    try:
        # First attempt to get results from the National MS Society website directly
        ms_society_results = []
        response = requests.get(
            f"https://www.nationalmssociety.org/Search-Results?k={user_query}", 
            timeout=10
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            titles = soup.find_all('h3', class_='title')[:3]
            ms_society_results = [item.get_text(strip=True) for item in titles]

        # Now do a general Google search for results from nationalmssociety.org
        web_results = []
        try:
            all_urls = list(search(user_query + " site:nationalmssociety.org"))
            for url in all_urls[:3]:
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        soup = BeautifulSoup(res.content, 'html.parser')
                        snippet = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')[:2]])
                        snippet = snippet if snippet else "No summary available."
                        web_results.append({
                            "url": url,
                            "snippet": snippet
                        })
                except Exception as inner_e:
                    print("Error fetching a result page:", inner_e)
        except Exception as search_error:
            print("Google search failed:", search_error)

        if ms_society_results or web_results:
            return jsonify({
                "question": user_query,
                "answer": "I couldn't find an exact FAQ match. Here's what I found online.",
                "ms_society_results": ms_society_results,
                "web_results": web_results
            })
        else:
            return jsonify({
                "question": user_query,
                "answer": "I couldn't find recent articles about this topic.",
                "ms_society_results": [],
                "web_results": []
            })

    except Exception as e:
        print("Error fetching from web:", e)
        return jsonify({
            "question": user_query,
            "answer": "I'm having trouble finding information right now. Please try rephrasing."
        })
    



@app.route('/mindfulness')
def mindfulness():
    return render_template('mindfulness.html')









@app.route('/fetch_ms_info_ajax', methods=['POST'])
def fetch_ms_info_ajax():
    try:
        session = HTMLSession()
        url = "https://www.nationalmssociety.org/About-the-Society/News"
        
        # Fetch the page and render (temporarily disable headless if needed for debugging)
        r = session.get(url)
        r.html.render(timeout=20, sleep=3)  # Add headless=False for visual debugging if desired
        
        rendered_html = r.html.html
        print("DEBUG: Total rendered HTML length:", len(rendered_html))
        
        if "newsarticle_click" in rendered_html:
            print("DEBUG: Found 'newsarticle_click' in the rendered HTML!")
        else:
            print("DEBUG: 'newsarticle_click' not found in rendered HTML.")
        
        # Optional: List all anchor tags with their classes for inspection
        soup = BeautifulSoup(rendered_html, 'html.parser')
        all_links = soup.find_all('a')
        for link in all_links:
            classes = link.get('class')
            text = link.get_text(strip=True)
            if classes and text:
                print(f"DEBUG: {classes} -> {text}")
        
        # Try extracting articles using the originally expected selector
        article_link_elements = soup.find_all('a', class_='newsarticle_click')
        print(f"DEBUG: Found {len(article_link_elements)} elements with class 'list_item'")
        
        articles = []
        for element in article_link_elements:
            title = element.get_text(strip=True)
            href = element.get('href')
            articles.append({'title': title, 'link': href})
        
        print(f"DEBUG: Final extracted article count: {len(articles)}")
        session.close()
        
        if not articles:
            return jsonify({
                'ms_info': "Successfully fetched info, but no articles were found.",
                'articles': []
            })
        
        return jsonify({
            'ms_info': "Latest Multiple Sclerosis Research & News Updates",
            'articles': articles
        })
    
    except Exception as e:
        print("DEBUG: Error occurred:", e)
        import traceback
        traceback.print_exc()
        return jsonify({
            'ms_info': f"An error occurred while retrieving MS information: {e}",
            'articles': []
        })



@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('send_message')
def handle_send_message(data):
    user_id = session.get('user_id')
    group_id = data.get('group_id')
    message = data.get('message')

    if not user_id:
        return

    # Save message to DB
    new_message = GroupMessage(
        support_group_id=group_id,
        user_id=user_id,
        message=message
    )
    db.session.add(new_message)
    db.session.commit()

    # Broadcast to everyone in the same group
    emit("receive_message", {
        "message": message,
        "user_id": user_id,
        "group_id": group_id
    }, broadcast=True)












# Route for appointment confirmation
#@app.route('/book_telemedicine', methods=['GET', 'POST'])
#def book_telemedicine():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        phone_number = request.form['phone_number']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        reason = request.form['reason']

        # Create a new telemedicine appointment
        new_appointment = TelemedicineAppointment(
            patient_name=patient_name,
            phone_number=phone_number,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason
        )

      #  db.session.add(new_appointment)
      #  db.session.commit()

       # flash("Appointment booked successfully!", "success")

        # Pass the appointment to the confirmation page
      #  return render_template('confirm_appointment.html', appointment=new_appointment)

    #return render_template('telemedicine.html')



if __name__ == '__main__':
      socketio.run(app, debug=True, use_reloader=False)
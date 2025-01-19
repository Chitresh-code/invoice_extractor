from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from src.logger import setup_logger
from src.database import register_user, login_user as db_login_user, get_user_by_username, get_all_users
from src.config import hash_password, is_valid_email, is_strong_password, create_temp_dir, delete_log_dir, delete_temp_dir
from src.preprocess import pdf_to_image_dict
from src.ai import process_image_data
from src.postprocess import create_dataframe, save_dataframe_to_excel
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import os

# Initialize Flask app
app = Flask(__name__)

# Apply ProxyFix to handle reverse proxy setups
app.wsgi_app = ProxyFix(app.wsgi_app)

logger = setup_logger(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY', 'default_secret_key')  # Use environment variable for secret key

@app.before_request
def make_session_permanent():
    session.permanent = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def get_id(self):
        return self.username

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(username):
    user_data, result = get_user_by_username(username)  # Implement this function to get user by username
    if result:
        return User(username=user_data['username'], role=user_data['role'])
    return None

# Home route, requires login
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    delete_temp_dir() # Delete the tempDir directory
    
    role = current_user.role
    if role == 'admin':
        logger.info('Admin home page accessed by user: %s with role: %s', current_user.username, role)
        return redirect(url_for('admin'))
    else:
        logger.info('Home page accessed by user: %s with role: %s', current_user.username, role)
        return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        data = request.form
        if not data:
            flash('No input data provided')
            logger.warning('Login attempt with no input data')
            return redirect(url_for('login'))
        
        if not all(key in data for key in ["username", "password"]):
            flash('Missing required fields')
            logger.warning('Login attempt with missing required fields')
            return redirect(url_for('login'))
        
        password = hash_password(data["password"])
        
        message, result = db_login_user(data["username"], password)
        
        if not result:
            flash(message)
            logger.warning('Login failed for user: %s', data["username"])
            return redirect(url_for('login'))
        else:
            user = User(username=message["username"], role=message['role'])
            login_user(user)
            logger.info('User logged in: %s', data["username"])
            return redirect(url_for('home'))
        
    logger.info('Login page accessed')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        if not data:
            flash('No input data provided')
            logger.warning('Registration attempt with no input data')
            return redirect(url_for('register'))
        
        if not all(key in data for key in ["username", "name", "email", "password"]):
            flash('Missing required fields')
            logger.warning('Registration attempt with missing required fields')
            return redirect(url_for('register'))
        
        if not is_valid_email(data["email"]):
            flash('Invalid email address')
            logger.warning('Registration attempt with invalid email: %s', data["email"])
            return redirect(url_for('register'))
        
        if not is_strong_password(data["password"]):
            flash('Password is not strong enough')
            logger.warning('Registration attempt with weak password')
            return redirect(url_for('register'))
        
        password = hash_password(data["password"])
        
        message, result = register_user(data["username"], data["name"], data["email"], password)
        
        if not result:
            flash(message)
            logger.warning('Registration failed for user: %s', data["username"])
            return redirect(url_for('register'))
        else:
            flash('Registration successful, please log in.')
            logger.info('User registered: %s', data["username"])
            return redirect(url_for('login'))

    logger.info('Registration page accessed')
    return render_template('login.html')

# Logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logger.info('User logged out: %s', current_user.username)
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Admin view to see all users
@app.route('/admin', methods=['GET'])
@login_required
def admin():
    if current_user.role != 'admin':
        logger.warning('Unauthorized access to admin page by user: %s', current_user.username)
        return redirect(url_for('home'))
    
    users, result = get_all_users()
    if not result:
        flash(users)
        logger.error('Error fetching users: %s', users)
        return redirect(url_for('home'))
    
    logger.info('Admin page accessed by user: %s', current_user.username)
    return render_template('admin.html', users=users)

# Users view for non-admin users
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    try:
        if current_user.role == 'admin':
            logger.warning('Unauthorized access to user page by admin: %s', current_user.username)
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            if 'pdf_file' not in request.files:
                flash('No file part')
                logger.error('No file part in the request')
                return redirect(request.url)
            
            file = request.files['pdf_file']
            
            if file.filename == '':
                flash('No selected file')
                logger.error('No selected file')
                return redirect(request.url)
            
            if file and file.filename.endswith('.pdf'):
                temp_dir = create_temp_dir()
                
                if temp_dir is None:
                    logger.error('Error creating temporary directory')
                    flash('Could not create temporary directory')
                    return redirect(request.url)
                
                filename = secure_filename(file.filename)
                file_path = temp_dir / filename
                file.save(file_path)
                logger.info('PDF file saved to temporary directory')
                flash('PDF file uploaded successfully')
                
                # Process the PDF file
                flash('Processing PDF file...')
                image_dict = pdf_to_image_dict(file_path)
                if image_dict is None:
                    logger.error('Error processing PDF file')
                    flash('Error processing PDF file')
                    return redirect(request.url)
                
                # Call the AI model to process the image data
                flash('Processing extracted data...')
                processed_data = process_image_data(current_user.username, image_dict)
                if processed_data is None:
                    logger.error('Error processing extracted data')
                    flash('Error processing extracted data')
                    return redirect(request.url)
                
                # Create a DataFrame from the processed data
                df = create_dataframe(processed_data)
                if df is None:
                    logger.error('Error creating DataFrame')
                    flash('Error processing extracted data')
                    return redirect(request.url)
                
                # Save the DataFrame to an Excel file
                excel_file = temp_dir / 'extracted_data.xlsx'
                result = save_dataframe_to_excel(df, excel_file)
                if not result:
                    logger.error('Error saving DataFrame to Excel')
                    flash('Error saving extracted data')
                    return redirect(request.url)
                else:
                    logger.info('DataFrame saved to Excel file')
                    flash('Data extracted successfully, download the Excel file below')
                    return redirect(url_for('download'))
                    
                    # output_file = 'extracted_data.xlsx'
                    # return send_from_directory(temp_dir, output_file, as_attachment=True)
                    
            else:
                logger.error('Invalid file type')
                flash('Invalid file type, please upload a PDF file')
                return redirect(request.url)
        
        logger.info('User page accessed by user: %s', current_user.username)
        return render_template('index.html')
    except Exception as e:
        logger.error('Error processing user request: %s', str(e))
        flash('Error processing user request')
        return redirect(url_for('home'))
    
# Download route
@app.route('/download', methods=['GET'])
@login_required
def download():
    filename = request.args.get('filename')
    if filename:
        return redirect(url_for('download_file', filename=filename))
    return render_template('download.html', file='extracted_data.xlsx')

# Download button route
@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    try:
        return send_from_directory('tempDir', filename, as_attachment=True)
    except Exception as e:
        logger.error('Error downloading file: %s', str(e))
        flash('Error downloading file')
        return redirect(url_for('home'))

# Run the app
if __name__ == '__main__':
    logger.info('Starting Flask app')
    delete_log_dir() # Delete the logs directory
    
    # For local development
    # app.run(host='0.0.0.0', port=5000)
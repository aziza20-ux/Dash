from flask import Blueprint, request, g, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .manage_db import inserting_in_database
from .parser import parser # The new parser
from .middleware import login_required

# Create a Blueprint for this functionality
upload_bp = Blueprint('upload', __name__)

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'xml'}

def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('dashboard.dashboard'))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(url_for('dashboard.dashboard'))

        if file and allowed_file(file.filename):
            try:
                user_id = g.user_id
                
                # Pass the FileStorage object directly to the parser
                parsed_data = parser(file)
                
                if parsed_data:
                    inserting_in_database(parsed_data, user_id)
                    flash('File uploaded and data processed successfully!', 'success')
                else:
                    flash('Failed to process the XML file. Please check its format.', 'danger')
            except Exception as e:
                flash(f'An unexpected error occurred: {e}', 'danger')
        else:
            flash('Invalid file type. Only XML files are allowed.', 'danger')

    return redirect(url_for('dashboard.dashboard'))
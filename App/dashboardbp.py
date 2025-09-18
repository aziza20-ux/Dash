from flask import Blueprint, render_template,request,g,url_for,flash,redirect
from .middleware import login_required
from .details import fetch_filtered_tra_details
from .details import fetch_tra_details
from .parser import parser
from .manage_db import inserting_in_database
from .dashboard import (
    get_most_used_transaction_type,
    get_total_amount,
    get_total_transactions
)

dashboardbp = Blueprint('dashboard', __name__, template_folder='templates')

@dashboardbp.route('/api/dashboard')
@login_required
def dashboard():
    user_id = g.user_id
    total = get_total_amount(user_id=user_id)
    tran = get_total_transactions(user_id=user_id)
    type= get_most_used_transaction_type(user_id=user_id) 
    most = type['transaction_type'] if type else "N/A"
    return render_template('dashboard.html', total=total, tran=tran, most=most)


@dashboardbp.route('/api/transactions', methods=['GET', 'POST'])
def transaction():
   # data = {}
    user_id = g.user_id

    if request.method == 'POST':
        start_date = request.form.get('startdate')
        end_date = request.form.get('enddate')
        transaction_type = request.form.get('filterbytype')

        # Call the filtering function with the form data
        data = fetch_filtered_tra_details(
            user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
    else: # This handles the initial GET request
        # Fetch all transactions for the default view
        data = fetch_tra_details(user_id=user_id)
    
    # Pass the data to the template. The variable name is now consistent.
    return render_template('transactions.html', data=data)
def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['xml']
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboardbp.route('/upload', methods=['POST'])
@login_required  # Ensure only logged-in users can access this page
def upload_file():
    """Handle file uploads, parse data, and insert into the database."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard.dashboard'))

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty file
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard.dashboard'))

    # Process the file if it's a valid type
    if file and allowed_file(file.filename):
        try:
            # The g object is available here because the request context is active.
            user_id = g.user_id
            
            # Parse the uploaded XML file
            parsed_data = parser(file)
            
            # Insert the parsed data into the database, linking it to the user_id
            inserting_in_database(parsed_data, user_id)
            
            flash('File uploaded and data processed successfully!')
            # Redirect to the dashboard after a successful upload
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            # Handle any errors during parsing or database insertion
            flash(f'An error occurred: {e}')
            return redirect(url_for('dashboard.dashboard'))
    else:
        flash('Invalid file type. Only XML files are allowed.')
        return redirect(url_for('dashboard.dashboard'))

@dashboardbp.route('/api/visuals')
@login_required
def visuals():
    return render_template('visuals.html')
@dashboardbp.route('/api/contactus')
@login_required
def contactus():
    return render_template('contactus.html')
#
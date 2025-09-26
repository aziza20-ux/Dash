from flask import Blueprint, render_template, request, g, url_for, flash, redirect
from .middleware import login_required
from .details import fetch_filtered_tra_details, fetch_tra_details
from .parser import parser
from .manage_db import inserting_in_database
from .dashboard import (
    get_most_used_transaction_type,
    get_total_amount,
    get_total_transactions,
    get_user_id_for_query, # <-- Now imported from dashboard.py
)

dashboardbp = Blueprint('dashboard', __name__, template_folder='templates')

# Removed: get_user_id_for_query definition (now in dashboard.py)

@dashboardbp.route('/api/dashboard')
@login_required
def dashboard():
    logged_in_user_id = g.user_id
    # Use the shared logic
    user_id_to_query = get_user_id_for_query(logged_in_user_id)
    
    total = get_total_amount(user_id=user_id_to_query)
    tran = get_total_transactions(user_id=user_id_to_query)
    type_data = get_most_used_transaction_type(user_id=user_id_to_query) 
    
    most = type_data['transaction_type'] if type_data else "N/A"
    
    return render_template('dashboard.html', total=total, tran=tran, most=most)


@dashboardbp.route('/api/transactions', methods=['GET', 'POST'])
@login_required 
def transaction():
    logged_in_user_id = g.user_id
    # Use the shared logic
    user_id_to_query = get_user_id_for_query(logged_in_user_id)

    if request.method == 'POST':
        start_date = request.form.get('startdate')
        end_date = request.form.get('enddate')
        transaction_type = request.form.get('filterbytype')

        data = fetch_filtered_tra_details(
            user_id=user_id_to_query,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
    else:
        data = fetch_tra_details(user_id=user_id_to_query)
    
    return render_template('transactions.html', data=data)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['xml']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dashboardbp.route('/upload', methods=['POST'])
@login_required 
def upload_file():
    """Handle file uploads, parse data, and insert into the database."""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard.dashboard'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard.dashboard'))

    if file and allowed_file(file.filename):
        try:
            user_id = g.user_id
            # Assuming parser and inserting_in_database are correctly imported/defined elsewhere
            parsed_data = parser(file)
            inserting_in_database(parsed_data, user_id)
            
            flash('File uploaded and data processed successfully!')
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
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
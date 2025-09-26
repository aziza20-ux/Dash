from flask import Blueprint, jsonify, g
from .middleware import login_required
from .details import fetch_tra_details

from .dashboard import (
    fetch_transactions,
    get_average_transaction_amount,
    get_transaction_distribution,
    get_monthly_transaction_trends,
    get_transaction_amount_by_type,
    get_transaction_volume_by_type,
    get_user_id_for_query, # <-- CRITICAL: Imported shared user ID logic
)
chart_bp = Blueprint('chart',__name__, url_prefix='/charts')


@chart_bp.route('/api/monthly_trends')
@login_required
def monthly_trends():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    all_data = fetch_transactions(user_id=user_id_to_query)
    labels, data = get_monthly_transaction_trends(all_data)
    return jsonify({'labels':labels,'data':data})

@chart_bp.route('/api/volume_type')
@login_required
def volume_type():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    all_data = fetch_transactions(user_id=user_id_to_query)
    labels, data = get_transaction_volume_by_type(all_data)
    return jsonify({'labels':labels,'data':data})

@chart_bp.route('/api/amount_type')
@login_required
def amount_type():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    all_data = fetch_transactions(user_id=user_id_to_query)
    labels, data = get_transaction_amount_by_type(all_data)
    return jsonify({'labels':labels,'data':data})

@chart_bp.route('/api/transaction_amount')
@login_required
def transaction_amount():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    all_data = fetch_transactions(user_id=user_id_to_query)
    labels, data = get_average_transaction_amount(all_data)
    return jsonify({'labels':labels,'data':data})

@chart_bp.route('/api/transaction_distribution')
@login_required
def transaction_destribution():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    all_data = fetch_transactions(user_id=user_id_to_query)
    labels, data = get_transaction_distribution(all_data)
    return jsonify({'labels':labels,'data':data})

@chart_bp.route('/api/details')
@login_required
def details():
    user_id_to_query = get_user_id_for_query(g.user_id) # Use shared logic
    data = fetch_tra_details(user_id=user_id_to_query)
    return jsonify(data)
from flask import Blueprint, request, jsonify
import requests
import os

integration_bp = Blueprint('integration', __name__)

# --- Odoo Integration ---
ODOO_URL = os.environ.get('ODOO_URL', 'https://your-odoo-instance.com')
ODOO_DB = os.environ.get('ODOO_DB', 'your-db-name')
ODOO_USERNAME = os.environ.get('ODOO_USERNAME', 'your-username')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD', 'your-password')

def get_odoo_uid():
    """Authenticate with Odoo and get user ID."""
    url = f"{ODOO_URL}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}]
        },
        "id": 1
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json().get('result')

@integration_bp.route('/odoo/sync', methods=['POST'])
def sync_to_odoo():
    """Sync a deal to Odoo as a CRM lead."""
    data = request.get_json()
    deal_id = data.get('deal_id')

    if not deal_id:
        return jsonify({'error': 'Deal ID is required'}), 400

    # In a real application, you would fetch the deal details from your database
    # For this example, we'll use dummy data
    deal = {
        'customer_company_name': 'Test Customer',
        'customer_spoc': 'John Doe',
        'customer_email': 'john.doe@test.com',
        'revenue_arr_estimation': 50000
    }

    try:
        uid = get_odoo_uid()
        if not uid:
            return jsonify({'error': 'Odoo authentication failed'}), 500

        url = f"{ODOO_URL}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [ODOO_DB, uid, ODOO_PASSWORD, 'crm.lead', 'create', [{
                    'name': f"Deal from Partner Portal: {deal['customer_company_name']}",
                    'partner_name': deal['customer_company_name'],
                    'contact_name': deal['customer_spoc'],
                    'email_from': deal['customer_email'],
                    'expected_revenue': deal['revenue_arr_estimation']
                }]]
            },
            "id": 2
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json().get('result')

        if result:
            return jsonify({'message': 'Deal synced to Odoo successfully', 'odoo_lead_id': result}), 200
        else:
            return jsonify({'error': 'Failed to create lead in Odoo', 'details': response.json()}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Odoo connection error: {e}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- HubSpot Integration ---
HUBSPOT_API_KEY = os.environ.get('HUBSPOT_API_KEY', 'your-hubspot-api-key')

@integration_bp.route('/hubspot/sync', methods=['POST'])
def sync_to_hubspot():
    """Sync a deal to HubSpot as a deal."""
    data = request.get_json()
    deal_id = data.get('deal_id')

    if not deal_id:
        return jsonify({'error': 'Deal ID is required'}), 400

    # Dummy deal data
    deal = {
        'customer_company_name': 'Test Customer',
        'revenue_arr_estimation': 50000,
        'status': 'Open'
    }

    try:
        url = "https://api.hubapi.com/crm/v3/objects/deals"
        headers = {
            'Authorization': f'Bearer {HUBSPOT_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            "properties": {
                "dealname": f"Deal from Partner Portal: {deal['customer_company_name']}",
                "amount": str(deal['revenue_arr_estimation']),
                "dealstage": "appointmentscheduled" # Example stage
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return jsonify({'message': 'Deal synced to HubSpot successfully', 'hubspot_deal_id': result['id']}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"HubSpot connection error: {e}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


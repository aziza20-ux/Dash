import re
import xml.etree.ElementTree
from datetime import datetime
import io

def parser(xml_data_stream):
    """
    Parses an XML data stream and categorizes transactions.
    
    Args:
        xml_data_stream: A file-like object containing the XML data.
    """
    categorized_type = {
        'Bank_Transfers': [],
        'Withdrawals_from_Agents': [],
        'Transactions_Initiated_by_Third_Parties': [],
        'Bundle_Purchases': [],
        'Cash_Power_Bill_Payments': [],
        'Airtime_Bill_Payments': [],
        'Bank_Deposits': [],
        'Transfers_to_Mobile_Numbers': [],
        'Payments_to_Code_Holders': [],
        'Incoming_Money': [],
        'unprocessed_data': []
    }

    try:
        tree = xml.etree.ElementTree.parse(xml_data_stream)
        root = tree.getroot()

        for sms_tag in root.findall('sms'):
            sms_body = sms_tag.get('body')
            transaction_date = sms_tag.get('readable_date')
            
            try:
                formated_date = datetime.strptime(transaction_date, '%d %b %Y %I:%M:%S %p')
            except ValueError:
                formated_date = None
            
            single_transaction = {
                'date': formated_date,
                'amount': None,
                'fee': None,
                'new_balance': None,
                'tra_type': 'unprocessed_data',
                'sender_name': None,
                'receiver_name': None,
                'transaction_id': None
            }
            
            # General matches
            transaction_id_match = re.search(r'TxId: (\d+)', sms_body)
            if transaction_id_match:
                single_transaction['transaction_id'] = transaction_id_match.group(1)

            amount_match = re.search(r'(\d{1,3}(?:,\d{3})*) RWF', sms_body)
            if amount_match:
                single_transaction['amount'] = amount_match.group(1).replace(",", "")

            fee_match = re.search(r'Fee was:?\s*(.*?) RWF', sms_body)
            if fee_match:
                single_transaction['fee'] = fee_match.group(1).replace(',', '')

            balance_match = re.search(r'(Your\s+)?new\s+balance\s*:\s*(\d+) RWF', sms_body, re.IGNORECASE)
            if balance_match:
                single_transaction['new_balance'] = balance_match.group(2).replace(',', '')
            
            # Specific category matches
            is_categorized = False

            # Incoming Money
            match_found = re.search(r'You have received (.*?) RWF from (.*?) \((\*?\d{9,15})\) on your mobile money account', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Incoming_Money'
                single_transaction['sender_name'] = match_found.group(2).strip()
                single_transaction['amount'] = match_found.group(1).replace(",", "")
                single_transaction['sender_number'] = match_found.group(3).strip()
                is_categorized = True

            # Bank Deposits
            match_found = re.search(r'A bank deposit of (.*?) RWF has been added to your mobile money account', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Bank_Deposits'
                single_transaction['amount'] = match_found.group(1).replace(",", "")
                is_categorized = True
            
            # Payments to Mobile Numbers
            match_found = re.search(r'\*(\d+)\*S\*(\d+)\sRWF transferred to ([A-Z][a-z]+(?: [A-Z][a-z]+)) \((\d{9,15})\) from (\d+)', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Transfers_to_Mobile_Numbers'
                single_transaction['amount'] = match_found.group(2).replace(",", "")
                single_transaction['receiver_name'] = match_found.group(3).strip()
                single_transaction['receiver_number'] = match_found.group(4)
                is_categorized = True

            # Payments to Code Holders
            match_found = re.search(r'TxId: (\d+)\.\s*Your payment of (.*?) RWF to\s*([A-Z][a-z]+(?: [A-Z][a-z]+)*)(?:\s+\d+)?\s+has been completed', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Payments_to_Code_Holders'
                single_transaction['receiver_name'] = match_found.group(3).strip()
                single_transaction['amount'] = match_found.group(2).replace(",", "")
                is_categorized = True

            # Payments Initiated by Third Parties
            match_found = re.search(r'A transaction of (.*?) RWF by (.*?) on your MOMO account was successfully completed', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Transactions_Initiated_by_Third_Parties'
                single_transaction['third_party_name'] = match_found.group(2).strip()
                single_transaction['amount'] = match_found.group(1).replace(",", "")
                is_categorized = True

            # Withdrawals from Agents
            match_found = re.search(r'You Abebe Chala CHEBUDIE \(.*?036\) have via agent: Agent ([A-Z][a-z]+(?: [A-Z][a-z]+)*) \((\d+)\), withdrawn (.*?) RWF from your mobile money ', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Withdrawals_from_Agents'
                single_transaction['agent_number'] = match_found.group(2)
                single_transaction['amount'] = match_found.group(3).replace(",", "")
                is_categorized = True

            # Cash Power Payments
            match_found = re.search(r'Your payment of (.*?) RWF to MTN Cash Power', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Cash_Power_Bill_Payments'
                single_transaction['amount'] = match_found.group(1).replace(",", "")
                is_categorized = True

            # Airtime Payments
            match_found = re.search(r'(\d+)\*TxId:(\d+)\*S\*Your payment of (\d{1,3}(?:,\d{3})*) RWF to Airtime with token has been completed', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Airtime_Bill_Payments'
                single_transaction['transaction_id'] = match_found.group(2)
                single_transaction['amount'] = match_found.group(3).replace(",", "")
                is_categorized = True

            # Bundles Payments
            match_found = re.search(r'(\d+)\*TxId:(\d+)\*S\*Your payment of (\d{1,3}(?:,\d{3})*) RWF to Bundles and Packs with token has been completed(?:.*)?', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Bundle_Purchases'
                single_transaction['amount'] = match_found.group(3).replace(",", "")
                single_transaction['transaction_id'] = match_found.group(2)
                is_categorized = True

            # Bank Transfer
            match_found = re.search(r'A bank Transfer of (.*?)', sms_body)
            if match_found:
                single_transaction['tra_type'] = 'Bank_Transfers'
                single_transaction['amount'] = float(match_found.group(1).replace(",", ""))
                is_categorized = True

            # Store the categorized transaction
            categorized_type[single_transaction['tra_type']].append(single_transaction)
            
    except xml.etree.ElementTree.ParseError as e:
        print(f"Error occurred while parsing the XML file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during parsing: {e}")
        return None
    
    return categorized_type
import requests

def send_sms(api_key, message, recipients, sender_id="BelovedChurch"):
    """
    Send SMS via Celcom Africa API.

    :param api_key: Your Celcom API key / Partner ID
    :param message: Text message to send
    :param recipients: List of phone numbers as strings
    :param sender_id: Registered Sender ID (default: BelovedChurch)
    :return: dict response from API
    """
    url = "https://sms.celcomafrica.com/api/services/send/"
    
    payload = {
        "partnerID": api_key,
        "message": message,
        "shortcode": sender_id,
        "mobile": ",".join(recipients)
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()  # raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        # Return error in a structured way
        return {"status": "error", "message": str(e)}

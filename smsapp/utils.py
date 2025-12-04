from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


# ============================
# SEND SMS
# ============================
def send_sms(message, recipients, sender_id="BelovedChurch"):
    """
    Send SMS via Celcom Africa API.
    :param message: Text message to send.
    :param recipients: List of phone numbers (list or comma-separated).
    :param sender_id: Sender ID registered in Celcom.
    :return: dict response from API.
    """

    # --- Validate message ---
    if not message or not str(message).strip():
        return {"status": "error", "message": "Message cannot be empty."}

    # --- Normalize recipients ---
    if isinstance(recipients, (list, tuple)):
        recipients = [str(r).strip() for r in recipients if r and str(r).strip()]
        mobile = ",".join(recipients)
    else:
        mobile = str(recipients).strip()

    if not mobile:
        return {"status": "error", "message": "No valid recipients provided."}

    payload = {
        "partnerID": settings.CELCOM_PARTNER_ID,
        "apikey": settings.CELCOM_API_KEY,
        "mobile": mobile,
        "shortcode": sender_id,
        "message": message,
        "pass_type": "plain"
    }

    logger.info(f"Sending SMS to {mobile} via Celcom API...")
    logger.debug(f"Payload: {payload}")

    try:
        response = requests.post(settings.CELCOM_SMS_URL, json=payload, timeout=15)

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        if response.status_code >= 400:
            logger.error(f"Celcom returned HTTP error {response.status_code}: {data}")
            return {"status": "error", "http_status": response.status_code, "response": data}

        logger.info(f"Celcom SMS Response: {data}")

        return {"status": "ok", "response": data}

    except requests.exceptions.RequestException as e:
        logger.error(f"Exception sending SMS: {str(e)}")
        return {"status": "error", "message": str(e)}


# ============================
# GET BALANCE
# ============================
def get_celcom_balance():
    payload = {
        "partnerID": settings.CELCOM_PARTNER_ID,
        "apikey": settings.CELCOM_API_KEY
    }

    logger.info("Checking Celcom Balance...")

    try:
        response = requests.post(settings.CELCOM_BALANCE_URL, json=payload, timeout=10)

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        if response.status_code >= 400:
            logger.error(f"Balance API error {response.status_code}: {data}")
            return {"status": "error", "response": data}

        logger.info(f"Celcom Balance Response: {data}")

        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Exception fetching balance: {str(e)}")
        return {"status": "error", "message": str(e)}

import random
import string
import datetime
import settings
from flask_mail import Message
from database import MongoAPI


def unique_email(email_id):
    """
    :param email_id: <str> email id of the requested user
    :return <bool> whether email id exists
    """
    obj = MongoAPI({"database": "C3AM",
                    "collection": "user_details"})
    documents = obj.read()
    for doc in documents:
        if doc["email"] == email_id:
            return {"unique": False,
                    "instance": doc}
    return {"unique": True}


def device_registration(email_id, device_details):
    """
    :param email_id: <str> email id of the requested user
    :param device_details: <json> Document to be inserted
    :return <json> status of insertion execution
    """
    device_obj = MongoAPI({"database": "RegisteredDevices",
                           "collection": email_id})
    response = device_obj.write({"document": device_details})
    return response


def generate_totp(email_id):
    """
    :param email_id: <str> email id of the requested user
    :return <str> OTP sent to the provided mail id
    """
    totp = ''.join([random.choice(string.digits) for n in range(6)])
    totp_obj = MongoAPI({"database": "C3AM",
                         "collection": "totp"})

    # Delete existing entries of the particular email id
    documents = totp_obj.read()
    for doc in documents:
        if doc["email"] == email_id:
            totp_obj.delete({"document": doc})

    # Write the generated totp into the Mongo DB
    response = totp_obj.write({"document": {"email": email_id, "totp": totp, "datetime": datetime.datetime.now()}})
    return {"status": response["status"],
            "totp": totp}


def totp_mail(email_id, content):
    """
    :param email_id: <str> email id of the requested user
    :param content: <json> contains the mail subject and body
    :return <object> Message object which should be mailed to the user
    """
    totp_res = generate_totp(email_id)
    if totp_res["status"] == "success":
        msg = Message(content["subject"], sender=settings.MAIL_USERNAME, recipients=[email_id])
        msg.body = content["body"] + totp_res["totp"]
        return {"status": "success",
                "data": msg}
    return totp_res

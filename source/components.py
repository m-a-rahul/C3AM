import random
import string
import datetime
import settings
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from passlib.hash import sha256_crypt
from flask_mail import Message
from database import MongoAPI


def decryptAES(enc):
    """
    :param enc: <str> encrypted cipher text
    :return <str> decrypted plain text
    """
    enc = base64.b64decode(enc)
    cipher = AES.new(settings.AES_KEY.encode('utf-8'), AES.MODE_ECB)
    return unpad(cipher.decrypt(enc), 16)


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


def is_device_registered(email_id, device_details):
    """
    :param email_id: <str> email id of the requested user
    :param device_details: <json> Document to be inserted
    :return <json> status of insertion execution
    """
    device_obj = MongoAPI({"database": "RegisteredDevices",
                           "collection": email_id})
    response = {"status": "failure"}
    documents = device_obj.read()
    for doc in documents:
        if sha256_crypt.verify(str(device_details), doc["device_hash"]):
            response = {"status": "success"}
    return response


def device_registration(email_id, device_details):
    """
    :param email_id: <str> email id of the requested user
    :param device_details: <json> Document to be inserted
    :return <json> status of insertion execution
    """
    device_obj = MongoAPI({"database": "RegisteredDevices",
                           "collection": email_id})
    hashed_device_details = sha256_crypt.encrypt(str(device_details))
    response = device_obj.write({"document": {"device_hash": hashed_device_details}})
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
    hashed_totp = sha256_crypt.encrypt(totp)
    # Write the generated totp into the Mongo DB
    response = totp_obj.write(
        {"document": {"email": email_id, "totp": hashed_totp, "datetime": datetime.datetime.now()}})
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


def verify_totp(data):
    """
    :param data: <json> JSON containing email and totp
    :return <json> JSON containing status along with the corresponding message
    """
    totp_obj = MongoAPI({"database": "C3AM", "collection": "totp"})
    documents = totp_obj.read()
    for doc in documents:
        if doc["email"] == data["email"] and sha256_crypt.verify(data["totp"], doc["totp"]):
            current_time = datetime.datetime.now()
            time_difference = current_time - doc["datetime"]
            time_delay = divmod(time_difference.days * (24 * 60 * 60) + time_difference.seconds, 60)
            in_secs = time_delay[0] * 60 + time_delay[1]
            if in_secs < 300:
                totp_obj.delete({"document": doc})
                return {"status": "success",
                        "message": "Authentication successful"}
    return {"status": "failure",
            "message": "Authentication unsuccessful"}

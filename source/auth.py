from database import MongoAPI
from passlib.handlers.sha2_crypt import sha256_crypt
from flask_jwt_extended import create_access_token, get_jwt


def authenticate(email_id, device_details):
    """
    :param email_id: <str> Email id of the requested user
    :param device_details: <str> JSON containing the device details for extra authentication
    :return: <json> Status of authentication
    """
    user_obj = MongoAPI({"database": "C3AM",
                         "collection": "user_details"})
    documents = user_obj.read()
    for doc in documents:
        if doc["email"] == email_id:
            session = {
                "username": doc["username"],
                "email": doc["email"],
                "device_details": sha256_crypt.encrypt(str(device_details)),
            }
            access_token = create_access_token(doc["username"], additional_claims=session)
            return {"status": "success", "access_token": access_token}
    return {"status": "failure"}


def current_user(device_details):
    """
    :return: <json> Current user details
    """
    session = get_jwt()
    if "email" in session and sha256_crypt.verify(str(device_details), session["device_details"]):
        return {"status": "success",
                "data": {"username": session["username"],
                         "email": session["email"]}}

    return {"status": "failure"}

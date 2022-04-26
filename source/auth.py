from database import MongoAPI
from flask_jwt_extended import create_access_token, get_jwt


def authenticate(email_id):
    """
    :param email_id: <str> Email id of the requested user
    :return: <json> Status of authentication
    """
    user_obj = MongoAPI({"database": "C3AM",
                         "collection": "user_details"})
    documents = user_obj.read()
    for doc in documents:
        if doc["email"] == email_id:
            session = {
                "username": doc["username"],
                "email": doc["email"]
            }
            access_token = create_access_token(doc["username"], additional_claims=session)
            return {"status": "success", "access_token": access_token}
    return {"status": "failure"}


def current_user():
    """
    :return: <json> Current user details
    """
    session = get_jwt()
    if "email" in session:
        return {"status": "success",
                "data": {"username": session["username"],
                         "email": session["email"]}}

    return {"status": "failure"}

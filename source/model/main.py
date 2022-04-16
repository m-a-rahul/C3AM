from database import MongoAPI


def password_less_login(data):
    password_less_obj = MongoAPI({"database": "PasswordLess",
                                  "collection": data["email"]})
    signatures = []
    documents = password_less_obj.read()
    for doc in documents:
        signatures.append(doc["signature"])
    return {"status": "success"}


def password_less_register(data):
    password_less_obj = MongoAPI({"database": "PasswordLess",
                                  "collection": data["email"]})
    response = password_less_obj.write({"document": {"signature": data["image"]}})
    return response

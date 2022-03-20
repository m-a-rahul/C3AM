import settings
from pymongo import MongoClient


class MongoAPI:
    """
    :param data: <json> Contained parameters -> database, collection names
    """

    def __init__(self, data):
        self.client = MongoClient(settings.MONGO_CLIENT_URL)

        database = data["database"]
        collection = data['collection']
        cursor = self.client[database]
        self.collection = cursor[collection]

    def read(self):
        """
        :return: <json> status, List of retrieved documents
        """
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def write(self, data):
        """
        :param data: <json> Contains the document to be inserted
        :return: <json> Status of write execution
        """
        new_document = data['document']
        response = self.collection.insert_one(new_document)
        output = {'status': 'success' if response.acknowledged else "failure"}
        return output

    def update(self, inst, updated_content):
        """
        :param inst: <json> Contains the document which should be updated
        :param updated_content: <json> Contains the updated content
        :return: <json> Status of update execution
        """
        updated_data = {"$set": updated_content}
        response = self.collection.update_one(inst, updated_data)
        output = {'status': 'success' if response.modified_count > 0 else "failure"}
        return output

    def delete(self, data):
        """
        :param data: <json> Contains the document to be deleted
        :return: <json> Status of update execution
        """
        inst = data['document']
        response = self.collection.delete_one(inst)
        output = {'status': 'success' if response.deleted_count > 0 else "failure"}
        return output

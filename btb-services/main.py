"""GCP HTTP Cloud Function Example."""
# -*- coding: utf-8 -*-

import json
import datetime
from google.cloud import firestore

db = firestore.Client()
users = db.collection("users")


def analysis(request):
    """GCP HTTP Cloud Function Example.

    Args:
        request (flask.Request)

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/0.12/api/#flask.Flask.make_response>.

    """
    userId = request.path.rsplit("/", 1)[1]
    print(f"Running analysis for user: {userId}")
    print(users.document(userId).collection("transactions").get())
    current_time = datetime.datetime.now().time()
    body = {
        "message": "Received a {} request at {}".format(
            request.method, str(current_time)
        )
    }

    response = {"statusCode": 200, "body": body}

    return json.dumps(response, indent=4)

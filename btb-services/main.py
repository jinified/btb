"""GCP HTTP Cloud Function Example."""
# -*- coding: utf-8 -*-

import json
import pandas as pd
import re
from google.cloud import firestore
from datetime import datetime

db = firestore.Client()
users = db.collection("users")


def saving(request):
    userId = request.path.rsplit("/", 1)[1]
    print(f"Getting saving for {userId}")
    response = {
        "responseCode": "SUCCESS",
        "responseMessage": "Success",
        "data": {
            "actual": [10, 23, 30, 45, 52, 60, 78, 85, 92],
            "expected": [10, 20, 26, 31, 40, 47, 50, 56, 60],
        },
    }
    return json.dumps(response, indent=4)


def transaction(request):
    categoryId, month, userId = re.match(
        "/(\w+)/(\d+-\d+)/(\w+)", request.path
    ).groups()
    print(
        f"Running analysis for user: {userId} for  category {categoryId} for month {month}"
    )
    response = {
        "responseCode": "SUCCESS",
        "responseMessage": "Success",
        "data": [
            {
                "company": "Mcdonald",
                "details": "fried chicken",
                "date": "2018-05-01",
                "value": "7.99",
            },
            {
                "company": "KFC",
                "details": "Zinger",
                "date": "2018-05-02",
                "value": "125.9o",
            },
            {
                "details": "Wan Tan Mee",
                "company": "Kopitiam Ah Seng",
                "date": "2018-05-03",
                "value": "52",
            },
        ],
    }
    return json.dumps(response, indent=4)


def analysis(request):
    """GCP HTTP Cloud Function Example.

    Args:
        request (flask.Request)

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/0.12/api/#flask.Flask.make_response>.

    """
    mode, userId = re.match("/(\w+)/(\w+)", request.path).groups()
    print(f"Running analysis for user: {userId} with mode {mode}")

    if mode == "month":
        response = {
            "responseCode": "SUCCESS",
            "responseMessage": "Success",
            "data": [
                {
                    "label": "05-18",
                    "sum": 5120,
                    "categories": [
                        {"categoryId": "food", "value": 1000},
                        {"categoryId": "bills", "value": 300},
                        {"categoryId": "loans", "value": 400},
                        {"categoryId": "entertainment", "value": 300},
                        {"categoryId": "shopping", "value": 150},
                        {"categoryId": "petrol", "value": 700},
                        {"categoryId": "gifts", "value": 70},
                        {"categoryId": "health", "value": 800},
                        {"categoryId": "education", "value": 1400},
                    ],
                },
                {
                    "label": "06-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 100},
                        {"categoryId": "bills", "value": 30},
                        {"categoryId": "loans", "value": 20},
                        {"categoryId": "entertainment", "value": 150},
                        {"categoryId": "shopping", "value": 230},
                        {"categoryId": "petrol", "value": 80},
                        {"categoryId": "gifts", "value": 200},
                        {"categoryId": "health", "value": 25},
                        {"categoryId": "education", "value": 1300},
                    ],
                },
                {
                    "label": "07-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 900},
                        {"categoryId": "bills", "value": 340},
                        {"categoryId": "loans", "value": 250},
                        {"categoryId": "entertainment", "value": 10},
                        {"categoryId": "shopping", "value": 240},
                        {"categoryId": "petrol", "value": 160},
                        {"categoryId": "gifts", "value": 30},
                        {"categoryId": "health", "value": 475},
                        {"categoryId": "education", "value": 250},
                    ],
                },
                {
                    "label": "08-18",
                    "sum": 3030,
                    "categories": [
                        {"categoryId": "food", "value": 1100},
                        {"categoryId": "bills", "value": 540},
                        {"categoryId": "loans", "value": 260},
                        {"categoryId": "entertainment", "value": 50},
                        {"categoryId": "shopping", "value": 640},
                        {"categoryId": "petrol", "value": 250},
                        {"categoryId": "gifts", "value": 0},
                        {"categoryId": "health", "value": 90},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "09-18",
                    "sum": 2195,
                    "categories": [
                        {"categoryId": "food", "value": 600},
                        {"categoryId": "bills", "value": 240},
                        {"categoryId": "loans", "value": 420},
                        {"categoryId": "entertainment", "value": 200},
                        {"categoryId": "shopping", "value": 40},
                        {"categoryId": "petrol", "value": 190},
                        {"categoryId": "gifts", "value": 130},
                        {"categoryId": "health", "value": 275},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "10-18",
                    "sum": 3615,
                    "categories": [
                        {"categoryId": "food", "value": 1200},
                        {"categoryId": "bills", "value": 310},
                        {"categoryId": "loans", "value": 400},
                        {"categoryId": "entertainment", "value": 700},
                        {"categoryId": "shopping", "value": 90},
                        {"categoryId": "petrol", "value": 460},
                        {"categoryId": "gifts", "value": 305},
                        {"categoryId": "health", "value": 100},
                        {"categoryId": "education", "value": 50},
                    ],
                },
                {
                    "label": "11-18",
                    "sum": 3015,
                    "categories": [
                        {"categoryId": "food", "value": 770},
                        {"categoryId": "bills", "value": 450},
                        {"categoryId": "loans", "value": 450},
                        {"categoryId": "entertainment", "value": 280},
                        {"categoryId": "shopping", "value": 200},
                        {"categoryId": "petrol", "value": 100},
                        {"categoryId": "gifts", "value": 390},
                        {"categoryId": "health", "value": 85},
                        {"categoryId": "education", "value": 290},
                    ],
                },
                {
                    "label": "12-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 900},
                        {"categoryId": "bills", "value": 340},
                        {"categoryId": "loans", "value": 250},
                        {"categoryId": "entertainment", "value": 10},
                        {"categoryId": "shopping", "value": 240},
                        {"categoryId": "petrol", "value": 160},
                        {"categoryId": "gifts", "value": 30},
                        {"categoryId": "health", "value": 475},
                        {"categoryId": "education", "value": 250},
                    ],
                },
                {
                    "label": "01-19",
                    "sum": 3030,
                    "categories": [
                        {"categoryId": "food", "value": 1100},
                        {"categoryId": "bills", "value": 540},
                        {"categoryId": "loans", "value": 260},
                        {"categoryId": "entertainment", "value": 50},
                        {"categoryId": "shopping", "value": 640},
                        {"categoryId": "petrol", "value": 250},
                        {"categoryId": "gifts", "value": 0},
                        {"categoryId": "health", "value": 90},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "02-19",
                    "sum": 2195,
                    "categories": [
                        {"categoryId": "food", "value": 600},
                        {"categoryId": "bills", "value": 240},
                        {"categoryId": "loans", "value": 420},
                        {"categoryId": "entertainment", "value": 200},
                        {"categoryId": "shopping", "value": 40},
                        {"categoryId": "petrol", "value": 190},
                        {"categoryId": "gifts", "value": 130},
                        {"categoryId": "health", "value": 275},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "03-19",
                    "sum": 3615,
                    "categories": [
                        {"categoryId": "food", "value": 1200},
                        {"categoryId": "bills", "value": 310},
                        {"categoryId": "loans", "value": 400},
                        {"categoryId": "entertainment", "value": 700},
                        {"categoryId": "shopping", "value": 90},
                        {"categoryId": "petrol", "value": 460},
                        {"categoryId": "gifts", "value": 305},
                        {"categoryId": "health", "value": 100},
                        {"categoryId": "education", "value": 50},
                    ],
                },
                {
                    "label": "04-19",
                    "sum": 3015,
                    "categories": [
                        {"categoryId": "food", "value": 770},
                        {"categoryId": "bills", "value": 450},
                        {"categoryId": "loans", "value": 450},
                        {"categoryId": "entertainment", "value": 280},
                        {"categoryId": "shopping", "value": 200},
                        {"categoryId": "petrol", "value": 100},
                        {"categoryId": "gifts", "value": 390},
                        {"categoryId": "health", "value": 85},
                        {"categoryId": "education", "value": 290},
                    ],
                },
            ],
        }
        return json.dumps(response, indent=4)
    if mode == "week":
        response = {
            "responseCode": "SUCCESS",
            "responseMessage": "Success",
            "data": [
                {
                    "label": "02-05-18",
                    "sum": 512,
                    "categories": [
                        {"categoryId": "food", "value": 100},
                        {"categoryId": "bills", "value": 30},
                        {"categoryId": "loans", "value": 40},
                        {"categoryId": "entertainment", "value": 30},
                        {"categoryId": "shopping", "value": 15},
                        {"categoryId": "petrol", "value": 70},
                        {"categoryId": "gifts", "value": 7},
                        {"categoryId": "health", "value": 80},
                        {"categoryId": "education", "value": 140},
                    ],
                },
                {
                    "label": "09-05-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 100},
                        {"categoryId": "bills", "value": 30},
                        {"categoryId": "loans", "value": 20},
                        {"categoryId": "entertainment", "value": 150},
                        {"categoryId": "shopping", "value": 230},
                        {"categoryId": "petrol", "value": 80},
                        {"categoryId": "gifts", "value": 200},
                        {"categoryId": "health", "value": 25},
                        {"categoryId": "education", "value": 1300},
                    ],
                },
                {
                    "label": "16-05-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 900},
                        {"categoryId": "bills", "value": 340},
                        {"categoryId": "loans", "value": 250},
                        {"categoryId": "entertainment", "value": 10},
                        {"categoryId": "shopping", "value": 240},
                        {"categoryId": "petrol", "value": 160},
                        {"categoryId": "gifts", "value": 30},
                        {"categoryId": "health", "value": 475},
                        {"categoryId": "education", "value": 250},
                    ],
                },
                {
                    "label": "23-05-18",
                    "sum": 5120,
                    "categories": [
                        {"categoryId": "food", "value": 1000},
                        {"categoryId": "bills", "value": 300},
                        {"categoryId": "loans", "value": 400},
                        {"categoryId": "entertainment", "value": 300},
                        {"categoryId": "shopping", "value": 150},
                        {"categoryId": "petrol", "value": 700},
                        {"categoryId": "gifts", "value": 70},
                        {"categoryId": "health", "value": 800},
                        {"categoryId": "education", "value": 1400},
                    ],
                },
                {
                    "label": "30-05-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 100},
                        {"categoryId": "bills", "value": 30},
                        {"categoryId": "loans", "value": 20},
                        {"categoryId": "entertainment", "value": 150},
                        {"categoryId": "shopping", "value": 230},
                        {"categoryId": "petrol", "value": 80},
                        {"categoryId": "gifts", "value": 200},
                        {"categoryId": "health", "value": 25},
                        {"categoryId": "education", "value": 1300},
                    ],
                },
                {
                    "label": "07-06-18",
                    "sum": 2135,
                    "categories": [
                        {"categoryId": "food", "value": 900},
                        {"categoryId": "bills", "value": 340},
                        {"categoryId": "loans", "value": 250},
                        {"categoryId": "entertainment", "value": 10},
                        {"categoryId": "shopping", "value": 240},
                        {"categoryId": "petrol", "value": 160},
                        {"categoryId": "gifts", "value": 30},
                        {"categoryId": "health", "value": 475},
                        {"categoryId": "education", "value": 250},
                    ],
                },
                {
                    "label": "14-06-18",
                    "sum": 3030,
                    "categories": [
                        {"categoryId": "food", "value": 1100},
                        {"categoryId": "bills", "value": 540},
                        {"categoryId": "loans", "value": 260},
                        {"categoryId": "entertainment", "value": 50},
                        {"categoryId": "shopping", "value": 640},
                        {"categoryId": "petrol", "value": 250},
                        {"categoryId": "gifts", "value": 0},
                        {"categoryId": "health", "value": 90},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "21-06-18",
                    "sum": 2195,
                    "categories": [
                        {"categoryId": "food", "value": 600},
                        {"categoryId": "bills", "value": 240},
                        {"categoryId": "loans", "value": 420},
                        {"categoryId": "entertainment", "value": 200},
                        {"categoryId": "shopping", "value": 40},
                        {"categoryId": "petrol", "value": 190},
                        {"categoryId": "gifts", "value": 130},
                        {"categoryId": "health", "value": 275},
                        {"categoryId": "education", "value": 100},
                    ],
                },
                {
                    "label": "28-06-18",
                    "sum": 3615,
                    "categories": [
                        {"categoryId": "food", "value": 1200},
                        {"categoryId": "bills", "value": 310},
                        {"categoryId": "loans", "value": 400},
                        {"categoryId": "entertainment", "value": 700},
                        {"categoryId": "shopping", "value": 90},
                        {"categoryId": "petrol", "value": 460},
                        {"categoryId": "gifts", "value": 305},
                        {"categoryId": "health", "value": 100},
                        {"categoryId": "education", "value": 50},
                    ],
                },
                {
                    "label": "05-07-18",
                    "sum": 3015,
                    "categories": [
                        {"categoryId": "food", "value": 770},
                        {"categoryId": "bills", "value": 450},
                        {"categoryId": "loans", "value": 450},
                        {"categoryId": "entertainment", "value": 280},
                        {"categoryId": "shopping", "value": 200},
                        {"categoryId": "petrol", "value": 100},
                        {"categoryId": "gifts", "value": 390},
                        {"categoryId": "health", "value": 85},
                        {"categoryId": "education", "value": 290},
                    ],
                },
            ],
        }
        return json.dumps(response, indent=4)

    current_time = datetime.now().time()
    body = {
        "message": "Received a {} request at {}".format(
            request.method, str(current_time)
        )
    }

    response = {"statusCode": 200, "body": body}

    return json.dumps(response, indent=4)

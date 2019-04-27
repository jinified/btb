"""GCP HTTP Cloud Function Example."""
# -*- coding: utf-8 -*-

import json
import pandas as pd
import re
from google.cloud import firestore
from datetime import datetime, timedelta
from pyfcm import FCMNotification
import operator
import os
import uuid

API_KEY = "AAAAxNpWUWQ:APA91bGcIaD6-UwlX_rqrAJv1eeOf1-s3d50mK-L_yNvg2AXXJIhHZh1kQnJ9kdCd7ULY3k7oavqWnm7UbcOx3hVvK_EBD6R712IOGAo748M-MO_RrjirmKqoIPSYSE98dcM6r75YKBR"

REG_ID = "e7OMCvddRgE:APA91bHDstR9R5qgcMEZ6bpCSEsgncOJYNGRVW16LjuAonIC-gmAx-A3MdBeH6TCGTeLuwvNBWwCVcaHhv0KeZv8D5MtyYIb13Wh4g3mFN6zc7kC4-uEBlv9O4XD5fFPJEKhjDDBcf-o"

categories = [
    "food",
    "bills",
    "loans",
    "entertainment",
    "shopping",
    "petrol",
    "gifts",
    "health",
    "education",
]

db = firestore.Client()
users = db.collection("users")
push_service = FCMNotification(api_key=API_KEY)


def generateMonthAggregate(monthly_transactions):
    def generateMonthObject(month, spending):
        totalSpending = sum(spending.values())
        categories = [{"categoryId": k, "value": v} for k, v in spending.items()]
        return {"label": month, "sum": totalSpending, "categories": categories}

    return [generateMonthObject(k, v) for k, v in monthly_transactions.items()]


def getTotalSpending(transactions, categoryId=None):
    if categoryId:
        return sum(
            [
                t.to_dict()["value"]
                for t in transactions.where("category", "==", categoryId).get()
            ]
        )
    return sum([t.to_dict()["value"] for t in transactions.get()])


def calculateWiseSavings(transactions):
    maxCat = calcMaxCategory(transactions.get())
    total_maxCat_spending = getTotalSpending(transactions, maxCat)
    return 0.1 * total_maxCat_spending


def calculateEssentialSavings(transactions, discount=[0.004, 0.01]):
    totalSpending = getTotalSpending(transactions)
    initSaving = discount[0] * min(totalSpending, 7000)
    subsequentSaving = (
        discount[1] * (totalSpending - 7000) if totalSpending > 7000 else 0
    )
    return initSaving + subsequentSaving


def plotEssential(transactions, discount=[0.004, 0.1]):
    accValue = 0
    actual_monthly_transactions = {}
    monthly_transactions = {}
    for doc in transactions.get():
        t = doc.to_dict()
        month = t["date"].strftime("%m-%y")
        value = t["value"]
        accValue += value
        if month not in actual_monthly_transactions:
            monthly_transactions[month] = 0
            actual_monthly_transactions[month] = 0
        monthly_transactions[month] += (
            0.996 * value if accValue <= 7000 else 0.99 * value
        )
        actual_monthly_transactions[month] += value
    actual_monthly_transactions = {
        datetime.strptime(date, "%m-%y").strftime("%y-%m"): v
        for date, v in actual_monthly_transactions.items()
    }
    monthly_transactions = {
        datetime.strptime(date, "%m-%y").strftime("%y-%m"): v
        for date, v in monthly_transactions.items()
    }
    actual_monthly_transactions = [
        x[1] for x in sorted(actual_monthly_transactions.items())
    ]
    monthly_transactions = [x[1] for x in sorted(monthly_transactions.items())]
    return {"actual": actual_monthly_transactions, "expected": monthly_transactions}


def plotWise(transactions, maxCat):
    actual_monthly_transactions = {}
    monthly_transactions = {}
    for doc in transactions.get():
        t = doc.to_dict()
        month = t["date"].strftime("%m-%y")
        value = t["value"]
        if month not in actual_monthly_transactions:
            monthly_transactions[month] = 0
            actual_monthly_transactions[month] = 0
        monthly_transactions[month] += value if t["category"] != maxCat else 0.9 * value
        actual_monthly_transactions[month] += value
    actual_monthly_transactions = {
        datetime.strptime(date, "%m-%y").strftime("%y-%m"): v
        for date, v in actual_monthly_transactions.items()
    }
    monthly_transactions = {
        datetime.strptime(date, "%m-%y").strftime("%y-%m"): v
        for date, v in monthly_transactions.items()
    }
    actual_monthly_transactions = [
        x[1] for x in sorted(actual_monthly_transactions.items())
    ]
    monthly_transactions = [x[1] for x in sorted(monthly_transactions.items())]
    return {"actual": actual_monthly_transactions, "expected": monthly_transactions}


def saving(request):
    userId = request.path.rsplit("/", 1)[1]
    print(f"Getting saving for {userId}")
    user_transactions = users.document(userId).collection("transactions")
    scoreWise = calculateWiseSavings(user_transactions)
    scoreEssential = calculateEssentialSavings(user_transactions)
    productId = "wise" if scoreWise >= scoreEssential else "essential"
    data = (
        plotWise(user_transactions, calcMaxCategory(user_transactions.get()))
        if productId == "wise"
        else plotEssential(user_transactions)
    )
    response = {
        "responseCode": "SUCCESS",
        "responseMessage": "Success",
        "data": {"productId": productId, "plot": data}
        # "data": {
        #     "actual": [10, 23, 30, 45, 52, 60, 78, 85, 92],
        #     "expected": [10, 20, 26, 31, 40, 47, 50, 56, 60],
        # },
    }
    return json.dumps(response, indent=4)


def calcMaxCategory(transactions):
    categories = [
        "food",
        "bills",
        "loans",
        "entertainment",
        "shopping",
        "petrol",
        "gifts",
        "health",
        "education",
    ]
    spending = {key: 0 for key in categories}
    for doc in transactions:
        t = doc.to_dict()
        spending[t["category"]] += t["value"]
    return max(spending.items(), key=operator.itemgetter(1))[0]


def getTransactionByMonth(docs, month, categoryId):
    def isInMonth(doc, month, categoryId):
        transaction = doc.to_dict()
        tMonth = transaction["date"].strftime("%m-%y")
        return tMonth == month and transaction["category"] == categoryId

    transactionInMonth = [
        d.to_dict() for d in list(docs) if isInMonth(d, month, categoryId)
    ]
    return [
        {
            "company": d["company"],
            "value": d["value"],
            "details": d["details"],
            "date": d["date"].strftime("%Y-%m-%d"),
        }
        for d in transactionInMonth
    ]


def transaction(request):
    categoryId, month, userId = re.match(
        "/(\w+)/(\d+-\d+)/(\w+)", request.path
    ).groups()
    print(
        f"Running analysis for user: {userId} for  category {categoryId} for month {month}"
    )
    user_transactions = users.document(userId).collection("transactions").get()
    response = {
        "responseCode": "SUCCESS",
        "responseMessage": "Success",
        "data": getTransactionByMonth(user_transactions, month, categoryId)
        # "data": [
        #     {
        #         "company": "Mcdonald",
        #         "details": "fried chicken",
        #         "date": "2018-05-01",
        #         "value": "7.99",
        #     },
        #     {
        #         "company": "KFC",
        #         "details": "Zinger",
        #         "date": "2018-05-02",
        #         "value": "125.9o",
        #     },
        #     {
        #         "details": "Wan Tan Mee",
        #         "company": "Kopitiam Ah Seng",
        #         "date": "2018-05-03",
        #         "value": "52",
        #     },
        # ],
    }
    return json.dumps(response, indent=4)


def pushNotify(transactions, body):
    historicalAvg = getTotalSpending(transactions) / 12.0
    paymentAvg = body["amount"] / body["duration"]
    data_message = {
        "data": {
            "id": body["id"],
            "total": body["amount"],
            "duration": body["duration"],
            "interest": 2,
            "payment": 100.00,
        }
    }
    message_title = "Loan approved"
    message_body = "Hi, review your loan offer now"
    push_service.notify_single_device(
        registration_id=os.environ["REG_ID"],
        message_title=message_title,
        message_body=message_body,
        data_message=data_message,
    )


def loan(request):
    def generateLoanObject(d):
        obj = d.to_dict()
        obj["id"] = d.id
        return obj

    args = re.match("/(\w+)/([\w\d-]+)/(\w+)", request.path)
    if request.method == "GET":
        userId = re.match("/(\w+)", request.path).groups()[0]
        loans = users.document(userId).collection("loans").get()
        loans = [generateLoanObject(d) for d in list(loans)]
        response = {
            "responseCode": "SUCCESS",
            "responseMessage": "Success",
            "data": loans,
        }
        return json.dumps(response, indent=4)

    if request.method == "POST":
        response = {"responseCode": "SUCCESS", "responseMessage": "Success"}
        if args and args.groups()[0] == "accept":
            print("Accepted")
            loans = (
                users.document(args.groups()[2])
                .collection("loans")
                .document(args.groups()[1])
                .update({"status": "ACCEPTED"})
            )
            return json.dumps(response, indent=4)
        if args and args.groups()[0] == "reject":
            loans = (
                users.document(args.groups()[2])
                .collection("loans")
                .document(args.groups()[1])
                .update({"status": "REJECTED"})
            )
            return json.dumps(response, indent=4)

        userId = re.match("/(\w+)", request.path).groups()[0]
        body = request.get_json(silent=True)
        id = str(uuid.uuid4())
        loans = (
            users.document(userId)
            .collection("loans")
            .document(id)
            .set(
                {
                    "total": body["amount"],
                    "duration": body["duration"],
                    "status": "PENDING",
                }
            )
        )
        body["id"] = id
        pushNotify(users.document(userId).collection("transactions"), body)
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
    user_transactions = users.document(userId).collection("transactions").get()
    print(f"Running analysis for user: {userId} with mode {mode}")

    if mode == "month":
        monthly_transactions = {}
        for doc in user_transactions:
            transaction = doc.to_dict()
            categoryId = transaction["category"]
            value = transaction["value"]
            date = transaction["date"]
            month = date.strftime("%m-%y")
            if month not in monthly_transactions:
                monthly_transactions[month] = {key: 0 for key in categories}
            monthly_transactions[month][categoryId] += value
        response = {
            "responseCode": "SUCCESS",
            "responseMessage": "Success",
            "data": generateMonthAggregate(monthly_transactions)
            # "data": [
            #     {
            #         "label": "05-18",
            #         "sum": 5120,
            #         "categories": [
            #             {"categoryId": "food", "value": 1000},
            #             {"categoryId": "bills", "value": 300},
            #             {"categoryId": "loans", "value": 400},
            #             {"categoryId": "entertainment", "value": 300},
            #             {"categoryId": "shopping", "value": 150},
            #             {"categoryId": "petrol", "value": 700},
            #             {"categoryId": "gifts", "value": 70},
            #             {"categoryId": "health", "value": 800},
            #             {"categoryId": "education", "value": 1400},
            #         ],
            #     },
            #     {
            #         "label": "06-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 100},
            #             {"categoryId": "bills", "value": 30},
            #             {"categoryId": "loans", "value": 20},
            #             {"categoryId": "entertainment", "value": 150},
            #             {"categoryId": "shopping", "value": 230},
            #             {"categoryId": "petrol", "value": 80},
            #             {"categoryId": "gifts", "value": 200},
            #             {"categoryId": "health", "value": 25},
            #             {"categoryId": "education", "value": 1300},
            #         ],
            #     },
            #     {
            #         "label": "07-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 900},
            #             {"categoryId": "bills", "value": 340},
            #             {"categoryId": "loans", "value": 250},
            #             {"categoryId": "entertainment", "value": 10},
            #             {"categoryId": "shopping", "value": 240},
            #             {"categoryId": "petrol", "value": 160},
            #             {"categoryId": "gifts", "value": 30},
            #             {"categoryId": "health", "value": 475},
            #             {"categoryId": "education", "value": 250},
            #         ],
            #     },
            #     {
            #         "label": "08-18",
            #         "sum": 3030,
            #         "categories": [
            #             {"categoryId": "food", "value": 1100},
            #             {"categoryId": "bills", "value": 540},
            #             {"categoryId": "loans", "value": 260},
            #             {"categoryId": "entertainment", "value": 50},
            #             {"categoryId": "shopping", "value": 640},
            #             {"categoryId": "petrol", "value": 250},
            #             {"categoryId": "gifts", "value": 0},
            #             {"categoryId": "health", "value": 90},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "09-18",
            #         "sum": 2195,
            #         "categories": [
            #             {"categoryId": "food", "value": 600},
            #             {"categoryId": "bills", "value": 240},
            #             {"categoryId": "loans", "value": 420},
            #             {"categoryId": "entertainment", "value": 200},
            #             {"categoryId": "shopping", "value": 40},
            #             {"categoryId": "petrol", "value": 190},
            #             {"categoryId": "gifts", "value": 130},
            #             {"categoryId": "health", "value": 275},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "10-18",
            #         "sum": 3615,
            #         "categories": [
            #             {"categoryId": "food", "value": 1200},
            #             {"categoryId": "bills", "value": 310},
            #             {"categoryId": "loans", "value": 400},
            #             {"categoryId": "entertainment", "value": 700},
            #             {"categoryId": "shopping", "value": 90},
            #             {"categoryId": "petrol", "value": 460},
            #             {"categoryId": "gifts", "value": 305},
            #             {"categoryId": "health", "value": 100},
            #             {"categoryId": "education", "value": 50},
            #         ],
            #     },
            #     {
            #         "label": "11-18",
            #         "sum": 3015,
            #         "categories": [
            #             {"categoryId": "food", "value": 770},
            #             {"categoryId": "bills", "value": 450},
            #             {"categoryId": "loans", "value": 450},
            #             {"categoryId": "entertainment", "value": 280},
            #             {"categoryId": "shopping", "value": 200},
            #             {"categoryId": "petrol", "value": 100},
            #             {"categoryId": "gifts", "value": 390},
            #             {"categoryId": "health", "value": 85},
            #             {"categoryId": "education", "value": 290},
            #         ],
            #     },
            #     {
            #         "label": "12-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 900},
            #             {"categoryId": "bills", "value": 340},
            #             {"categoryId": "loans", "value": 250},
            #             {"categoryId": "entertainment", "value": 10},
            #             {"categoryId": "shopping", "value": 240},
            #             {"categoryId": "petrol", "value": 160},
            #             {"categoryId": "gifts", "value": 30},
            #             {"categoryId": "health", "value": 475},
            #             {"categoryId": "education", "value": 250},
            #         ],
            #     },
            #     {
            #         "label": "01-19",
            #         "sum": 3030,
            #         "categories": [
            #             {"categoryId": "food", "value": 1100},
            #             {"categoryId": "bills", "value": 540},
            #             {"categoryId": "loans", "value": 260},
            #             {"categoryId": "entertainment", "value": 50},
            #             {"categoryId": "shopping", "value": 640},
            #             {"categoryId": "petrol", "value": 250},
            #             {"categoryId": "gifts", "value": 0},
            #             {"categoryId": "health", "value": 90},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "02-19",
            #         "sum": 2195,
            #         "categories": [
            #             {"categoryId": "food", "value": 600},
            #             {"categoryId": "bills", "value": 240},
            #             {"categoryId": "loans", "value": 420},
            #             {"categoryId": "entertainment", "value": 200},
            #             {"categoryId": "shopping", "value": 40},
            #             {"categoryId": "petrol", "value": 190},
            #             {"categoryId": "gifts", "value": 130},
            #             {"categoryId": "health", "value": 275},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "03-19",
            #         "sum": 3615,
            #         "categories": [
            #             {"categoryId": "food", "value": 1200},
            #             {"categoryId": "bills", "value": 310},
            #             {"categoryId": "loans", "value": 400},
            #             {"categoryId": "entertainment", "value": 700},
            #             {"categoryId": "shopping", "value": 90},
            #             {"categoryId": "petrol", "value": 460},
            #             {"categoryId": "gifts", "value": 305},
            #             {"categoryId": "health", "value": 100},
            #             {"categoryId": "education", "value": 50},
            #         ],
            #     },
            #     {
            #         "label": "04-19",
            #         "sum": 3015,
            #         "categories": [
            #             {"categoryId": "food", "value": 770},
            #             {"categoryId": "bills", "value": 450},
            #             {"categoryId": "loans", "value": 450},
            #             {"categoryId": "entertainment", "value": 280},
            #             {"categoryId": "shopping", "value": 200},
            #             {"categoryId": "petrol", "value": 100},
            #             {"categoryId": "gifts", "value": 390},
            #             {"categoryId": "health", "value": 85},
            #             {"categoryId": "education", "value": 290},
            #         ],
            #     },
            # ],
        }
        return json.dumps(response, indent=4)
    if mode == "week":
        weekly_transactions = {}
        for doc in user_transactions:
            transaction = doc.to_dict()
            categoryId = transaction["category"]
            value = transaction["value"]
            date = transaction["date"]
            week = date - timedelta(days=date.weekday())
            week = date.strftime("%d-%m-%y")
            if week not in weekly_transactions:
                weekly_transactions[week] = {key: 0 for key in categories}
            weekly_transactions[week][categoryId] += value
        response = {
            "responseCode": "SUCCESS",
            "responseMessage": "Success",
            "data": generateMonthAggregate(weekly_transactions)
            # "data": [
            #     {
            #         "label": "02-05-18",
            #         "sum": 512,
            #         "categories": [
            #             {"categoryId": "food", "value": 100},
            #             {"categoryId": "bills", "value": 30},
            #             {"categoryId": "loans", "value": 40},
            #             {"categoryId": "entertainment", "value": 30},
            #             {"categoryId": "shopping", "value": 15},
            #             {"categoryId": "petrol", "value": 70},
            #             {"categoryId": "gifts", "value": 7},
            #             {"categoryId": "health", "value": 80},
            #             {"categoryId": "education", "value": 140},
            #         ],
            #     },
            #     {
            #         "label": "09-05-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 100},
            #             {"categoryId": "bills", "value": 30},
            #             {"categoryId": "loans", "value": 20},
            #             {"categoryId": "entertainment", "value": 150},
            #             {"categoryId": "shopping", "value": 230},
            #             {"categoryId": "petrol", "value": 80},
            #             {"categoryId": "gifts", "value": 200},
            #             {"categoryId": "health", "value": 25},
            #             {"categoryId": "education", "value": 1300},
            #         ],
            #     },
            #     {
            #         "label": "16-05-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 900},
            #             {"categoryId": "bills", "value": 340},
            #             {"categoryId": "loans", "value": 250},
            #             {"categoryId": "entertainment", "value": 10},
            #             {"categoryId": "shopping", "value": 240},
            #             {"categoryId": "petrol", "value": 160},
            #             {"categoryId": "gifts", "value": 30},
            #             {"categoryId": "health", "value": 475},
            #             {"categoryId": "education", "value": 250},
            #         ],
            #     },
            #     {
            #         "label": "23-05-18",
            #         "sum": 5120,
            #         "categories": [
            #             {"categoryId": "food", "value": 1000},
            #             {"categoryId": "bills", "value": 300},
            #             {"categoryId": "loans", "value": 400},
            #             {"categoryId": "entertainment", "value": 300},
            #             {"categoryId": "shopping", "value": 150},
            #             {"categoryId": "petrol", "value": 700},
            #             {"categoryId": "gifts", "value": 70},
            #             {"categoryId": "health", "value": 800},
            #             {"categoryId": "education", "value": 1400},
            #         ],
            #     },
            #     {
            #         "label": "30-05-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 100},
            #             {"categoryId": "bills", "value": 30},
            #             {"categoryId": "loans", "value": 20},
            #             {"categoryId": "entertainment", "value": 150},
            #             {"categoryId": "shopping", "value": 230},
            #             {"categoryId": "petrol", "value": 80},
            #             {"categoryId": "gifts", "value": 200},
            #             {"categoryId": "health", "value": 25},
            #             {"categoryId": "education", "value": 1300},
            #         ],
            #     },
            #     {
            #         "label": "07-06-18",
            #         "sum": 2135,
            #         "categories": [
            #             {"categoryId": "food", "value": 900},
            #             {"categoryId": "bills", "value": 340},
            #             {"categoryId": "loans", "value": 250},
            #             {"categoryId": "entertainment", "value": 10},
            #             {"categoryId": "shopping", "value": 240},
            #             {"categoryId": "petrol", "value": 160},
            #             {"categoryId": "gifts", "value": 30},
            #             {"categoryId": "health", "value": 475},
            #             {"categoryId": "education", "value": 250},
            #         ],
            #     },
            #     {
            #         "label": "14-06-18",
            #         "sum": 3030,
            #         "categories": [
            #             {"categoryId": "food", "value": 1100},
            #             {"categoryId": "bills", "value": 540},
            #             {"categoryId": "loans", "value": 260},
            #             {"categoryId": "entertainment", "value": 50},
            #             {"categoryId": "shopping", "value": 640},
            #             {"categoryId": "petrol", "value": 250},
            #             {"categoryId": "gifts", "value": 0},
            #             {"categoryId": "health", "value": 90},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "21-06-18",
            #         "sum": 2195,
            #         "categories": [
            #             {"categoryId": "food", "value": 600},
            #             {"categoryId": "bills", "value": 240},
            #             {"categoryId": "loans", "value": 420},
            #             {"categoryId": "entertainment", "value": 200},
            #             {"categoryId": "shopping", "value": 40},
            #             {"categoryId": "petrol", "value": 190},
            #             {"categoryId": "gifts", "value": 130},
            #             {"categoryId": "health", "value": 275},
            #             {"categoryId": "education", "value": 100},
            #         ],
            #     },
            #     {
            #         "label": "28-06-18",
            #         "sum": 3615,
            #         "categories": [
            #             {"categoryId": "food", "value": 1200},
            #             {"categoryId": "bills", "value": 310},
            #             {"categoryId": "loans", "value": 400},
            #             {"categoryId": "entertainment", "value": 700},
            #             {"categoryId": "shopping", "value": 90},
            #             {"categoryId": "petrol", "value": 460},
            #             {"categoryId": "gifts", "value": 305},
            #             {"categoryId": "health", "value": 100},
            #             {"categoryId": "education", "value": 50},
            #         ],
            #     },
            #     {
            #         "label": "05-07-18",
            #         "sum": 3015,
            #         "categories": [
            #             {"categoryId": "food", "value": 770},
            #             {"categoryId": "bills", "value": 450},
            #             {"categoryId": "loans", "value": 450},
            #             {"categoryId": "entertainment", "value": 280},
            #             {"categoryId": "shopping", "value": 200},
            #             {"categoryId": "petrol", "value": 100},
            #             {"categoryId": "gifts", "value": 390},
            #             {"categoryId": "health", "value": 85},
            #             {"categoryId": "education", "value": 290},
            #         ],
            #     },
            # ],
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

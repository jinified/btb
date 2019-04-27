import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timedelta
import operator


API_KEY = "AAAAxNpWUWQ:APA91bGcIaD6-UwlX_rqrAJv1eeOf1-s3d50mK-L_yNvg2AXXJIhHZh1kQnJ9kdCd7ULY3k7oavqWnm7UbcOx3hVvK_EBD6R712IOGAo748M-MO_RrjirmKqoIPSYSE98dcM6r75YKBR"

REG_ID = "e7OMCvddRgE:APA91bHDstR9R5qgcMEZ6bpCSEsgncOJYNGRVW16LjuAonIC-gmAx-A3MdBeH6TCGTeLuwvNBWwCVcaHhv0KeZv8D5MtyYIb13Wh4g3mFN6zc7kC4-uEBlv9O4XD5fFPJEKhjDDBcf-o"

# Use a service account
cred = credentials.Certificate("../keyfile.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


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


def getTotalSpending(transactions, categoryId=None):
    if categoryId:
        return sum(
            [
                t.to_dict()["value"]
                for t in transactions.where(u"category", u"==", categoryId).get()
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


if __name__ == "__main__":
    from pyfcm import FCMNotification

    push_service = FCMNotification(api_key=API_KEY)
    message_title = "Uber update"
message_body = "Hi john, your customized news for today is ready"
result = push_service.notify_single_device(
    registration_id=REG_ID, message_title=message_title, message_body=message_body
)

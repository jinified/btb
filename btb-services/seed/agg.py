import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timedelta

# Use a service account
cred = credentials.Certificate("../keyfile.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def generateMonthAggregate(monthly_transactions):
    def generateMonthObject(month, spending):
        totalSpending = sum(spending.values())
        categories = [{"categoryId": k, "value": v} for k, v in spending.items()]
        return {"label": month, "sum": totalSpending, "categories": categories}

    return [generateMonthObject(k, v) for k, v in monthly_transactions.items()]


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


if __name__ == "__main__":
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
    weekly_transactions = {}
    users = db.collection("users")
    user_transactions = users.document(u"stephen").collection(u"transactions").get()
    weekly_transactions = {}
    weeks = []
    for doc in user_transactions:
        transaction = doc.to_dict()
        categoryId = transaction["category"]
        value = transaction["value"]
        date = transaction["date"]
        week = date.strftime("%V-%y")
        if week not in weekly_transactions:
            weekly_transactions[week] = {key: 0 for key in categories}
        weekly_transactions[week][categoryId] += value
    print(sorted(weekly_transactions.keys()))

import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timedelta
import operator


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


def getTotalSpending(categoryId, transactions):
    return sum(
        [
            t.to_dict()["value"]
            for t in transactions.where(u"category", u"==", categoryId).get()
        ]
    )


def calculateWiseSavings(transactions):
    maxCat = calcMaxCategory(transactions.get())
    total_maxCat_spending = getTotalSpending(maxCat, transactions)
    print(total_maxCat_spending)
    return 0.1 * total_maxCat_spending


def calculateEssentialSavings(transactions):
    pass


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
    users = db.collection("users")
    user_transactions = users.document(u"stephen").collection(u"transactions")
    scoreWise = calculateWiseSavings(user_transactions)
    print("Save", scoreWise)

import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Use a service account
cred = credentials.Certificate('../keyfile.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def generateMonthAggregate(monthly_transactions):
    def generateMonthObject(month, spending):
        totalSpending = sum(spending.values())
        categories = [{"categoryId": k, "value": v} for k, v in spending.items()]
        return {
                "label": month,
                "sum": totalSpending,
                "categories": categories
        }
    return [generateMonthObject(k, v) for k,v in monthly_transactions.items()]


if __name__ == "__main__":
    categories = ['food', 'bills', 'loans', 'entertainment', 'shopping', 'petrol', 'gifts', 'health', 'education']
    monthly_transactions = {}
    users = db.collection("users")
    
    user_transactions = users.document(u"stephen").collection(u"transactions").get()
    for doc in user_transactions:
        transaction = doc.to_dict()
        categoryId = transaction['category']
        value = transaction['value']
        date = transaction['date']
        month = date.strftime('%m-%y')
        if month not in monthly_transactions:
            monthly_transactions[month] = {key: 0 for key in categories}
        monthly_transactions[month][categoryId] += value
    print(generateMonthAggregate(monthly_transactions))

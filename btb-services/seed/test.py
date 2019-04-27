import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Use a service account
cred = credentials.Certificate('../keyfile.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

if __name__ == "__main__":
    users = db.collection("users")
    user = users.document(u"stephen").collection(u"transactions")

    my_filtered_csv = pd.read_csv(
        "./missing_transac.csv",
        usecols=["Details", "Company", "Category", "Year", "Value"],
    )
    for i, row in my_filtered_csv.iterrows():
        data = {
            u'details': row['Details'],
            u'category': row['Category'],
            u'company': row['Company'],
            u'value': row['Value'],
            u'date': datetime.strptime(row['Year'], '%Y-%m-%d')
        }
        user.add(data)

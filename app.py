from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Load rate card data from CSV into a pandas DataFrame
rate_card_data = pd.read_csv('assignment_raw_rate.csv')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['insurance']  # Replace 'insurance' with your MongoDB database name
premium_collection = db['premiums']  # MongoDB collection to store premium data

def calculate_premium_logic(member_ages, sum_insured, city_tier, tenure):
    # Get the relevant rate card data based on the user inputs
    
    # print(rate_card)
    # Calculate premium for different member combinations
    premium = 0
    # print(member_ages,sum_insured,city_tier,tenure)
    member_ages = list(map(int,member_ages))
    sum_insured = list(map(int,sum_insured))
    city_tier = list(map(int,city_tier))
    tenure = list(map(int,tenure))
    if len(member_ages) == 1:
          # Single Individual (1a)
        rate_card = rate_card_data[
        (rate_card_data['SumInsured'] == int(sum_insured[0])) &
        (rate_card_data['TierID'] == int(city_tier[0])) &
        (rate_card_data['Tenure'] == int(tenure[0]))
    ]
        # print(rate_card)
        age = member_ages[0]
        if(age>=18):
            rate_card_temp = rate_card[rate_card['Age'] == age]
            premium += int(rate_card_temp['Rate'].values[0]) #Only One Adult
            # print(int(rate_card_temp['Rate'].values[0]))
        else:
            rate_card_temp = rate_card[rate_card['Age'] == age]
            premium += int(rate_card_temp['Rate'].values[0])/2 #Only One Child
            # print(int(rate_card_temp['Rate'].values[0])/2)
    else:  # Family combinations
        childrens = []
        adults = []
        for i in range(len(member_ages)):
            if(member_ages[i]>=18):
                adults.append(member_ages[i])
                
            else:
                childrens.append(member_ages[i])
        # print(adults)
        # print(childrens)   
        for i in range(len(childrens)):
            rate_card = rate_card_data[
        (rate_card_data['SumInsured'] == sum_insured[i]) &
        (rate_card_data['TierID'] == city_tier[i]) &
        (rate_card_data['Tenure'] == tenure[i])]
           
            rate_card = rate_card[rate_card['Age'] == member_ages[i]]
            
            premium = premium + int(rate_card['Rate'].values[0])/2
            # print(int(rate_card['Rate'].values[0])/2)
        count = 0
        for i in range(len(adults)):
            
            rate_card = rate_card_data[
        (rate_card_data['SumInsured'] == sum_insured[i]) &
        (rate_card_data['TierID'] == city_tier[i]) &
        (rate_card_data['Tenure'] == tenure[i])]
            rate_card = rate_card[rate_card['Age'] == member_ages[i]]
            if(count==0):
                premium = premium + int(rate_card['Rate'].values[0])
                # print(rate_card)
                # print(int(rate_card['Rate'].values[0]))
            else:
                # print(int(rate_card['Rate'].values[0])/2)
                premium += int(rate_card['Rate'].values[0])/2
                # print(rate_card)
            count += 1
            



    
    return premium

def store_premium_data(member_ages, sum_insured, city_tier, tenure, premium):
    # Create a document to store premium data
    data = {
        'member_ages': member_ages,
        'sum_insured': sum_insured,
        'city_tier': city_tier,
        'tenure': tenure,
        'premium': premium
    }
    
    # Insert the document into the MongoDB collection
    premium_collection.insert_one(data)

@app.route('/calculate-premium', methods=['POST'])
def calculate_premium():
    data = request.json
    
    # Retrieve user inputs from the request JSON
    member_ages = data['member_ages']
    sum_insured = data['sum_insured']
    city_tier = data['city_tier']
    tenure = data['tenure']
    
    # Implement the logic to calculate the premium based on the rate card data and user inputs
    premium = calculate_premium_logic(member_ages, sum_insured, city_tier, tenure)
    
    # Store the premium data in MongoDB
    store_premium_data(member_ages, sum_insured, city_tier, tenure, premium)
    
    # Return the premium as a JSON response
    return jsonify({'premium': premium})

if __name__ == '__main__':
    app.run(debug=True)

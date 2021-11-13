from flask import Flask, render_template, request, redirect, url_for
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import random

app = Flask(__name__)
app.secret_key = "super secret key"

with open('lr.pickle', 'rb') as handle:
    model = pickle.load(handle)


@app.route('/')
def helloIndex():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about-us.html')

@app.route('/research')
def research():
    return render_template('research.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/analyzer')
def analyze():
    return render_template('analyzer.html')


@app.route('/uploader', methods=['GET', 'POST'])
def getData():
    # getting input of the inserted values by user

    platform = request.form['platform']
    genre = request.form['genre']
    publisher = request.form['publisher']
    yearOfRelease = request.form['year-of-release']
    criticScore = request.form['critic-score']
    developmentExpense = float(request.form['development-expense'])
    marketingExpense = float(request.form['marketing-expense'])
    perUnitPrice = float(request.form['per-unit-price'])

    # Array with inserted values
    data = [{'Platform': platform, 'Genre': genre, 'Publisher': publisher, 'Year_of_Release': float(yearOfRelease),
             'Critic_Score': float(criticScore)}]
    row = pd.DataFrame(data)  # converting it into dataframe

    # taking the dataset to apply labelencoder to the data so that encoder transform data into satisfying transformation
    df = pd.read_csv('Video_Games_Sales_as_at_22_Dec_2016.csv')
    dfa = df

    dfb = dfa[['Name', 'Platform', 'Genre', 'Publisher', 'Year_of_Release', 'Critic_Score', 'Global_Sales']]
    dfb = dfb.fillna(dfb.mean())
    dfb = dfb.dropna().reset_index(drop=True)
    df2 = dfb[['Platform', 'Genre', 'Publisher', 'Year_of_Release', 'Critic_Score', 'Global_Sales']]

    # inserting user givern row into the dataset
    X = df2.iloc[:, :-1]
    X = X.append(row, ignore_index=True)
    X = X.apply(LabelEncoder().fit_transform)

    # predicting the value
    r1 = X.iloc[-1:]
    prd = model.predict(r1)
    prdictedSales = (round(float(prd) * 1000000))

    totalBudget = developmentExpense + marketingExpense
    unitsToBeSoldToBreakEven = (totalBudget/perUnitPrice)
    expectedProfit = prdictedSales - unitsToBeSoldToBreakEven

    if expectedProfit < 0:
        return render_template('result.html', ps=prdictedSales, de=developmentExpense, me=marketingExpense, pup=perUnitPrice, ep=round(abs(expectedProfit)), tb=totalBudget, strPL="Expected Loss")
    else:
        return render_template('result.html', ps=prdictedSales, de=developmentExpense, me=marketingExpense, pup=perUnitPrice, ep=round(expectedProfit), tb=totalBudget, strPL="Expected Profit")

@app.route('/subscription', methods=['GET','POST'])
def subsAlert():
    subscribedEmails = pd.read_csv('subscribed emails.csv')

    email = [{'index': random.randint(0, 100), 'Emails': request.form['EMAIL']}]
    pdEmail = pd.DataFrame(email)
    subscribedEmails = subscribedEmails.append(pdEmail, ignore_index=True)
    subscribedEmails.sort_values('index', ascending=True, inplace=True)

    return "subscribed successfully"

if __name__ == '__main__':
    app.run(debug=True)

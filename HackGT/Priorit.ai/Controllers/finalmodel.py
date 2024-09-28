import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from time import time
from sklearn.pipeline import Pipeline
from pprint import pprint
from sklearn.model_selection import GridSearchCV
import sys

kNB = "https://raw.githubusercontent.com/schakk34/Priorit.ai/refs/heads/main/kitchenAndBath.csv"
rI = "https://raw.githubusercontent.com/schakk34/Priorit.ai/refs/heads/main/roomIssue.csv"
elc = "https://raw.githubusercontent.com/schakk34/Priorit.ai/refs/heads/main/electrical.csv"
kitchenDF = pd.read_csv(kNB)
roomDF = pd.read_csv(rI)
electricalDF = pd.read_csv(elc)

def test(df):
    X_train, X_test, y_train, y_test = train_test_split(
        df['Complaint'], df['Issue'], shuffle=True, test_size=0.2, random_state=None)

    tfidf = TfidfVectorizer(sublinear_tf=True,
                            min_df=4,
                            max_df=0.6,
                            norm='l1',
                            ngram_range=(1, 2),
                            stop_words='english')

    X_train_counts = tfidf.fit_transform(X_train)
    X_test_counts = tfidf.transform(X_test)

    model = MultinomialNB(alpha=1e-04)
    model.fit(X_train_counts, y_train)

    y_pred_prob = model.predict_proba(X_test_counts)
    predicted_dict = {}
    unique_issues = df['Issue'].unique()
    for k in range(len(unique_issues)):
      predicted_dict[unique_issues[k]] = y_pred_prob[:, k]
    predicted = pd.DataFrame(predicted_dict)


    y_pred = model.predict(X_test_counts)
    acc = metrics.accuracy_score(y_test, y_pred)

    return acc, model, tfidf

def test_reply (order, df, myAcc, myModel, myTFDIF):
    input = np.array([order])
    input_counts = myTFDIF.transform(input)
    y_pred_prob = myModel.predict_proba(input_counts)
    dict = {}
    unique_issues = df["Issue"].unique()
    for k in range(len(unique_issues)):
      dict[unique_issues[k]] = y_pred_prob[:, k]
    largest_element = y_pred_prob.max()
    if largest_element >= (3.5/5):
        reply = [myModel.predict(input_counts)[0], 1]
    elif largest_element >= (1.5/5):
        reply = [myModel.predict(input_counts)[0], 0]
    else:
        reply = [myModel.predict(input_counts)[0], -1]
    return reply

def model_reply(arg1, arg2):
  input_df = arg1
  order = arg2
  myAcc, myModel, myTFDIF = test(input_df)
  return test_reply(order, input_df, myAcc, myModel, myTFDIF)

if __name__ == '__main__':
    input_data = sys.argv[1]  # Get input from command line
    result = model_reply(input_data)
    print(result)  # Output the result

from flask import Flask, render_template, request
from textblob import TextBlob
from apify_client import ApifyClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = Flask(__name__)

client = ApifyClient("**************************************")


def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'
    
def SendMail(data1):    
    message = MIMEMultipart()
    sender_email = 'Your email'
    receiver_email = request.form['email']
    password = '*******'
    message['From'] = sender_email
    message['To'] = receiver_email
    formatted_data = '\n'.join(['-'.join(item) for item in data1])
    message['Subject'] = "Sentiment Analysis of your latest post"


    body = formatted_data
    message.attach(MIMEText(body, 'plain'))


    with smtplib.SMTP('smtp.gmail.com', 587) as server:
      server.starttls()  # Secure the connection
      # Login to your email account
      server.login(sender_email, password)
      text = message.as_string()
      # Send the email
      server.sendmail(sender_email, receiver_email, text)
   
        


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
   
    url = request.form['url']
    
    # Prepare the Actor input
    run_input = {
        "startUrls": [{"url": url}],
        "resultsLimit": 1,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }


    run = client.actor("KoJrdxJCTtpon81KY").call(run_input=run_input)

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        ab = item['url']
        # print(ab)


    run_input = {
        "startUrls": [{"url": ab}],
        "resultsLimit": 100,
        "includeNestedComments": False,
        "viewOption": "RANKED_UNFILTERED",
    }

    run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)


    comment_sentiments = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        if 'text' not in item:
            continue
        text = item['text']
        sentiment = analyze_sentiment(text)
        
        comment_sentiments.append((text, sentiment))
    
    SendMail(comment_sentiments)
    return render_template('result.html', comment_sentiments=comment_sentiments)

if __name__ == '__main__':
    app.run(debug=True)

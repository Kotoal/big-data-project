import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

data = {
    'text': [
        'Free entry in 2 a weekly comp to win FA Cup final tickets 21st May.',
        'Free tones Hope you enjoyed your new text tone',
        'Winner as a valued network customer you have been selected to receivea £900 prize reward!',
        'URGENT! Your Mobile number has been awarded with a £2000 prize BONUS.',
        'Had your mobile 11 months or more? U R entitled to Update to the latest colour camera mobiles for Free!',
        'Hi, how are you doing today?',
        'Are you coming for dinner tonight at 8?',
        'Just chilling at home, let me know when you are free.',
        'Hey, can you send me the homework details?',
        'The meeting is scheduled for tomorrow morning.'
    ],
    'label': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0] # 1 = Spam, 0 = Normal
}

df = pd.DataFrame(data)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['label']

model = LogisticRegression()
model.fit(X, y)

os.makedirs("models", exist_ok=True)
with open("models/spam_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("Model trained and saved in models/ directory:")
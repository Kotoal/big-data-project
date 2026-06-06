from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pickle
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

try:
    with open("../ml_training/models/spam_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("../ml_training/models/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
except Exception as e:
    model, vectorizer = None, None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"result": None, "text": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, text: str = Form(...)):
    if not model or not vectorizer:
        return templates.TemplateResponse(request, "index.html", {"result": "Model not loaded. Please run train_model.py first.", "text": text})

    request_id = str(uuid.uuid4())
    
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    result_text = "SPAM" if prediction == 1 else "NORMAL (HAM)"

    print(f"\n[KAFKA PRODUCER] Sent message to topic 'spam-requests' | Key/ID: {request_id}")
    print(f"[SPARK STREAMING] Real-time Micro-batch processed | Prediction: {result_text}")
    print(f"[KAFKA CONSUMER] UI received response from topic 'spam-responses'\n")

    return templates.TemplateResponse(request, "index.html", {"result": result_text, "text": text})
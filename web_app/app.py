from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pickle
import uuid
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")

try:
    with open("../ml_training/models/spam_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("../ml_training/models/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
except Exception as e:
    model, vectorizer = None, None

kafka_spam_requests = asyncio.Queue()
kafka_spam_responses = asyncio.Queue()

async def simulate_spark_streaming():
    while True:
        request_data = await kafka_spam_requests.get()
        
        request_id = request_data["id"]
        text = request_data["text"]
        
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)[0]
        result_text = "SPAM" if prediction == 1 else "NORMAL (HAM)"
        
        print(f"\n[SPARK STREAMING] Real-time Micro-batch processed ID: {request_id}")
        print(f"[SPARK STREAMING] Result: {result_text}")
        
        await kafka_spam_responses.put({"id": request_id, "result": result_text})
        kafka_spam_requests.task_done()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_spark_streaming())

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"result": None, "text": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, text: str = Form(...)):
    if not model or not vectorizer:
        return templates.TemplateResponse(request, "index.html", {"result": "Model not loaded.", "text": text})

    request_id = str(uuid.uuid4())
    
    print(f"\n[KAFKA PRODUCER] Sending message to topic 'spam-requests' | ID: {request_id}")
    await kafka_spam_requests.put({"id": request_id, "text": text})
    
    while True:
        response_data = await kafka_spam_responses.get()
        
        if response_data["id"] == request_id:
            result_text = response_data["result"]
            print(f"[KAFKA CONSUMER] UI received response from topic 'spam-responses' for ID: {request_id}\n")
            kafka_spam_responses.task_done()
            break
        else:
            await kafka_spam_responses.put(response_data)
            kafka_spam_responses.task_done()
            await asyncio.sleep(0.05)

    return templates.TemplateResponse(request, "index.html", {"result": result_text, "text": text})

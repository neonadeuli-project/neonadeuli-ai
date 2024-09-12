from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
from clovax import CompletionExecutor, SlidingWindowExecutor
from models import ChatRequest
import os

load_dotenv()
app = FastAPI()

@app.post("/chat")
async def chat(request:ChatRequest):
    try:
        completion_executor = CompletionExecutor(
            host='https://clovastudio.stream.ntruss.com',
            api_key=os.getenv("API_KEY"),
            api_key_primary_val=os.getenv("API_PRIMARY_VALUE"),
            request_id='0c5652e1-2810-4e8f-a58d-620a9b9e2b71'
        )
        slidingwindow_executor = SlidingWindowExecutor(
            host='https://clovastudio.apigw.ntruss.com',
            api_key=os.getenv("API_KEY"),
            api_key_primary_val=os.getenv("API_PRIMARY_VALUE"),
        )

        preset_text = [{"role":"user", "content":request.content}]
        request_data = {
            'messages' : preset_text,
            'maxTokens' : 2000
        }
        adjusted_messages = slidingwindow_executor.execute(request_data)
        request_data = {
            'messages': adjusted_messages,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }
        response = completion_executor.execute(request_data)
        return {"response": response['result']['message']['content']}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
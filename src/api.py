from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
import time

from src.graph import agent_graph


# ============================================================
# CREATE API
# ============================================================

app = FastAPI(
    title="LangGraph AI Agent API",
    description="OpenAI-compatible API for LangGraph + Ollama Agent",
    version="1.0"
)


# ============================================================
# OPENAI-COMPATIBLE DATA MODELS
# ============================================================

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "running",
        "message": "LangGraph AI Agent API is running"
    }


# ============================================================
# MODEL LIST
# ============================================================

@app.get("/v1/models")
def list_models():

    return {
        "object": "list",
        "data": [
            {
                "id": "langgraph-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local-agent"
            }
        ]
    }


# ============================================================
# CHAT COMPLETIONS
# ============================================================

@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest):

    # --------------------------------------------------------
    # GET THE USER'S LATEST MESSAGE
    # --------------------------------------------------------

    user_message = ""

    for message in reversed(request.messages):

        if message.role == "user":

            user_message = message.content
            break

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not user_message:

        return {
            "error": {
                "message": "No user message was provided.",
                "type": "invalid_request_error"
            }
        }

    # --------------------------------------------------------
    # INITIAL AGENT STATE
    # --------------------------------------------------------

    initial_state = {

        "user_input": user_message,

        "plan": [],

        "tool_arguments": {},

        "current_step": 0,

        "max_steps": 5,

        "tool_results": [],

        "reasoning_history": [],

        "error": "",

        "final_response": ""
    }

    # --------------------------------------------------------
    # RUN LANGGRAPH AGENT
    # --------------------------------------------------------

    try:

        result = agent_graph.invoke(initial_state)

        final_response = result.get(
            "final_response",
            "I could not generate a response."
        )

    except Exception as e:

        final_response = (
            f"Agent execution failed: {str(e)}"
        )

    # --------------------------------------------------------
    # STREAMING RESPONSE
    # --------------------------------------------------------

    if request.stream:

        completion_id = f"chatcmpl-{uuid.uuid4().hex}"

        def generate():

            # First chunk
            first_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant"
                        },
                        "finish_reason": None
                    }
                ]
            }

            yield f"data: {json.dumps(first_chunk)}\n\n"

            # Response chunk
            response_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": final_response
                        },
                        "finish_reason": None
                    }
                ]
            }

            yield f"data: {json.dumps(response_chunk)}\n\n"

            # Final chunk
            final_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }

            yield f"data: {json.dumps(final_chunk)}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    # --------------------------------------------------------
    # NORMAL RESPONSE
    # --------------------------------------------------------

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": final_response
                },
                "finish_reason": "stop"
            }
        ]
    }
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
from graphiti_core import Graphiti
from fastapi.middleware.cors import CORSMiddleware
from graphiti_core.search.search_config_recipes import (
    COMBINED_HYBRID_SEARCH_RRF,     
    COMBINED_HYBRID_SEARCH_MMR, 
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_RRF,
    EDGE_HYBRID_SEARCH_MMR,
    EDGE_HYBRID_SEARCH_NODE_DISTANCE,
    EDGE_HYBRID_SEARCH_EPISODE_MENTIONS,
    EDGE_HYBRID_SEARCH_CROSS_ENCODER,
    NODE_HYBRID_SEARCH_RRF,
    NODE_HYBRID_SEARCH_MMR,
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_EPISODE_MENTIONS,
    NODE_HYBRID_SEARCH_CROSS_ENCODER,
    COMMUNITY_HYBRID_SEARCH_RRF,
    COMMUNITY_HYBRID_SEARCH_MMR,
    COMMUNITY_HYBRID_SEARCH_CROSS_ENCODER
)
from typing import List
import logging

# --- Load environment variables ---
load_dotenv()
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')

app = FastAPI(
    title="Graphiti Minimal Search API",
    description="Minimal search endpoint using Graphiti. Accepts only a query string.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.vapi.ai"], # Or ["*"] for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Vapi-Signature"],
)

class SearchResponse(BaseModel):
    results: list[dict]

class ManualSearchRequest(BaseModel):
    query: str

class ToolCallArguments(BaseModel):
    query: str

class ToolCall(BaseModel):
    id: str
    arguments: ToolCallArguments

class Message(BaseModel):
    toolCallList: List[ToolCall]

class SearchToolRequest(BaseModel):
    message: Message

class SearchToolResult(BaseModel):
    toolCallId: str
    result: List[dict]

class SearchToolResponse(BaseModel):
    results: List[SearchToolResult]

# --- Graphiti client (initialized on startup) ---
graphiti = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook-search")

@app.on_event("startup")
async def startup_event():
    global graphiti
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    await graphiti.build_indices_and_constraints()

@app.on_event("shutdown")
async def shutdown_event():
    global graphiti
    if graphiti:
        await graphiti.close()

node_search_config = NODE_HYBRID_SEARCH_EPISODE_MENTIONS.model_copy(deep=True)
node_search_config.limit = 5

@app.post("/search", response_model=SearchToolResponse)
async def search_endpoint(req: SearchToolRequest):
    try:
        tool_call = req.message.toolCallList[0]
        query = tool_call.arguments.query
        tool_call_id = tool_call.id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")
    try:
        results = await graphiti._search(
            query=query,
            config=node_search_config,
            group_ids=["absolute_cosmetic_procedures"]
        )
        # Extract only the nodes
        nodes = []
        for label, items in results:
            if label == "nodes":
                nodes = items
                break
        filtered = [
            {
                "name": getattr(node, "name", None),
                "group_id": getattr(node, "group_id", None),
                "summary": getattr(node, "summary", None)
            }
            for node in nodes
        ]
        return SearchToolResponse(
            results=[
                SearchToolResult(
                    toolCallId=tool_call_id,
                    result=filtered
                )
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@app.post("/search-manual", response_model=SearchResponse)
async def search_manual_endpoint(req: ManualSearchRequest):
    query = req.query
    if not query:
        raise HTTPException(status_code=400, detail="'query' is required.")
    try:
        results = await graphiti._search(
            query=query,
            config=node_search_config,
            group_ids=["absolute_cosmetic_procedures"]
        )
        # Extract only the nodes
        nodes = []
        for label, items in results:
            if label == "nodes":
                nodes = items
                break
        filtered = [
            {
                "name": getattr(node, "name", None),
                "group_id": getattr(node, "group_id", None),
                "summary": getattr(node, "summary", None)
            }
            for node in nodes
        ]
        return {"results": filtered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@app.post("/webhook-search")
async def webhook_search(request: Request):
    try:
        events = await request.json()
        logger.info(f"Received events: {events}")
        event = events[0]
        body = event["body"]
        tool_call = body["message"]["toolCallList"][0]
        tool_call_id = tool_call["id"]
        query = tool_call["function"]["arguments"]["query"]
        logger.info(f"Extracted toolCallId: {tool_call_id}, query: {query}")
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid webhook format: {e}")

    try:
        results = await graphiti._search(
            query=query,
            config=node_search_config,
            group_ids=["absolute_cosmetic_procedures"]
        )
        # Extract only the nodes
        nodes = []
        for label, items in results:
            if label == "nodes":
                nodes = items
                break
        filtered = [
            {
                "name": getattr(node, "name", None),
                "group_id": getattr(node, "group_id", None),
                "summary": getattr(node, "summary", None)
            }
            for node in nodes
        ]
        logger.info(f"Returning {len(filtered)} results for toolCallId {tool_call_id}")
        return {
            "results": [
                {
                    "toolCallId": tool_call_id,
                    "result": filtered
                }
            ]
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


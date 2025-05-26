# learn_tube_ai/app/services/llm_service.py
import os
import time 
import random 
from typing import Optional # <<< ADD THIS IMPORT (or add Optional to existing typing import)
# import anthropic 
# import json 

# --- MockAnthropicClient class definition (remains the same as before) ---
class MockAnthropicClient:
    # ... (your existing MockAnthropicClient code)
    def __init__(self, api_key=None):
        if api_key: print(f"MockAnthropicClient initialized WITH API key: {api_key[:5]}... (but will use placeholder data).")
        else: print("MockAnthropicClient initialized WITHOUT API key (will use placeholder data).")
        self.api_key = api_key
    def messagescreate(self, model, max_tokens, messages, system=None):
        print(f"MockAnthropicClient: messages.create called. Model: {model}, Max Tokens: {max_tokens}")
        time.sleep(0.5 + random.random() * 0.5)
        user_prompt_summary = "Generic user prompt"
        if messages and messages[0].get("role") == "user":
            content = messages[0].get("content")
            if isinstance(content, list): user_prompt_summary = " ".join([block.get("text", "") for block in content if block.get("type") == "text"])
            elif isinstance(content, str): user_prompt_summary = content
        mock_response_text = f"This is a structured MOCK LLM response for general analysis based on the prompt: '{user_prompt_summary[:70]}...'. "
        return { "table_of_contents": [{"title": "Mock ToC - Intro", "timestamp_seconds": 10}, {"title": "Mock ToC - Main", "timestamp_seconds": 60}], "key_terms": [{"term": "Mock Data", "definition": "Placeholder info. " + mock_response_text}, {"term": "Simulation", "definition": "Mimicking behavior. " + mock_response_text}], "logical_flow": "Mock flow: 1. A, 2. B, 3. C. " + mock_response_text, "summary": "This is a mock summary. " + mock_response_text }

# --- Global LLM_CLIENT initialization (remains the same) ---
LLM_CLIENT = None
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY: # ... (rest of LLM_CLIENT init)
    print("LLM_SERVICE: ANTHROPIC_API_KEY not found. Using MOCK LLM client.")
    LLM_CLIENT = MockAnthropicClient()
else:
    try:
        print(f"LLM_SERVICE: ANTHROPIC_API_KEY found. Real client would be initialized (currently using mock).")
        LLM_CLIENT = MockAnthropicClient(api_key=ANTHROPIC_API_KEY) 
    except Exception as e:
        print(f"LLM_SERVICE: Error initializing real Anthropic client: {e}. Falling back to MOCK LLM client.")
        LLM_CLIENT = MockAnthropicClient()

def generate_analysis_from_text(transcript_text: str) -> dict:
    """
    Generates video analysis (ToC, key terms, logical flow, summary) from transcript text.
    Uses the globally initialized LLM_CLIENT (mock or real).
    """
    if not LLM_CLIENT:
        print("LLM_SERVICE: LLM Client not initialized. Cannot generate analysis.")
        return {
            "table_of_contents": [], "key_terms": [], 
            "logical_flow": "LLM client not available for analysis.", 
            "summary": "Summary generation skipped as LLM client is not available."
        }

    # This system prompt can be refined to better instruct the LLM
    system_prompt = """You are a helpful assistant. Analyze the provided video transcript and generate the following:
    1.  A table of contents (list of objects, each with "title" and approximate "timestamp_seconds" if inferable, otherwise just titles).
    2.  A list of key terms (list of objects, each with "term" and "definition" relevant to the transcript).
    3.  A description of the logical flow or structure of the content (string).
    4.  A concise summary of the video (string).
    Return your response as a single JSON object with keys: "table_of_contents", "key_terms", "logical_flow", and "summary"."""

    # Using the newer message format if your client expects it
    messages_payload = [
        {
            "role": "user",
            "content": [ # Claude 3 often prefers content as a list of blocks
                {
                    "type": "text",
                    "text": f"Here is the transcript:\n\n{transcript_text}"
                }
            ]
        }
    ]
    
    print("LLM_SERVICE: Sending request to LLM client...")
    try:
        # Ensure the method name matches your client (mock or real)
        # For Anthropic SDK, it's often client.messages.create
        # Our mock uses client.messagescreate directly
        response = LLM_CLIENT.messagescreate( 
            model="claude-3-haiku-20240307", # Or your preferred model like opus or sonnet
            max_tokens=3000, # Increased token limit for potentially long analysis
            # system=system_prompt, # Pass system prompt if your client/model supports it this way
            messages=messages_payload
        )
        
        # If the mock client directly returns the dict:
        analysis_data = response 
        
        # If using the real Anthropic SDK, you might need to parse response.content
        # For example:
        # if response.content and isinstance(response.content, list) and response.content[0].type == "text":
        #   try:
        #     analysis_data = json.loads(response.content[0].text)
        #   except json.JSONDecodeError:
        #     print("LLM_SERVICE: Failed to parse JSON from LLM response text.")
        #     # Fallback or re-raise error
        #     raise ValueError("LLM response was not valid JSON.")
        # else:
        #   print("LLM_SERVICE: Unexpected LLM response format.")
        #   raise ValueError("LLM response format not recognized.")

        return analysis_data
    except Exception as e:
        print(f"LLM_SERVICE: Error calling LLM: {e}")
        # import traceback # For debugging
        # print(traceback.format_exc())
        return {
            "table_of_contents": [], "key_terms": [], 
            "logical_flow": f"LLM call failed: {e}", 
            "summary": f"Summary generation failed: {e}"
        }
    
    # --- NEW FUNCTION FOR EXPLAINING SELECTED TEXT (MOCK) ---
def explain_selected_text_mock(selected_text: str, video_id_context: Optional[str] = None) -> dict:
    """
    Generates a MOCK explanation for a selected piece of text, optionally using video context.
    """
    print(f"LLM_SERVICE (Mock): explain_selected_text_mock called with text: '{selected_text[:100]}...' and video_id: {video_id_context}")
    
    # Simulate some processing time
    time.sleep(0.3 + random.random() * 0.4)

    explanation = f"This is a MOCK explanation for the selected text: \"{selected_text[:70]}...\". "
    if video_id_context:
        explanation += f"In the context of video ID '{video_id_context}', this segment likely refers to [mock contextual detail]. "
    explanation += "A real AI would provide a more detailed and accurate breakdown based on semantic understanding and the broader transcript content."

    # The response structure should be simple, e.g., just the explanation text
    return {"explanation": explanation}
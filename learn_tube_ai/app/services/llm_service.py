# learn_tube_ai/app/services/llm_service.py
import os
import time 
# import anthropic # Keep commented if not using the real SDK yet
import random

# --- Mock Anthropic Client ---
class MockAnthropicClient:
    def __init__(self, api_key=None):
        if api_key:
            print(f"MockAnthropicClient initialized WITH API key: {api_key[:5]}... (but will use placeholder data).")
        else:
            print("MockAnthropicClient initialized WITHOUT API key (will use placeholder data).")
        self.api_key = api_key

    def messagescreate(self, model, max_tokens, messages, system=None): # Added system parameter for potential future use
        print(f"MockAnthropicClient: messages.create called. Model: {model}, Max Tokens: {max_tokens}")
        # print(f"MockAnthropicClient: Received messages: {messages}")
        # print(f"MockAnthropicClient: Received system prompt: {system}")
        
        time.sleep(0.5 + random.random() * 0.5) # Simulate a variable delay (0.5 to 1.0 seconds)
        
        user_prompt_summary = "Generic user prompt"
        if messages and messages[0].get("role") == "user":
            content = messages[0].get("content")
            if isinstance(content, list): # Handle new complex content format
                user_prompt_summary = " ".join([block.get("text", "") for block in content if block.get("type") == "text"])
            elif isinstance(content, str):
                user_prompt_summary = content
        
        mock_response_text = f"This is a structured MOCK LLM response based on the prompt: '{user_prompt_summary[:70]}...'. "
        
        return {
            "table_of_contents": [
                {"title": "Mock ToC - Introduction", "timestamp_seconds": 10},
                {"title": "Mock ToC - Main Point", "timestamp_seconds": 60},
                {"title": "Mock ToC - Conclusion", "timestamp_seconds": 120}
            ],
            "key_terms": [
                {"term": "Mockup Data", "definition": "Placeholder information used for testing and development when real data or API access is not available. " + mock_response_text},
                {"term": "API Simulation", "definition": "Mimicking the behavior of an external API to allow frontend or other services to be built independently. " + mock_response_text}
            ],
            "logical_flow": "The mock logical flow is: 1. Initialization, 2. Input Processing, 3. Mock Response Generation, 4. Output. " + mock_response_text,
            "summary": "This is a concise mock summary, indicating that the LLM analysis was simulated due to the absence of a live API key or being in a test environment. " + mock_response_text
        }

# --- Global LLM Client (Mock or Real) ---
LLM_CLIENT = None
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    print("LLM_SERVICE: ANTHROPIC_API_KEY not found. Using MOCK LLM client.")
    LLM_CLIENT = MockAnthropicClient()
else:
    try:
        # When you're ready for the real client:
        # import anthropic
        # LLM_CLIENT = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print(f"LLM_SERVICE: ANTHROPIC_API_KEY found ({ANTHROPIC_API_KEY[:5]}...). Real client would be initialized (currently using mock).")
        LLM_CLIENT = MockAnthropicClient(api_key=ANTHROPIC_API_KEY) # Still using mock for now
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
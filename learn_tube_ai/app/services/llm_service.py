# learn_tube_ai/app/services/llm_service.py
import os
import json
# We will import 'anthropic' when you have the package and key
# from anthropic import Anthropic

# --- MOCK Anthropic client for now, until API key is ready ---
class MockAnthropicClient:
    def __init__(self, api_key=None):
        if api_key:
            print(f"MockAnthropicClient initialized with API key: {'*' * len(api_key)}")
        else:
            print("MockAnthropicClient initialized WITHOUT API key (will use placeholder data).")

    class MockMessages:
        def create(self, model, max_tokens, system, messages, temperature):
            print(f"Mock LLM call: model={model}, max_tokens={max_tokens}")
            print(f"System prompt: {system}")
            print(f"User message: {messages[0]['content'][:100]}...") # First 100 chars of user message

            class MockContent:
                def __init__(self, text):
                    self.text = text
            class MockResponse:
                def __init__(self, text_content):
                    self.content = [MockContent(text_content)]

            # Simulate a JSON response if the prompt asks for it
            if "json object" in system.lower() or "json object" in messages[0]['content'].lower():
                mock_json_data = {
                    "table_of_contents": [
                        {"title": "Mock Intro", "timestamp_seconds": 0},
                        {"title": "Mock Middle", "timestamp_seconds": 300}
                    ],
                    "key_terms": [
                        {"term": "Mock Term 1", "definition": "This is a mock definition."}
                    ],
                    "logical_flow": "This is a mock logical flow outline."
                }
                return MockResponse(json.dumps(mock_json_data))
            else:
                return MockResponse("This is a mock explanation from the LLM.")

    def __init__(self, api_key=None): # Main constructor for MockAnthropicClient
        self.messages = self.MockMessages()
        if api_key:
            print(f"MockAnthropicClient initialized with API key: {'*' * (len(api_key)-4) + api_key[-4:] if api_key and len(api_key) > 4 else 'key_present'}")
        else:
            print("MockAnthropicClient initialized WITHOUT API key (will use placeholder data).")


# Initialize Anthropic client (best to do this once)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Use the mock client if the real one isn't available or key is missing
if ANTHROPIC_API_KEY:
    try:
        from anthropic import Anthropic # Try to import the real one
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("Using REAL Anthropic client.")
    except ImportError:
        print("Anthropic SDK not installed. Using MOCK LLM client.")
        anthropic_client = MockAnthropicClient(api_key=ANTHROPIC_API_KEY) # Still pass key for print
else:
    print("ANTHROPIC_API_KEY not found. Using MOCK LLM client.")
    anthropic_client = MockAnthropicClient()


DEFAULT_LLM_MODEL = "claude-3-haiku-20240307"

def get_llm_completion(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    model_identifier: str = DEFAULT_LLM_MODEL,
    max_tokens: int = 4000,
    temperature: float = 0.2,
    is_json_output: bool = False
):
    print(f"--- Attempting LLM completion: {model_identifier} ---")
    messages = [{"role": "user", "content": prompt}]

    try:
        response_obj = anthropic_client.messages.create( # This will call either real or mock
            model=model_identifier,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
        )
        
        # Check if response_obj.content is a list and has elements
        if isinstance(response_obj.content, list) and len(response_obj.content) > 0:
             raw_text_response = response_obj.content[0].text
        else: # Handle cases where response_obj.content might not be as expected (e.g. if it's a string directly, or empty)
             # This case might indicate an issue with the mock or an unexpected real response format
             print("Warning: LLM response content is not in the expected list format.")
             raw_text_response = str(response_obj.content) # Fallback, or handle error

        if is_json_output:
            try:
                if raw_text_response.strip().startswith("```json"):
                    cleaned_response = raw_text_response.strip()[7:-3].strip()
                elif raw_text_response.strip().startswith("```"):
                    cleaned_response = raw_text_response.strip()[3:-3].strip()
                else:
                    cleaned_response = raw_text_response.strip()
                return json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from LLM: {e}")
                print(f"Problematic LLM output: {raw_text_response}")
                raise ValueError("LLM did not return valid JSON when expected.")
        return raw_text_response

    except Exception as e:
        print(f"Error during LLM interaction: {e}")
        # For a real app, re-raise or handle more gracefully
        # For mock, this might indicate an issue in the mock logic itself
        if isinstance(anthropic_client, MockAnthropicClient):
             print("Error occurred with Mock LLM client. Check mock implementation.")
        raise
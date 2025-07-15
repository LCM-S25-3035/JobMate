from app import create_app
from app.ai_agents.gemini_utils import call_gemini_api
import json

app = create_app()

with app.app_context():
    # A simple test prompt
    test_prompt = "Return a JSON with the key 'test' and value 'success'"
    
    # Call the API
    api_response = call_gemini_api(test_prompt)
    
    # Print the raw response structure
    print("API Response Type:", type(api_response))
    print("API Response Structure:")
    print(json.dumps(api_response, indent=2, default=str)[:1000])  # Show first 1000 chars
    
    # Test the extraction logic
    if (isinstance(api_response, dict) and
        'candidates' in api_response and
        len(api_response['candidates']) > 0 and
        'content' in api_response['candidates'][0] and
        'parts' in api_response['candidates'][0]['content'] and
        len(api_response['candidates'][0]['content']['parts']) > 0 and
        'text' in api_response['candidates'][0]['content']['parts'][0]):
        
        response_text = api_response['candidates'][0]['content']['parts'][0]['text']
        print("\nExtracted Text:")
        print(response_text[:200])  # First 200 chars
    else:
        print("\nFailed to extract text using current logic. Response structure doesn't match expectations.")

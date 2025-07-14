from app import create_app
from app.ai_agents.gemini_utils import call_gemini_api
import json
import re

app = create_app()

with app.app_context():
    # Test prompt with a simple JSON request
    test_prompt = """
    Please return a valid JSON object with the following structure:
    {
      "optimized_resume": "This is a sample optimized resume",
      "ats_score": 95,
      "implemented_suggestions": [0, 1, 2]
    }
    
    The response should be only the JSON object, with no additional text or formatting.
    """
    
    print("Sending test prompt to Gemini API...")
    api_response = call_gemini_api(test_prompt)
    
    print("\n=== RAW API RESPONSE STRUCTURE ===")
    print(f"Type: {type(api_response)}")
    if isinstance(api_response, dict):
        keys = list(api_response.keys())
        print(f"Keys: {keys}")
        
        if 'candidates' in api_response and len(api_response['candidates']) > 0:
            print("\n=== FIRST CANDIDATE CONTENT ===")
            candidate = api_response['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    raw_text = parts[0]['text']
                    print(f"Raw text length: {len(raw_text)}")
                    print(f"Raw text preview: {raw_text[:200]}...")
                    
                    print("\n=== JSON EXTRACTION TEST ===")
                    # Test JSON extraction
                    try:
                        # Direct parsing
                        result = json.loads(raw_text)
                        print("Direct JSON parsing worked!")
                        print(f"Extracted result: {json.dumps(result, indent=2)[:200]}...")
                    except json.JSONDecodeError:
                        print("Direct JSON parsing failed, trying alternatives...")
                        
                        # Try removing code blocks
                        if "```" in raw_text:
                            code_block_pattern = r"```(?:json)?(.*?)```"
                            code_match = re.search(code_block_pattern, raw_text, re.DOTALL)
                            if code_match:
                                cleaned_text = code_match.group(1).strip()
                                print(f"Extracted from code block: {cleaned_text[:100]}...")
                                
                                try:
                                    result = json.loads(cleaned_text)
                                    print("JSON parsing after code block extraction worked!")
                                    print(f"Extracted result: {json.dumps(result, indent=2)[:200]}...")
                                except json.JSONDecodeError as e:
                                    print(f"JSON parsing after code block extraction failed: {str(e)}")
                        
                        # Try regex extraction
                        first_brace = raw_text.find('{')
                        last_brace = raw_text.rfind('}')
                        
                        if first_brace >= 0 and last_brace >= 0 and last_brace > first_brace:
                            json_str = raw_text[first_brace:last_brace+1]
                            print(f"Extracted potential JSON: {json_str[:100]}...")
                            
                            try:
                                result = json.loads(json_str)
                                print("JSON parsing after regex extraction worked!")
                                print(f"Extracted result: {json.dumps(result, indent=2)[:200]}...")
                            except json.JSONDecodeError as e:
                                print(f"JSON parsing after regex extraction failed: {str(e)}")
                                
                                # One last attempt - fix quotes
                                fixed_str = json_str.replace("'", '"')
                                try:
                                    result = json.loads(fixed_str)
                                    print("JSON parsing after quote fixing worked!")
                                    print(f"Extracted result: {json.dumps(result, indent=2)[:200]}...")
                                except json.JSONDecodeError as e:
                                    print(f"All JSON parsing attempts failed: {str(e)}")

import requests
import time

# Test skills generator
print("Testing Skills Generator...")

skills_data = {
    'skills': 'Python, SQL, Machine Learning',
    'level': 'intermediate',
    'question_type': 'technical',
    'language': 'English',
    'count': '3'
}

try:
    response = requests.post(
        'http://127.0.0.1:5002/api/generate-questions-skills',
        data=skills_data,
        timeout=30
    )
    
    print(f"Skills Response Status: {response.status_code}")
    if response.status_code == 200:
        print("Skills generator working!")
        # The response should be HTML (template rendered)
        html_content = response.text
        
        # Check if our debug sections are present
        if "DEBUG: Generated Questions" in html_content:
            print("✅ Debug header found in skills response")
        
        if "Relevance &amp; Importance:" in html_content:
            print("✅ Relevance section found in skills response")
        
        if "Expected Answer:" in html_content:
            print("✅ Expected Answer section found in skills response")
            
        # Save the response for inspection
        with open('skills_response.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Saved skills response to skills_response.html")
        
    else:
        print(f"Skills generator failed: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"Error testing skills: {e}")

time.sleep(2)

# Test description generator
print("\nTesting Description Generator...")

desc_data = {
    'job_position': 'Senior Python Developer',
    'job_description': 'We are looking for a senior Python developer with 5+ years of experience in building scalable web applications using Django and Flask.',
    'level': 'Senior',
    'question_type': 'Technical',
    'count': '3',
    'language': 'English'
}

try:
    response = requests.post(
        'http://127.0.0.1:5002/api/generate-questions-description',
        data=desc_data,
        timeout=30
    )
    
    print(f"Description Response Status: {response.status_code}")
    if response.status_code == 200:
        print("Description generator working!")
        html_content = response.text
        
        # Check if our debug sections are present
        if "DEBUG: Generated Questions" in html_content:
            print("✅ Debug header found in description response")
        
        if "Relevance &amp; Importance:" in html_content:
            print("✅ Relevance section found in description response")
        
        if "Expected Answer:" in html_content:
            print("✅ Expected Answer section found in description response")
            
        # Save the response for inspection
        with open('description_response.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("Saved description response to description_response.html")
        
    else:
        print(f"Description generator failed: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"Error testing description: {e}")

print("\nTest completed!")

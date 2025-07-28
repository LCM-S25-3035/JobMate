from app import create_app

app = create_app()

if __name__ == '__main__':
    print("📋 Available URL routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    
    print("🔍 Looking specifically for /api/suggest_skills_salary route...")
    ai_routes = [str(rule) for rule in app.url_map.iter_rules() if '/api/suggest_skills_salary' in str(rule)]
    if ai_routes:
        print(f"  ✅ Found AI route: {ai_routes[0]}")
    else:
        print("  ❌ AI route not found!")
    
    print("🚀 Starting Flask application on port 5002...")
    app.run(debug=True, host='0.0.0.0', port=5002)
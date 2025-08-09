#!/bin/bash

# Enhanced Profile Setup Script for JobMate
echo "🚀 Setting up Enhanced Profile Module..."

# Create necessary directories
echo "📁 Creating upload directories..."
mkdir -p app/static/uploads/profiles
chmod 755 app/static/uploads/profiles

# Check if migration is needed
echo "🔍 Checking database setup..."
if [ -f "migrations/versions/enhanced_profile_001.py" ]; then
    echo "✅ Migration file found"
    echo "💡 Run 'flask db upgrade' to apply database changes"
else
    echo "⚠️  Migration file not found"
fi

# Check if templates exist
echo "🎨 Checking templates..."
if [ -f "templates/main/enhanced_profile.html" ]; then
    echo "✅ Enhanced profile template found"
else
    echo "❌ Enhanced profile template missing"
fi

# Check if routes are set up
echo "🛣️  Checking routes..."
if [ -f "app/main/profile_routes.py" ]; then
    echo "✅ Enhanced profile routes found"
else
    echo "❌ Enhanced profile routes missing"
fi

# Create default profile picture placeholder
echo "🖼️  Setting up default profile picture..."
if [ ! -f "app/static/uploads/profiles/default.png" ]; then
    echo "📝 Creating default profile picture placeholder..."
    echo "Default Profile Picture - Replace with actual image" > app/static/uploads/profiles/default.txt
    echo "💡 Add a default.png image to app/static/uploads/profiles/ for profile pictures"
fi

echo ""
echo "✨ Enhanced Profile Module Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Run: flask db upgrade (to apply database changes)"
echo "2. Add default.png to app/static/uploads/profiles/"
echo "3. Start your Flask application"
echo "4. Navigate to /profile → Enhanced Profile"
echo ""
echo "🔗 Features Available:"
echo "   • Profile picture upload/management"
echo "   • Social media links (LinkedIn, GitHub, Portfolio)"
echo "   • Password change functionality"
echo "   • Enhanced profile statistics"
echo "   • Professional profile interface"
echo ""
echo "📚 See docs/enhanced-profile-implementation.md for detailed documentation"

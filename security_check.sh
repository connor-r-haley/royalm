#!/bin/bash

echo "🔒 Security Check for GitHub Push"
echo "=================================="

# Check for .env files
echo "1. Checking for .env files..."
if find . -name ".env" -type f | grep -q .; then
    echo "   ❌ Found .env files:"
    find . -name ".env" -type f
    echo "   ⚠️  Remove these before pushing to GitHub!"
else
    echo "   ✅ No .env files found"
fi

# Check for API keys in code
echo ""
echo "2. Checking for API keys in code..."
if grep -r "sk-" . --exclude-dir=venv --exclude-dir=node_modules --exclude-dir=.git 2>/dev/null; then
    echo "   ❌ Found potential API keys in code!"
else
    echo "   ✅ No API keys found in code"
fi

# Check for OpenAI API keys
echo ""
echo "3. Checking for OpenAI API keys..."
if grep -r "OPENAI_API_KEY" . --exclude-dir=venv --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" --exclude="*.txt" 2>/dev/null | grep -v "your_openai_api_key_here"; then
    echo "   ❌ Found actual OpenAI API keys!"
else
    echo "   ✅ No actual OpenAI API keys found"
fi

# Check for News API keys
echo ""
echo "4. Checking for News API keys..."
if grep -r "NEWS_API_KEY" . --exclude-dir=venv --exclude-dir=node_modules --exclude-dir=.git --exclude="*.md" --exclude="*.txt" 2>/dev/null | grep -v "your_news_api_key_here"; then
    echo "   ❌ Found actual News API keys!"
else
    echo "   ✅ No actual News API keys found"
fi

# Check .gitignore
echo ""
echo "5. Checking .gitignore..."
if grep -q "\.env" .gitignore; then
    echo "   ✅ .env files are ignored"
else
    echo "   ❌ .env files are NOT ignored!"
fi

echo ""
echo "=================================="
echo "🔒 Security check complete!"
echo ""
echo "If all checks passed (✅), you're safe to push to GitHub!"
echo "If any checks failed (❌), fix the issues before pushing." 
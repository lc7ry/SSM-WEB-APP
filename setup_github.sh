#!/bin/bash

echo "🚀 Setting up GitHub repository for automatic deployment"
echo ""

# Check if remote origin exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Git remote 'origin' already exists"
    echo "Current remote URL: $(git remote get-url origin)"
    echo ""
    read -p "Do you want to update the remote URL? (y/n): " update_remote
    if [[ $update_remote =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub repository URL: " repo_url
        git remote set-url origin $repo_url
        echo "✅ Remote URL updated"
    fi
else
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin $repo_url
    echo "✅ Remote 'origin' added"
fi

echo ""
echo "📤 Pushing code to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! Your code has been pushed to GitHub"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to your GitHub repository"
    echo "2. Navigate to Settings → Secrets and variables → Actions"
    echo "3. Add the required secrets (see DEPLOYMENT_README.md)"
    echo "4. Push more changes to trigger automatic deployment!"
    echo ""
    echo "📖 For detailed instructions, see: DEPLOYMENT_README.md"
else
    echo ""
    echo "❌ Push failed. This might be because:"
    echo "1. The repository doesn't exist yet on GitHub"
    echo "2. You don't have push permissions"
    echo "3. The branch name is different (try 'master' instead of 'main')"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- Create the repository on GitHub first"
    echo "- Make sure you have push access"
    echo "- Check if the default branch is 'main' or 'master'"
fi

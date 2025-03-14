#!/bin/bash

# F1ClashAnalytics GitHub Repository Setup Script

echo "Setting up F1ClashAnalytics GitHub repository..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
else
    echo "Git repository already initialized."
fi

# Add all files to git
echo "Adding files to git..."
git add .

# Commit files
echo "Committing files..."
git commit -m "Initial commit of F1ClashAnalytics"

# Prompt for GitHub repository URL
echo ""
echo "Please enter your GitHub repository URL (e.g., https://github.com/username/F1ClashAnalytics.git):"
read repo_url

if [ -z "$repo_url" ]; then
    echo "Error: No repository URL provided."
    exit 1
fi

# Add remote repository
echo "Adding remote repository..."
git remote add origin $repo_url

# Push to GitHub
echo "Pushing to GitHub (main branch)..."
git push -u origin main

# Check if push was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "Success! F1ClashAnalytics has been pushed to GitHub."
    echo "Repository URL: $repo_url"
else
    echo ""
    echo "Error: Failed to push to GitHub. Please check your repository URL and try again."
    echo "You can manually push using: git push -u origin main"
fi

echo ""
echo "Next steps:"
echo "1. Visit Streamlit Cloud (https://streamlit.io/cloud)"
echo "2. Connect your GitHub repository"
echo "3. Deploy your app"
echo ""
echo "Happy analyzing!" 
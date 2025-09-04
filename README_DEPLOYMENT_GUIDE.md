# Deployment Guide: Uploading Your Flask App to GitHub and Deploying on PythonAnywhere

This guide will walk you through the steps to:

1. Create a GitHub repository and push your local Flask app code.
2. Deploy your Flask app on PythonAnywhere using the GitHub repository.

---

## Step 1: Create a GitHub Repository and Push Your Code

1. **Create a GitHub account** (if you don't have one):  
   https://github.com/join

2. **Create a new repository:**  
   - Go to https://github.com/new  
   - Enter a repository name (e.g., `car-meet-community`)  
   - Choose Public or Private  
   - Do NOT initialize with README, .gitignore, or license (we will push existing code)  
   - Click "Create repository"

3. **Initialize Git in your local project folder (if not already):**  
   Open your terminal/command prompt in your project directory and run:  
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Add the remote GitHub repository and push:**  
   Replace `<your-username>` and `<repo-name>` with your GitHub username and repository name:  
   ```
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 2: Deploy Flask App on PythonAnywhere

1. **Sign up / log in to PythonAnywhere:**  
   https://www.pythonanywhere.com/

2. **Clone your GitHub repo on PythonAnywhere:**  
   - Open a Bash console on PythonAnywhere dashboard  
   - Run:  
   ```
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```

3. **Set up a virtual environment and install dependencies:**  
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure your web app:**  
   - Go to the "Web" tab on PythonAnywhere  
   - Create a new web app, select Flask, and specify the path to your Flask app's `wsgi.py` or `app.py`  
   - Set environment variables (email credentials, secret keys) in the "Web" tab under "Environment Variables"  
   - Reload the web app

---

If you want, I can help you with the exact commands and configuration files for your project. Just let me know!

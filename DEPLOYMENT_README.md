# 🚀 Automatic Deployment Setup

This guide will help you set up automatic deployment to GitHub when you push changes to your repository.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Deployment Platform**: Choose one of the supported platforms:
   - Heroku
   - Render
   - Railway
   - Fly.io

## 🔧 Setup Instructions

### Step 1: Choose Your Deployment Platform

#### Option A: Heroku (Recommended for Flask apps)

1. **Create a Heroku account** at https://heroku.com
2. **Create a new app** in Heroku dashboard
3. **Get your API key**:
   - Go to Account Settings → API Key
   - Copy your API key

#### Option B: Render

1. **Create a Render account** at https://render.com
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Get your API key** from Account Settings

### Step 2: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add the following secrets**:

#### For Heroku:
```
HEROKU_API_KEY=your_heroku_api_key_here
HEROKU_APP_NAME=your_heroku_app_name
HEROKU_EMAIL=your_email@example.com
```

#### For Render:
```
RENDER_API_KEY=your_render_api_key_here
RENDER_SERVICE_ID=your_render_service_id
```

### Step 3: Push Your Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add automatic deployment"
   git push origin main
   ```

2. **Monitor deployment**:
   - Go to your repository → Actions tab
   - Watch the deployment workflow run
   - Check deployment status on your platform

## 📁 Files Created

- `.github/workflows/deploy.yml` - Heroku deployment
- `.github/workflows/deploy-render.yml` - Render deployment
- `DEPLOYMENT_README.md` - This guide

## 🔄 How It Works

1. **Push to main/master branch** → Triggers workflow
2. **Run tests** → Ensures code quality
3. **Deploy automatically** → Updates your live application
4. **Get notified** → Success/failure notifications

## 🧪 Testing Your Deployment

The workflow includes automated testing:

```bash
python test_hybrid_db.py
```

This ensures your database configuration works correctly before deployment.

## 🚨 Troubleshooting

### Common Issues:

1. **"Secret not found"**
   - Check that you added the secrets correctly
   - Ensure secret names match exactly

2. **"Deployment failed"**
   - Check the Actions logs for error details
   - Verify your platform credentials

3. **"Tests failing"**
   - Run `python test_hybrid_db.py` locally
   - Fix any database connection issues

### Manual Deployment

If automatic deployment fails, you can still deploy manually:

**Heroku:**
```bash
heroku login
git push heroku main
```

**Render:**
- Push to your connected branch
- Render will auto-deploy

## 📊 Monitoring

- **GitHub Actions**: View deployment history and logs
- **Platform Dashboard**: Monitor app performance and logs
- **Database**: Check data integrity after deployment

## 🔒 Security Notes

- Never commit sensitive data to your repository
- Use GitHub Secrets for all API keys and credentials
- Regularly rotate your API keys
- Monitor your deployment logs for security issues

## 🎯 Best Practices

1. **Test locally first** before pushing
2. **Use feature branches** for development
3. **Review changes** before merging to main
4. **Monitor deployments** regularly
5. **Keep dependencies updated**

## 📞 Support

If you encounter issues:

1. Check the GitHub Actions logs
2. Review platform-specific documentation
3. Verify your configuration matches this guide
4. Contact your deployment platform support

---

**Happy deploying! 🚀**

Your app will now automatically update whenever you push changes to GitHub!

# 🚀 Netlify Deployment Guide for Flask App

This guide will help you deploy your Flask application to Netlify with custom domain support.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Netlify Account**: Sign up at https://netlify.com
3. **Custom Domain**: sulistreetmeet.duckdns.org (already configured)

## 🔧 Setup Instructions

### Step 1: Connect to Netlify

1. **Go to Netlify Dashboard**: https://app.netlify.com
2. **Click "New site from Git"**
3. **Connect your GitHub repository**
4. **Configure build settings**:
   - **Branch**: `main` (or your default branch)
   - **Build command**: `bash build.sh`
   - **Publish directory**: `build`

### Step 2: Environment Variables

Add these environment variables in Netlify (Site settings → Environment variables):

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///carmeet_community.db
```

### Step 3: Deploy

1. **Click "Deploy site"**
2. **Wait for build completion** (may take 5-10 minutes)
3. **Your site will be available** at a Netlify subdomain (e.g., `random-name.netlify.app`)

### Step 4: Add Custom Domain

1. **Go to Site settings → Domain management**
2. **Click "Add custom domain"**
3. **Enter**: `sulistreetmeet.duckdns.org`
4. **Follow DNS setup instructions**:
   - Netlify will provide DNS records to add to DuckDNS
   - Add the provided CNAME or A records in your DuckDNS control panel

## 📁 Files Created

- `netlify.toml` - Netlify configuration
- `netlify/functions/app.py` - Serverless function handler
- `netlify/functions/requirements.txt` - Function dependencies
- `build.sh` - Build script
- `NETLIFY_DEPLOYMENT_README.md` - This guide

## 🔄 How It Works

1. **Build Process**: `build.sh` copies static files and database
2. **Serverless Functions**: Flask app runs as Netlify function
3. **Routing**: All requests redirected to the function
4. **Database**: SQLite database included in build

## 🧪 Testing Your Deployment

After deployment:

1. **Test the Netlify URL** first
2. **Check basic routes** work
3. **Verify database** connections
4. **Test custom domain** after DNS propagation

## 🚨 Troubleshooting

### Common Issues:

1. **Build fails**
   - Check build logs in Netlify dashboard
   - Verify `requirements.txt` dependencies
   - Ensure `build.sh` has execute permissions

2. **Function timeout**
   - Netlify functions have 10-second timeout
   - Optimize slow database queries
   - Consider using external database

3. **Database issues**
   - SQLite works but may have concurrency issues
   - Consider PostgreSQL add-on for production

4. **Custom domain not working**
   - Wait for DNS propagation (up to 24 hours)
   - Verify DNS records in DuckDNS
   - Check domain ownership verification

### Function Logs

Check function logs in Netlify dashboard under "Functions" tab.

## 📊 Monitoring

- **Deploy logs**: View in Netlify dashboard
- **Function logs**: Monitor serverless function performance
- **Analytics**: Enable Netlify Analytics for traffic data

## 🔒 Security Notes

- Never commit sensitive data to repository
- Use environment variables for secrets
- Regularly update dependencies
- Monitor function usage for costs

## 🎯 Best Practices

1. **Test locally** before pushing to GitHub
2. **Use feature branches** for development
3. **Monitor build times** and optimize if needed
4. **Set up automated deployments** from main branch
5. **Keep dependencies updated**

## 📞 Support

If you encounter issues:

1. Check Netlify deploy logs
2. Review function logs
3. Verify DNS configuration
4. Check DuckDNS domain status
5. Contact Netlify support

---

**Happy deploying! 🚀**

Your Flask app will be live at sulistreetmeet.duckdns.org once DNS propagates.

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database_manager_hybrid import db_manager
from permissions_manager import require_login
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/blog')
def blog_home():
    """Community blog/stories homepage"""
    try:
        # Get filter parameters
        category = request.args.get('category', 'all')
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page

        # Get blog posts
        posts = db_manager.get_blog_posts(per_page, offset, category if category != 'all' else None, featured_only)

        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM blog_posts WHERE Published = 1"
        count_params = []

        if category and category != 'all':
            count_query += " AND Category = ?"
            count_params.append(category)

        if featured_only:
            count_query += " AND Featured = 1"

        total_posts = db_manager.execute_query(count_query, count_params)[0][0]
        total_pages = (total_posts + per_page - 1) // per_page

        # Get unique categories
        categories = db_manager.execute_query("SELECT DISTINCT Category FROM blog_posts WHERE Category IS NOT NULL AND Published = 1 ORDER BY Category")

        # Get featured posts for sidebar
        featured_posts = db_manager.execute_query("""
            SELECT PostID, Title, CreatedDate FROM blog_posts
            WHERE Published = 1 AND Featured = 1
            ORDER BY CreatedDate DESC LIMIT 5
        """)

        return render_template('blog_home.html',
                             posts=posts,
                             categories=categories,
                             featured_posts=featured_posts,
                             category=category,
                             featured_only=featured_only,
                             page=page,
                             total_pages=total_pages)

    except Exception as e:
        logger.error(f"Blog home error: {e}")
        return render_template('blog_home.html', error="Error loading blog posts")

@blog_bp.route('/blog/post/<int:post_id>')
def blog_post(post_id):
    """Individual blog post view"""
    try:
        # Get blog post
        post = db_manager.get_blog_post(post_id)

        if not post:
            flash('Blog post not found', 'error')
            return redirect(url_for('blog.blog_home'))

        post = post[0]

        # Get author info
        author = db_manager.execute_query("""
            SELECT FirstName, LastName, Bio, ProfilePicture FROM members WHERE MemberID = ?
        """, (post[3],))  # AuthorID

        author = author[0] if author else None

        # Get comments
        comments = db_manager.get_comments('blog', post_id)

        # Increment view count (we'd need to add a Views column to blog_posts)
        # For now, we'll skip this

        # Get related posts
        related_posts = db_manager.execute_query("""
            SELECT PostID, Title, CreatedDate FROM blog_posts
            WHERE Published = 1 AND Category = ? AND PostID != ?
            ORDER BY CreatedDate DESC LIMIT 3
        """, (post[4], post_id))  # Category

        return render_template('blog_post.html',
                             post=post,
                             author=author,
                             comments=comments,
                             related_posts=related_posts)

    except Exception as e:
        logger.error(f"Blog post error: {e}")
        flash('Error loading blog post', 'error')
        return redirect(url_for('blog.blog_home'))

@blog_bp.route('/api/blog/post/<int:post_id>/like', methods=['POST'])
def toggle_blog_like(post_id):
    """Toggle like on a blog post"""
    try:
        user_id = request.form.get('user_id')  # For anonymous likes, we'd need session management
        if not user_id:
            return jsonify({'success': False, 'error': 'User authentication required'}), 401

        liked = db_manager.toggle_like(int(user_id), 'blog', post_id)

        # Get updated like count
        like_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM likes WHERE PostType = 'blog' AND PostID = ?",
            (post_id,)
        )[0][0]

        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })

    except Exception as e:
        logger.error(f"Toggle blog like error: {e}")
        return jsonify({'success': False, 'error': 'Failed to toggle like'}), 500

@blog_bp.route('/api/blog/post/<int:post_id>/comment', methods=['POST'])
def add_blog_comment(post_id):
    """Add a comment to a blog post"""
    try:
        content = request.form.get('content')
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')

        if not content or not content.strip():
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400

        if not author_name or not author_email:
            return jsonify({'success': False, 'error': 'Name and email are required'}), 400

        # For public comments, use system user ID
        system_user_id = 0

        db_manager.add_comment(content.strip(), system_user_id, 'blog', post_id, None)

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Add blog comment error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add comment'}), 500

@blog_bp.route('/blog/create', methods=['GET', 'POST'])
@require_login
def create_blog_post():
    """Create a new blog post (for authorized users)"""
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            tags = request.form.get('tags')
            featured = request.form.get('featured') == 'on'

            if not title or not content:
                flash('Title and content are required', 'error')
                return redirect(request.url)

            # Get current user
            user_id = request.current_user.id

            # Create blog post
            db_manager.add_blog_post(title, content, user_id, category, tags, featured)

            # Log activity
            db_manager.log_activity(user_id, 'blog_post_created', f'Created blog post: {title}')

            flash('Blog post created successfully!', 'success')
            return redirect(url_for('blog.blog_home'))

        # GET request - show form
        return render_template('create_blog_post.html')

    except Exception as e:
        logger.error(f"Create blog post error: {e}")
        flash('Error creating blog post', 'error')
        return redirect(url_for('blog.blog_home'))

def init_app(app):
    """Initialize the blog blueprint"""
    app.register_blueprint(blog_bp)

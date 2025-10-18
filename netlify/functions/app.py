import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main Flask app
from app import app

def handler(event, context):
    """
    Netlify function handler for Flask app
    """
    # Get the request path
    path = event.get('path', '/')

    # Remove the function path prefix
    if path.startswith('/.netlify/functions/app'):
        path = path.replace('/.netlify/functions/app', '', 1) or '/'

    # Create a WSGI environ dict
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'PATH_INFO': path,
        'QUERY_STRING': event.get('queryStringParameters', {}) or '',
        'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': str(len(event.get('body', '') or '')),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers
    for header, value in event.get('headers', {}).items():
        environ[f'HTTP_{header.upper().replace("-", "_")}'] = value

    # Handle query parameters
    if event.get('queryStringParameters'):
        query_parts = []
        for key, value in event.get('queryStringParameters').items():
            query_parts.append(f'{key}={value}')
        environ['QUERY_STRING'] = '&'.join(query_parts)

    # Response collector
    response_data = []
    response_headers = []
    response_status = None

    def start_response(status, headers, exc_info=None):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers

    # Call the Flask app
    try:
        result = app(environ, start_response)
        response_data = b''.join(result)
    except Exception as e:
        # Error handling
        response_status = '500 Internal Server Error'
        response_headers = [('Content-Type', 'text/plain')]
        response_data = str(e).encode()

    # Format response for Netlify
    return {
        'statusCode': int(response_status.split()[0]),
        'headers': dict(response_headers),
        'body': response_data.decode('utf-8', errors='ignore')
    }

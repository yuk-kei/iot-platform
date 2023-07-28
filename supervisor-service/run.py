from application import create_app

app = create_app()


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # If you want all HTTP converted to HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['SYS_CONTROL_PORT'])

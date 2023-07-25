from application import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # If you want all HTTP converted to HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['DATA_WIZARD_PORT'])

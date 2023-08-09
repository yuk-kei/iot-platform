from application import create_app


app = create_app()

if __name__ == '__main__':
    app.run()
    # # app.run(host='127.0.0.1', port=5000)
    # socketio.run(app, host='127.0.0.1', port=5000)
    # # app.run(host='0.0.0.0', port=app.config['DATA_WIZARD_PORT'])
    # socketio.run(app, host='0.0.0.0', port=app.config['DATA_WIZARD_PORT'], debug=True)

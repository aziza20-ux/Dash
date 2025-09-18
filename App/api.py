from . import create_app
app = create_app()
application = app.server  # Expose the WSGI server instance for deployments
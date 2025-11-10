# run.py — tiny launcher used in development.
# Creates the Flask app via the factory and starts the dev server.

from app import create_app

# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    # In this insecure branch, DEBUG may be True via .env (not for production).
    app.run()

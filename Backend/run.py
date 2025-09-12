from app import create_app


# This script is the entry point for running the Flask application.
# app = create_app("development") => Initializes the Flask application with the "development" configuration.
app = create_app("development")

if __name__ == "__main__":
    # Run the Flask application with debug mode enabled.
    app.run(debug=True, host="0.0.0.0", port=5555)

from app import create_app, db

# Create Flask app using the factory
app = create_app()

# Optional: Allow "flask shell" to access db, models, etc.
@app.shell_context_processor
def make_shell_context():
    return {"db": db}

from web_app import app

if __name__ == "__main__":
    print("Starting Flask server...")
    print("Your app will be available at: http://127.0.0.1:5000")
    app.run(debug=True)


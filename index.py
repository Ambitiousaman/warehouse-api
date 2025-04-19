from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Welcome to Warehouse API"}

@app.route('/welcome')
def welcome():
    return {"message": "Hello from the Warehouse API"}

if __name__ == '__main__':
    app.run()
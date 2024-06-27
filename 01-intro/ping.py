from flask import Flask
app = Flask("ping")

@app.route("/ping",methods=['GET'])
def ping():
    return "PONG"

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=9696)
    
    
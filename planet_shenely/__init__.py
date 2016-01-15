import os.path
from main import app

if __name__ == "__main__":
    app.config["DATABASE"] = os.path.join(os.path.dirname(__file__),
                                          "data.json"),
    
    app.run(debug=True)
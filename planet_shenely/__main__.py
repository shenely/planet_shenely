import os.path
import argparse

from main import app

SERVER_NAME = "%s:%d"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Welcome to Planet Shenely!")
    
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable or disable debug mode")
    parser.add_argument("-f", "--file", type=str,
                        default=os.path.join(os.path.dirname(__file__),
                                             "data.json"),
                        help="the file to store data")
    parser.add_argument("-o", "--host", type=str, default="localhost",
                        help="the hostname to listen on")
    parser.add_argument("-p","--port", type=int, default=8080,
                        help="the port of the webserver")
    
    args = vars(parser.parse_args())
    
    app.config["SERVER_NAME"] = SERVER_NAME % (args["host"], args["port"])
    app.config["DATABASE"] = args["file"]

    app.run(debug=args["debug"])
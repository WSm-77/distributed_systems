from server.server import Server

def app():
    server = Server()
    server.run()

if __name__ == "__main__":
    app()

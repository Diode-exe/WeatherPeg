import webbrowser

class WebOpen:
    @staticmethod
    def opener(port):
        webbrowser.open(f"http://localhost:{port}/weather")
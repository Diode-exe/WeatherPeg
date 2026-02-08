import webbrowser

class WebOpen:
    """Helper class to open the web browser to a specific URL."""
    @staticmethod
    def opener(port):
        """Open the web browser to the weather page."""
        webbrowser.open(f"http://localhost:{port}/weather")
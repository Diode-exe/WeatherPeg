import logging

class Config():
    """Class to read configuration values from a text file"""
    def get_config_bool(self, key):
        """Read a boolean config value (0 or 1) from the config file"""
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Convert to boolean (0 = False, 1 = True)
                        return value == "1"
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return False
        return False  # Default to False if not found

    def get_config_port(self):
        """Read the port number from the config file"""
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.lower().startswith("port:"):
                        value = line.split(":", 1)[1].strip()
                        try:
                            return int(value)  # return as integer
                        except ValueError:
                            logging.error(f"Invalid port value: {value}")
                            return None
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return None

        return None  # Default if "port:" not found

    def get_config_value(self, key, default=None):
        """Read a config value from the config file, with optional default"""
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Try to convert to int if possible
                        if value.isdigit():
                            return int(value)
                        try:
                            return float(value)  # handles decimal numbers
                        except ValueError:
                            return value  # fallback to raw string
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return default
        return default

if __name__ == "__main__":
    print("This is a module, and not meant to be run directly")

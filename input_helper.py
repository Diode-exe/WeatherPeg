def commander(command):
        if command == "help":
            fileloc = "txt/helpfile.txt"
            try:
                with open (fileloc, "r") as helpfile:
                    print(helpfile.read())
            except FileNotFoundError:
                print("Help file not found!")
                
def input_loop():
    while True:
        command = input("weather: ")
        commander(command)
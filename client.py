import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import json
import threading

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 65432

class NumberGuessingGame:
    def __init__(self, master, username):
        self.master = master
        self.master.title(f"Number Guessing Game - {username}")
        self.username = username

        self.guess_label = tk.Label(master, text=f"Enter your guess (1-20), {username}:")
        self.guess_label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.button = tk.Button(master, text="Guess", command=self.send_guess)
        self.button.pack()

        self.response_label = tk.Label(master, text="")
        self.response_label.pack()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))
        self.client.sendall(username.encode())
        
        threading.Thread(target=self.receive_messages).start()

    def send_guess(self):
        guess = self.entry.get()
        self.client.sendall(json.dumps({"guess": guess}).encode())

    def receive_messages(self):
        while True:
            response = self.client.recv(1024).decode()
            if response:
                response_data = json.loads(response)
                message = response_data.get("message", "Invalid response from server")
                self.response_label.config(text=message)
                
                # Check if the game is won
                if response_data.get("winner"):
                    self.show_winner_screen(response_data)
                    self.client.close()
                    break

    def show_winner_screen(self, response_data):
            winner_message = f"Congratulations {response_data['winner']}!\n" \
                            f"You guessed correctly in {response_data['time_taken']:.2f} seconds.\n" \
                            f"Number of guesses: {response_data['guesses']}\n"

            accuracy = 100 / response_data['guesses']  # Calculating accuracy
            winner_message += f"Accuracy: {accuracy:.2f}%"

            # Display a message box with winner details
            messagebox.showinfo("Winner!", winner_message)

    def start_client(username):
        root = tk.Tk()
        game = NumberGuessingGame(root, username)
        root.mainloop()

    def main():
        usernames = []
        for i in range(2):
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            username = simpledialog.askstring("Input", f"Enter name for Player {i + 1}:")
            root.destroy()  # Destroy the root window
            if username:
                usernames.append(username)
        
        if len(usernames) == 2:
            player1_thread = threading.Thread(target=start_client, args=(usernames[0],))
            player2_thread = threading.Thread(target=start_client, args=(usernames[1],))
            
            player1_thread.start()
            player2_thread.start()

            player1_thread.join()
            player2_thread.join()
        else:
            print("Both players need to enter their names to start the game.")

    if __name__ == "__main__":
        main()
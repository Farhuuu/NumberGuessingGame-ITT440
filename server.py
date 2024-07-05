import socket
import threading
import json
import random
import time

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 65432

clients = []
scores = {}
target_number = random.randint(1, 20)
print(f"Target number set for guessing: {target_number}")
current_turn = None
start_time = None
game_over = False  # Flag to indicate if game is over

def broadcast(message):
    for client in clients:
        try:
            client['conn'].sendall(json.dumps(message).encode())
        except socket.error as e:
            print(f"Error sending message to {client['username']}: {e}")
            client['conn'].close()
            clients.remove(client)

def handle_client(client):
    global current_turn, start_time, game_over
    conn = client['conn']
    addr = client['addr']
    username = client['username']
    print(f"New connection: {addr} ({username})")
    conn.sendall(json.dumps({"message": f"Welcome {username} to the Number Guessing Game!"}).encode())
    
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            
            if current_turn != username:
                conn.sendall(json.dumps({"message": "It's not your turn yet!"}).encode())
                continue
            
            guess = json.loads(data).get("guess")
            if guess:
                guess = int(guess)
                print(f"{username} guessed: {guess}")
                if guess < target_number:
                    response = {"message": f"{username} guessed too low!"}
                elif guess > target_number:
                    response = {"message": f"{username} guessed too high!"}
                else:
                    end_time = time.time()
                    time_taken = end_time - start_time
                    response = {
                        "message": f"{username} guessed correctly!",
                        "winner": username,
                        "time_taken": time_taken,
                        "guesses": len(scores[username]['guesses']) + 1  # Include the correct guess
                    }
                    broadcast(response)
                    game_over = True  # Set game over flag
                    conn.close()
                    clients.remove(client)
                    break
                scores[username]['guesses'].append(guess)
                broadcast(response)
                # Switch turns
                current_turn = [client['username'] for client in clients if client['username'] != username][0]
                broadcast({"message": f"It's {current_turn}'s turn now!"})
        except (socket.error, json.JSONDecodeError) as e:
            print(f"Error: {e}")
            break
    
    print(f"Connection closed: {addr} ({username})")
    conn.close()

def start_server():
    global current_turn, start_time, game_over
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        username = conn.recv(1024).decode()
        client = {'conn': conn, 'addr': addr, 'username': username}
        clients.append(client)
        scores[username] = {'guesses': []}
        
        if current_turn is None:
            current_turn = username
            start_time = time.time()
            conn.sendall(json.dumps({"message": f"It's your turn, {username}!"}).encode())
        
        threading.Thread(target=handle_client, args=(client,)).start()

        if game_over:
            break  # Exit the loop if game over

if __name__ == "__main__":
    start_server()

# client/client.py

import threading
import time
import requests

SERVER_URL = "http://127.0.0.1:5000"  # Flask server URL


class ChatClient:
    """
    Simple terminal-based chat client that talks to the Flask server.

    Endpoints used:
      - POST /signup
      - POST /login
      - POST /send
      - GET  /messages?after_id=X
    """

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.username = None
        self.last_message_id = 0
        self._stop_event = threading.Event()

    # ---------- Auth ----------

    def signup(self) -> None:
        """
        Create a new account by calling /signup.
        """
        print("\n=== Create New Account ===")
        username = input("Choose a username: ").strip()
        password = input("Choose a password: ").strip()

        if not username or not password:
            print(" Username and password cannot be empty.")
            return

        try:
            resp = requests.post(
                f"{self.server_url}/signup",
                json={"username": username, "password": password},
                timeout=5,
            )
        except requests.RequestException as exc:
            print(f" Error: could not reach server: {exc}")
            return

        if resp.status_code == 201:
            print(" Account created successfully!")
        else:
            # Try to show server message if available
            try:
                data = resp.json()
                msg = data.get("message", "Unknown error from server.")
            except Exception:
                msg = f"HTTP {resp.status_code}"
            print(f" Signup failed: {msg}")

    def login(self) -> bool:
        """
        Log in by calling /login.
        """
        print("\n=== Login ===")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if not username or not password:
            print("  Username and password cannot be empty.")
            return False

        try:
            resp = requests.post(
                f"{self.server_url}/login",
                json={"username": username, "password": password},
                timeout=5,
            )
        except requests.RequestException as exc:
            print(f" Error: could not reach server: {exc}")
            return False

        if resp.status_code == 200:
            self.username = username
            print(" Login successful.")
            return True

        try:
            data = resp.json()
            msg = data.get("message", "Unknown error from server.")
        except Exception:
            msg = f"HTTP {resp.status_code}"
        print(f" Login failed: {msg}")
        return False

    # ---------- Messaging ----------

    def send_message(self, content: str) -> None:
        """
        Send a message through /send.
        """
        if not self.username:
            print("  You must be logged in to send messages.")
            return

        try:
            resp = requests.post(
                f"{self.server_url}/send",
                json={"username": self.username, "content": content},
                timeout=5,
            )
        except requests.RequestException as exc:
            print(f" Error sending message: {exc}")
            return

        if resp.status_code != 201:
            try:
                data = resp.json()
                msg = data.get("message", "Unknown error from server.")
            except Exception:
                msg = f"HTTP {resp.status_code}"
            print(f" Error from server: {msg}")

    def receive_messages_loop(self) -> None:
        """
        Background loop that polls /messages for new messages.
        """
        print(" Listening for new messages...\n")

        while not self._stop_event.is_set():
            try:
                resp = requests.get(
                    f"{self.server_url}/messages",
                    params={"after_id": self.last_message_id},
                    timeout=5,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    messages = data.get("messages", [])

                    for msg in messages:
                        msg_id = msg["id"]
                        sender = msg["sender"]
                        content = msg["content"]
                        timestamp = msg["timestamp"]

                        # Update last seen message id
                        if msg_id > self.last_message_id:
                            self.last_message_id = msg_id

                        # Print nicely
                        if sender == self.username:
                            print(f"[You @ {timestamp}]: {content}")
                        else:
                            print(f"[{sender} @ {timestamp}]: {content}")

                else:
                    print(f"Error fetching messages: HTTP {resp.status_code}")
            except requests.RequestException:
                print(" Could not contact server for new messages.")

            # Wait a bit before polling again
            time.sleep(1.5)

    # ---------- Main interaction ----------

    def run(self) -> None:
        """
        Main entry point: show menu, login/signup, then enter chat loop.
        """
        print("=== Chatroom Client ===")
        print(f"Server: {self.server_url}\n")

        # Menu: login / signup
        while True:
            print("1) Login")
            print("2) Create account")
            print("3) Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                if self.login():
                    break
            elif choice == "2":
                self.signup()
            elif choice == "3":
                print("Goodbye.")
                return
            else:
                print("  Invalid option. Please choose 1, 2, or 3.\n")

        # Once logged in, start background thread for receiving messages
        receiver_thread = threading.Thread(
            target=self.receive_messages_loop,
            daemon=True,
        )
        receiver_thread.start()

        print("\n=== You are now in the chatroom ===")
        print("Type your message and press Enter to send.")
        print("Press Ctrl+C to exit.\n")

        try:
            while True:
                msg = input()
                msg = msg.strip()
                if msg:
                    self.send_message(msg)
        except KeyboardInterrupt:
            print("\n Exiting chat...")
            self._stop_event.set()
            receiver_thread.join(timeout=2)
           


def main():
    client = ChatClient(SERVER_URL)
    client.run()


if __name__ == "__main__":
    main()

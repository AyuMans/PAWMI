import os
from core.assistant import Assistant
from dotenv import load_dotenv

def main():
    load_dotenv()
    print("PAWMI ONLIiNE")
    
    assistant = Assistant()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "goodbye"]:
            print("PAWMI: Goodbye.")
            break
        try:
            response = assistant.ask(user_input)
            print(f"PAWMI: {response}")
        except Exception as e:
            print(f"PAWMI: I have encountered an error: {e}")
            
if __name__ == "__main__":
    main()
    
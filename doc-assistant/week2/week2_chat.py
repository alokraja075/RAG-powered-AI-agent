# week2_chat.py
# The chat loop. Imports the bedrock_client module we just wrote.
# Run this with: python week2_chat.py

from bedrock_client import get_bedrock_client, stream_response

def main():
    print("Enterprise Doc Assistant — Week 2")
    print("Type your message and press Enter. Type 'quit' to exit.\n")

    client = get_bedrock_client()

    conversation_history = []
    print(conversation_history)

    while True:  
        user_input = input("You: ").strip()   

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        print("Assistant: ", end="", flush=True)
        assistant_reply = stream_response(client, conversation_history)


        conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })
        turns = len(conversation_history) // 2
        print(f"  [{turns} turn(s) in memory]\n")


if __name__ == "__main__":
    main()
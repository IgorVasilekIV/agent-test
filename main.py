from openai import AsyncOpenAI, OpenAIError
import asyncio

from src import memory

session = memory.create_hash()
client = AsyncOpenAI(api_key="smthng", base_url="http://10.69.42.4:8080/v1", timeout=60)

async def main():
    mem = await memory.load_memory(session)
    messages = [memory.SYS_PROMPT] + mem

    try:
        response = await client.chat.completions.create(
            model="YandexGPT-4",
            messages=messages
        )
        reply = response.choices[0].message
        print("\nAssistant:", reply.content)

        await memory.append_memory(session, {"role": "assistant", "content": reply.content})

    except OpenAIError as e:
        print(f"\nError during OpenAI API call: {e}")
        
async def list_models():
    try:
        models = await client.models.list()
        if not models.data:
            print("No models available.")
            return
        
        print("\nAvailable Models:")
        for model in models.data:
            print(f"- {model.id}")
    
    except OpenAIError as e:
        print(f"\nError fetching models: {e}")

if __name__ == "__main__":
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if user_input.strip() == "":
                continue
            if user_input.lower() == "/models":
                asyncio.run(list_models())
                continue
            
            asyncio.run(memory.append_memory(session, {"role": "user", "content": user_input}))
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break
from openai import AsyncOpenAI, OpenAIError
import asyncio
import contextlib

from src import memory

session = memory.create_hash()
client = AsyncOpenAI(api_key="smthng", base_url="http://10.69.42.4:8080/v1", timeout=60)

async def main():
    mem = await memory.load_memory(session)
    messages = [memory.SYS_PROMPT] + mem
    full_reply = ""
    cancelled = False

    try:
        response = await client.chat.completions.create(
            model="YandexGPT-4",
            messages=messages,
            temperature=0.6,
            stream=True
        )
        print("\nAssistant: ", end="", flush=True)
        async for chunk in response:
            if cancelled:
                break
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_reply += delta.content
                print(delta.content, end="", flush=True)
        print()

    except OpenAIError as e:
        print(f"\nError during OpenAI API call: {e}")
    except asyncio.CancelledError:
        cancelled = True
    finally:
        if full_reply:
            await memory.append_memory(session, {"role": "assistant", "content": full_reply})
        else:
            await memory.append_memory(session, {"role": "system", "content": "[Response was cancelled by user]"})
        
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
    loop = asyncio.new_event_loop()
    task = None

    try:
        while True:
            try:
                user_input = input("\nYou: ")
            except (KeyboardInterrupt, EOFError):
                if task and not task.done():
                    task.cancel()
                    print("\n[Cancelled]")
                    continue
                print("\nExiting...")
                break

            if user_input.lower() in ["exit", "quit"]:
                if task and not task.done():
                    task.cancel()
                break

            if user_input.strip() == "":
                continue
            if user_input.lower() == "/models":
                loop.run_until_complete(list_models())
                continue

            loop.run_until_complete(memory.append_memory(session, {"role": "user", "content": user_input}))
            task = loop.create_task(main())
            try:
                loop.run_until_complete(task)
            except (KeyboardInterrupt, asyncio.CancelledError):
                if task and not task.done():
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        loop.run_until_complete(task)
                print("\n[Cancelled]")
    finally:
        loop.close()
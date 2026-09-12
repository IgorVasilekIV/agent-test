import json
import secrets
import os
from typing import Dict, Any
from pathlib import Path
import aiofiles

SYS_PROMPT = {"role": "system", "content": "The correspondence history is provided below. Base your response on it."}

data_dir = Path("~/.local/share/agent").expanduser()
data_dir.mkdir(parents=True, exist_ok=True)
(data_dir / "memory").mkdir(parents=True, exist_ok=True)

def create_hash():
    return secrets.token_hex(12)

async def load_memory(hash_id: str) -> list[Dict[str, Any]]:
    path = f"{data_dir}/memory/mem-{hash_id}.jsonl"
    if not os.path.exists(path):
        return []
    
    memory_list = []
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        async for line in f:
            line = line.strip()
            if line:
                memory_list.append(json.loads(line))
                
    return memory_list
async def append_memory(hash_id: str, data: Dict[str, Any]) -> None:
    path = f"{data_dir}/memory/mem-{hash_id}.jsonl"
    async with aiofiles.open(path, "a", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False) + "\n")
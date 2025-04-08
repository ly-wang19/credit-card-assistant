"""
LLM适配器
提供大语言模型接口
"""

from typing import List, Dict
import httpx
# from ..config import DEEPSEEK_API_KEY

class DeepSeekAdapter:
    """DeepSeek API适配器"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json={"input": text}
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """发送聊天消息"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": messages
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"] 
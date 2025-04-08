"""
DeepSeek API适配器
实现与DeepSeek API的交互功能
"""

from typing import List, Dict, Optional
import httpx
import logging
from config import settings

# 设置日志记录器
logger = logging.getLogger(__name__)

class DeepSeekAdapter:
    """DeepSeek API适配器类"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
            
        self.api_base = settings.DEEPSEEK_API_BASE
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        logger.info("DeepSeek适配器初始化完成")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本的向量表示"""
        try:
            logger.info(f"获取文本向量表示，文本数量: {len(texts)}")
            response = await self.client.post(
                "/embeddings",
                json={
                    "input": texts,
                    "model": "text-embedding-ada-002"
                }
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except httpx.HTTPError as e:
            logger.error(f"获取向量表示失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"获取向量表示时发生错误: {str(e)}")
            raise
    
    async def chat_completion(self, messages: List[Dict[str, str]], 
                            temperature: float = 0.7) -> str:
        """生成对话回复"""
        try:
            logger.info("开始生成对话回复")
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info("成功生成对话回复")
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            logger.error(f"生成对话回复失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"生成对话回复时发生错误: {str(e)}")
            raise
    
    async def generate_card_recommendation(self, user_profile: Dict) -> Dict:
        """生成信用卡推荐"""
        try:
            logger.info("开始生成信用卡推荐")
            prompt = self._build_recommendation_prompt(user_profile)
            response = await self.chat_completion([
                {"role": "system", "content": "你是一个专业的信用卡推荐助手"},
                {"role": "user", "content": prompt}
            ])
            return self._parse_recommendation_response(response)
        except Exception as e:
            logger.error(f"生成信用卡推荐时发生错误: {str(e)}")
            raise
    
    def _build_recommendation_prompt(self, user_profile: Dict) -> str:
        """构建推荐提示词"""
        return f"""
        请根据以下用户信息推荐最适合的信用卡：
        年龄：{user_profile.get('age')}
        年收入：{user_profile.get('annual_income')}
        消费习惯：{user_profile.get('spending_habits')}
        主要需求：{user_profile.get('needs')}
        """
    
    def _parse_recommendation_response(self, response: str) -> Dict:
        """解析推荐响应"""
        return {
            "recommended_cards": [],
            "reasoning": response
        }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose() 
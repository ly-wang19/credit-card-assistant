"""
智能体核心
实现对话管理和状态处理的核心功能
"""

from typing import Dict, List, Optional
from enum import Enum
from llm_service.deepseek_adapter import DeepSeekAdapter
from rag_service.retriever import RAGRetriever
from knowledge_base.manager import KnowledgeBaseManager

class AgentState(Enum):
    """智能体状态枚举"""
    INITIAL = "initial"  # 初始状态
    COLLECTING_INFO = "collecting_info"  # 收集用户信息
    RECOMMENDING = "recommending"  # 推荐信用卡
    EXPLAINING = "explaining"  # 解释信用卡详情
    COMPARING = "comparing"  # 比较信用卡
    FINAL = "final"  # 最终状态

class CreditCardAgent:
    """信用卡智能体类"""
    
    def __init__(self):
        self.state = AgentState.INITIAL
        self.llm_adapter = DeepSeekAdapter()
        self.retriever = RAGRetriever()
        self.kb_manager = KnowledgeBaseManager()
        self.user_profile = {}
        self.conversation_history = []
    
    async def process_message(self, message: str) -> str:
        """处理用户消息"""
        # 更新对话历史
        self.conversation_history.append({"role": "user", "content": message})
        
        # 根据当前状态处理消息
        response = await self._handle_state(message)
        
        # 更新对话历史
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    async def _handle_state(self, message: str) -> str:
        """根据当前状态处理消息"""
        if self.state == AgentState.INITIAL:
            return await self._handle_initial_state(message)
        elif self.state == AgentState.COLLECTING_INFO:
            return await self._handle_collecting_info(message)
        elif self.state == AgentState.RECOMMENDING:
            return await self._handle_recommending(message)
        elif self.state == AgentState.EXPLAINING:
            return await self._handle_explaining(message)
        elif self.state == AgentState.COMPARING:
            return await self._handle_comparing(message)
        else:
            return "抱歉，我遇到了一个未知状态。让我们重新开始对话吧。"
    
    async def _handle_initial_state(self, message: str) -> str:
        """处理初始状态"""
        self.state = AgentState.COLLECTING_INFO
        return """
        欢迎使用信用卡推荐助手！为了给您提供最合适的信用卡推荐，我需要了解一些基本信息：
        
        1. 您的年龄范围是？
        2. 您的年收入大约是多少？
        3. 您的主要消费场景是什么？（如购物、旅游、餐饮等）
        4. 您对信用卡的主要需求是什么？（如积分、优惠、额度等）
        
        请依次回答这些问题，我会根据您的需求推荐最适合的信用卡。
        """
    
    async def _handle_collecting_info(self, message: str) -> str:
        """处理信息收集状态"""
        # 使用LLM提取用户信息
        extracted_info = await self._extract_user_info(message)
        self.user_profile.update(extracted_info)
        
        # 检查是否收集到足够的信息
        if self._has_enough_info():
            self.state = AgentState.RECOMMENDING
            return await self._generate_recommendation()
        else:
            return self._get_next_question()
    
    async def _handle_recommending(self, message: str) -> str:
        """处理推荐状态"""
        if "详情" in message or "介绍" in message:
            self.state = AgentState.EXPLAINING
            return await self._explain_card_details(message)
        elif "比较" in message:
            self.state = AgentState.COMPARING
            return await self._compare_cards(message)
        else:
            return "您是想了解某张卡的详情，还是想比较不同的信用卡？"
    
    async def _handle_explaining(self, message: str) -> str:
        """处理解释状态"""
        # 检索相关文档
        docs = await self.retriever.retrieve(message)
        
        # 生成解释
        response = await self.llm_adapter.chat_completion([
            {"role": "system", "content": "你是一个专业的信用卡顾问"},
            {"role": "user", "content": f"请根据以下信息解释这张信用卡：\n{docs[0]['content']}"}
        ])
        
        return response
    
    async def _handle_comparing(self, message: str) -> str:
        """处理比较状态"""
        # 提取要比较的信用卡
        card_names = self._extract_card_names(message)
        
        # 检索相关文档
        docs = []
        for card_name in card_names:
            card_docs = await self.retriever.retrieve(card_name)
            if card_docs:
                docs.append(card_docs[0])
        
        # 生成比较结果
        response = await self.llm_adapter.chat_completion([
            {"role": "system", "content": "你是一个专业的信用卡比较专家"},
            {"role": "user", "content": f"请比较以下信用卡：\n{chr(10).join(doc['content'] for doc in docs)}"}
        ])
        
        return response
    
    async def _extract_user_info(self, message: str) -> Dict:
        """提取用户信息"""
        response = await self.llm_adapter.chat_completion([
            {"role": "system", "content": "你是一个信息提取专家"},
            {"role": "user", "content": f"从以下文本中提取年龄、收入和消费信息：{message}"}
        ])
        
        # 这里需要根据实际响应格式进行解析
        return {}
    
    def _has_enough_info(self) -> bool:
        """检查是否收集到足够的信息"""
        required_fields = ["age", "annual_income", "spending_habits", "needs"]
        return all(field in self.user_profile for field in required_fields)
    
    def _get_next_question(self) -> str:
        """获取下一个问题"""
        if "age" not in self.user_profile:
            return "请问您的年龄范围是？"
        elif "annual_income" not in self.user_profile:
            return "请问您的年收入大约是多少？"
        elif "spending_habits" not in self.user_profile:
            return "您的主要消费场景是什么？（如购物、旅游、餐饮等）"
        else:
            return "您对信用卡的主要需求是什么？（如积分、优惠、额度等）"
    
    async def _generate_recommendation(self) -> str:
        """生成信用卡推荐"""
        return await self.llm_adapter.generate_card_recommendation(self.user_profile)
    
    def _extract_card_names(self, message: str) -> List[str]:
        """提取信用卡名称"""
        # 这里需要实现具体的提取逻辑
        return [] 
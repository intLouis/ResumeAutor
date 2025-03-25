import os

from exceptiongroup import catch
from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_deepseek import ChatDeepSeek
import requests
from langchain.prompts import PromptTemplate

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = "sk-a6ca73fb7c7b4f549d9ff068f37b9b26"

# 初始化大模型
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_retries=2,
    # other params...
)


class ECommerceAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._init_tools()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self._create_agent()
        self.agent_executor = self._create_executor()

    def generate_image(self, image_prompt: str) -> str:
        """Generate image based on prompt and save to local file"""
        resp = requests.get(f'https://image.pollinations.ai/prompt/${image_prompt}')
        import uuid
        file_name = f'{uuid.uuid4()}.jpg'
        with open(file_name, 'wb') as f:
            f.write(resp.content)
        return file_name

    def get_detail_by_keyword(self, keyword: str) -> str:
        """请关键词生成详细描述"""
        return self.llm.predict(f"请为以下关键词生成100字详细描述: {keyword}")

    def fallback_response(self, query: str) -> str:
        """兜底回复工具"""
        return "当前问题需要人工处理，请拨打客服热线400-xxxx或添加客服微信"

    def _init_tools(self):
        return [
            Tool(
                name="get_keywords_detail",
                func=self.get_detail_by_keyword,
                description="为关键词生成详细描述"
            ),
            Tool(
                name="GenerateImage",
                func=self.generate_image,
                description="根据提示词生成图片"
            ),
            Tool(
                name="HumanSupport",
                func=self.fallback_response,
                description="兜底回复工具"
            )
        ]

    def _create_agent(self):
        CUSTOM_PROMPT = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
            template="""你是一个智能助手，需要按照严格的顺序执行以下操作：
1. 必须先用get_keywords_detail工具生成详细描述
2. 必须用GenerateImage工具生成图片
3. 当任何工具返回包含[ERROR]的结果时，必须立即调用HumanSupport工具
4. 最终答案必须包含生成的图片路径或人工联系方式

可用工具：
{tools}

工具名称：{tool_names}

请按照以下格式输出你的思考和行动：
Thought: 思考当前需要做什么
Action: 要使用的工具名称
Action Input: 工具的输入参数
Observation: 工具返回的结果
... (这个思考-行动-观察的过程会重复)
Thought: 我已经完成了所有任务
Final Answer: 最终的输出结果

请记住：每个步骤都必须包含Thought、Action和Action Input！

用户输入: {input}

{agent_scratchpad}"""
        )
        return create_react_agent(self.llm, self.tools, prompt=CUSTOM_PROMPT)

    def _create_executor(self):
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            max_iterations=3,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )

    def run(self, input_text: str):
        return self.agent_executor.invoke({"input": input_text})

# 实例化并运行
agent = ECommerceAgent(llm)
resp = agent.run("女人")
print(resp)

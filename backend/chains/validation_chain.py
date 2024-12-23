from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough

from ..models.validation_models import ValidationResult
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE

class ValidationChain:
    """쿼리 검증을 수행하는 체인"""
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        self.validation_parser = PydanticOutputParser(pydantic_object=ValidationResult)
        
        # 검증을 위한 프롬프트
        validation_prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Analyze the following query about building data:
            Query: {query}

            Determine:
            1. If it specifically references Building 530
            2. If it relates to October 2024
            3. If it involves short cycling analysis
            4. The type of query (building/panel/breaker/date/hierarchy)

            Return a JSON with these exact fields:
            {{
                "is_building_530": boolean,
                "is_october_2024": boolean,
                "is_short_cycling": boolean,
                "query_type": "building" or "panel" or "breaker" or "date" or "hierarchy"
            }}
            """
        )
        
        self.validation_chain = (
            {"query": RunnablePassthrough()} 
            | validation_prompt 
            | self.llm 
            | StrOutputParser() 
            | self.validation_parser
        )
    
    def validate(self, query: str) -> ValidationResult:
        """쿼리 검증 수행"""
        return self.validation_chain.invoke({"query": query}) 
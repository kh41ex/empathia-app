# psychology_rag.py
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.utils.conversation_memory import conversation_memory
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

class PsychologyBookExpert:
    _instance = None  # Singleton instance
    _initialized = False  # Track initialization
    
    def __new__(cls):
        """Singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super(PsychologyBookExpert, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize only once"""
        if not self._initialized:
            # Load the pre-built vector database (ONCE)
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vector_store = Chroma(
                persist_directory="./outputs/psychology_books_db_clean",
                embedding_function=self.embeddings
            )
            self.llm = None # Will be initialized later
            self.prompt_template = None # Will be initialized later
            self.initialize_llm() # Will be initialized later
            self._initialized = True # Mark as initialized
            print("✅ Psychology expert initialized successfully!")
        # Else: Already initialized, do nothing

    def initialize_llm(self):
        """Initialize LLM components (only once)"""
        if self.llm is not None:  # Already initialized
            return  
           
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],  # Removed emotion_label
            template="""
            You are a grief counseling expert providing evidence-based guidance on pet loss. Your responses should blend psychological research with compassionate support.

            **CORE PRINCIPLES:**
            - Lead with 1 key research-backed insight from the context
            - Provide 1 practical, actionable suggestion
            - Keep responses under 75 words - extremely concise
            - Use accessible language (no academic jargon)
            - Focus on normalization and validation
            - Always cite the psychological perspective

            **RESPONSE STRUCTURE:**
            1. Normalize the emotion ("It's natural to feel...")
            2. Provide 1 evidence-based insight  
            3. Offer 1 concrete practice ("Try...")
            4. Don't use bullet points or lists
            5. End with validation ("Be patient with yourself")

            **CONTEXT INTEGRATION:**
            - Extract 1 relevant concept from the psychology context
            - Translate research into practical, everyday language
            - Focus on concepts that reduce shame and isolation

            **AVOID:**
            - ❌ Lists or multiple recommendations
            - ❌ Clinical terminology without explanation
            - ❌ Long paragraphs or complex explanations
            - ❌ Making guarantees or promises
            - ❌ Overwhelming with multiple strategies

            **EXAMPLE RESPONSES:**
            - Research shows grief often comes in waves. Allow yourself to feel each emotion without judgment. This oscillation is a natural part of healing.
            - Attachment theory explains why pet loss triggers deep grief. Honor your bond through small rituals - this helps integrate the loss gradually.
            - The dual process model shows grieving involves both loss-oriented and restoration-oriented activities. Balance remembering with engaging in new routines.

            Context: {context}

            Question: {question}

            Expert Answer::
            """
        )

        
        try:
            # ✅ Initialize the LLM with proper error handling
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0.01,  # Very low temperature for factual responses
                max_tokens=100,  # Very short responses
                request_timeout=15,  # Timeout individual requests
                max_retries=1  # Fewer retries
            )

        except Exception as e:
            print(f"❌ Failed to initialize psychology expert: {e}")
            import traceback
            traceback.print_exc()



    def get_expert_response(self, user_input, session_id="default"):
        """The main function to get an expert response."""
        if not self._initialized or self.llm is None or self.prompt_template is None:
            return "Expert system not available. Please check configuration."

        try:

            # Get conversation history for context
            history = conversation_memory.get_formatted_history(session_id)


            # Retrieve relevant context from psychology books
            # Search with both current input and recent history for better context
            search_query = f"{user_input} {history[-200:]}" if history else user_input
            relevant_docs = self.vector_store.similarity_search(search_query, k=1)

            if not relevant_docs:
                # Fallback: respond without context if search fails
                context = "Pet loss grief and coping strategies"
            else:
                context = "\n".join([doc.page_content[:200] for doc in relevant_docs])  # Very short context
        
        
            # MODERN SYNTAX: Use invoke pattern
            # 1. Create the prompt with variables
            prompt_value = self.prompt_template.invoke({
                "context": f"{context}\n\nConversation Context: {history}",
                "question": user_input
            })
        
            # 2. Send the prompt to the LLM
            result = self.llm.invoke(prompt_value.to_string())
        
            # 3. Extract the text content from the LLM response
            return result.content.strip()
        
        except Exception as e:
            return f"Error consulting psychology resources: {e}"
        

def get_psychology_expert():
    """Get the psychology expert instance (Streamlit-safe)"""
    try:
        if 'psychology_expert' not in st.session_state:
            st.session_state.psychology_expert = PsychologyBookExpert()
        return st.session_state.psychology_expert
    except (AttributeError, RuntimeError):
        # Fallback for threads: use module-level cache
        if not hasattr(get_psychology_expert, "_instance"):
            get_psychology_expert._instance = PsychologyBookExpert()
        return get_psychology_expert._instance      

# Global instance
# psychology_expert = PsychologyBookExpert()
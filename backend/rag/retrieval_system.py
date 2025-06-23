from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import JSONLoader, PyPDFLoader
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import chromadb
from typing import List, Dict, Any, Optional
import os
import json
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 persist_directory: str = "./data/chroma_db"):
        
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize vector store
        self.vectorstore = None
        self.retriever = None
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize LLM (using a lightweight model for demo)
        self.llm = None
        self.qa_chain = None
        
        # MOSDAC-specific prompt templates
        self.prompt_templates = {
            "product_information": """
            You are a MOSDAC AI assistant specializing in satellite data products. 
            Use the following context to answer questions about satellite missions, data products, and specifications.
            
            Context: {context}
            
            Question: {question}
            
            Provide a detailed, accurate answer focusing on:
            - Product specifications and characteristics
            - Data availability and coverage
            - Technical details and formats
            - Access procedures if relevant
            
            Answer:
            """,
            
            "data_download": """
            You are a MOSDAC AI assistant helping users with data download procedures.
            Use the following context to provide step-by-step guidance.
            
            Context: {context}
            
            Question: {question}
            
            Provide clear, actionable instructions including:
            - Required registration or authentication steps
            - Data search and selection procedures
            - Download methods and tools
            - File formats and processing requirements
            
            Answer:
            """,
            
            "technical_support": """
            You are a MOSDAC technical support AI assistant.
            Use the following context to help resolve technical issues.
            
            Context: {context}
            
            Question: {question}
            
            Provide helpful troubleshooting guidance including:
            - Common causes of the issue
            - Step-by-step resolution steps
            - Alternative approaches if applicable
            - When to contact human support
            
            Answer:
            """,
            
            "general": """
            You are a helpful MOSDAC AI assistant with expertise in satellite data and remote sensing.
            Use the following context to provide accurate, informative answers.
            
            Context: {context}
            
            Question: {question}
            
            Provide a comprehensive answer that is:
            - Accurate and based on the provided context
            - Clear and easy to understand
            - Relevant to MOSDAC services and satellite data
            - Helpful for the user's specific needs
            
            Answer:
            """
        }
    
    def initialize_vectorstore(self):
        """Initialize or load the vector store"""
        try:
            # Try to load existing vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Check if vector store has documents
            if self.vectorstore._collection.count() == 0:
                logger.info("Vector store is empty, will need to ingest documents")
            else:
                logger.info(f"Loaded vector store with {self.vectorstore._collection.count()} documents")
            
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            # Create new vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def ingest_documents(self, data_directory: str):
        """Ingest documents into the vector store"""
        if not self.vectorstore:
            self.initialize_vectorstore()
        
        documents = []
        
        # Process JSON files (scraped web content)
        json_files = [f for f in os.listdir(data_directory) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(data_directory, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract content based on data structure
                if isinstance(data, dict):
                    content = self.extract_content_from_json(data)
                    if content:
                        documents.extend(content)
                        
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
        
        # Process PDF files
        pdf_files = [f for f in os.listdir(data_directory) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(data_directory, pdf_file)
            try:
                loader = PyPDFLoader(file_path)
                pdf_documents = loader.load()
                documents.extend(pdf_documents)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
        
        if documents:
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vectorstore.add_documents(texts)
            self.vectorstore.persist()
            
            logger.info(f"Ingested {len(texts)} document chunks into vector store")
        else:
            logger.warning("No documents found to ingest")
    
    def extract_content_from_json(self, data: Dict[str, Any]) -> List[Any]:
        """Extract content from JSON data structure"""
        from langchain.schema import Document
        
        documents = []
        
        # Main content
        if data.get('content'):
            doc = Document(
                page_content=data['content'],
                metadata={
                    'source': data.get('url', 'unknown'),
                    'title': data.get('title', ''),
                    'type': data.get('content_type', 'webpage')
                }
            )
            documents.append(doc)
        
        # FAQ content
        if data.get('faqs'):
            for faq in data['faqs']:
                faq_content = f"Q: {faq['question']}\nA: {faq['answer']}"
                doc = Document(
                    page_content=faq_content,
                    metadata={
                        'source': data.get('url', 'unknown'),
                        'type': 'faq',
                        'question': faq['question']
                    }
                )
                documents.append(doc)
        
        # Table content
        if data.get('tables'):
            for i, table in enumerate(data['tables']):
                if table.get('headers') and table.get('rows'):
                    table_content = self.format_table_content(table)
                    doc = Document(
                        page_content=table_content,
                        metadata={
                            'source': data.get('url', 'unknown'),
                            'type': 'table',
                            'table_index': i
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    def format_table_content(self, table: Dict[str, Any]) -> str:
        """Format table data as readable text"""
        headers = table.get('headers', [])
        rows = table.get('rows', [])
        
        if not headers or not rows:
            return ""
        
        content = "Table Data:\n"
        content += " | ".join(headers) + "\n"
        content += "-" * (len(" | ".join(headers))) + "\n"
        
        for row in rows:
            if len(row) == len(headers):
                content += " | ".join(str(cell) for cell in row) + "\n"
        
        return content
    
    def generate_response(self, 
                         query: str, 
                         intent: str = "general",
                         entities: List[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using RAG approach"""
        
        if not self.vectorstore:
            self.initialize_vectorstore()
        
        if not self.retriever:
            return {
                "response": "I apologize, but the knowledge base is not available at the moment. Please try again later.",
                "sources": []
            }
        
        try:
            # Retrieve relevant documents
            relevant_docs = self.retriever.get_relevant_documents(query)
            
            if not relevant_docs:
                return {
                    "response": "I couldn't find specific information about your query in the knowledge base. Could you please rephrase your question or provide more details?",
                    "sources": []
                }
            
            # Prepare context from retrieved documents
            context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Select appropriate prompt template
            template_key = intent if intent in self.prompt_templates else "general"
            prompt_template = self.prompt_templates[template_key]
            
            # Generate response using template
            response = self.generate_template_response(
                query=query,
                context=context_text,
                template=prompt_template,
                entities=entities
            )
            
            # Extract sources
            sources = list(set([doc.metadata.get('source', 'Unknown') for doc in relevant_docs]))
            
            return {
                "response": response,
                "sources": sources,
                "retrieved_docs": len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I encountered an error while processing your query. Please try again or contact support if the issue persists.",
                "sources": []
            }
    
    def generate_template_response(self, 
                                 query: str, 
                                 context: str, 
                                 template: str,
                                 entities: List[Dict[str, Any]] = None) -> str:
        """Generate response using template (fallback without LLM)"""
        
        # For demo purposes, we'll use template-based responses
        # In production, this would use an actual LLM
        
        # Extract key information from context
        context_snippets = context.split('\n\n')[:3]  # Use first 3 most relevant snippets
        
        # Create a structured response based on intent and entities
        if entities:
            entity_names = [entity['text'] for entity in entities]
            entity_info = f"Based on your query about {', '.join(entity_names)}, "
        else:
            entity_info = "Based on the available information, "
        
        # Combine context snippets into a coherent response
        response_parts = []
        for snippet in context_snippets:
            if len(snippet.strip()) > 50:  # Only include substantial content
                response_parts.append(snippet.strip()[:500])  # Limit length
        
        if response_parts:
            main_response = entity_info + "\n\n".join(response_parts)
        else:
            main_response = "I found some relevant information, but it may not fully address your specific question. Please provide more details or try rephrasing your query."
        
        return main_response
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.vectorstore:
            self.initialize_vectorstore()
            return []
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content[:500],  # Truncate for display
                    "metadata": doc.metadata,
                    "source": doc.metadata.get('source', 'Unknown')
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

if __name__ == "__main__":
    # Initialize RAG system
    rag_system = RAGSystem()
    rag_system.initialize_vectorstore()
    
    # Ingest documents (if data directory exists)
    data_dir = "./data/scraped"
    if os.path.exists(data_dir):
        rag_system.ingest_documents(data_dir)
    
    # Test query
    test_query = "How do I download INSAT-3D data?"
    response = rag_system.generate_response(test_query, intent="data_download")
    print(f"Query: {test_query}")
    print(f"Response: {response['response']}")
    print(f"Sources: {response['sources']}")
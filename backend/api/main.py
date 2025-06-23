from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from contextlib import asynccontextmanager

from backend.ml_models.intent_classifier import IntentClassificationPipeline
from backend.ml_models.ner_model import MOSDACNERModel, EntityRelationshipExtractor
from backend.knowledge_graph.graph_builder import KnowledgeGraphBuilder, GraphQueryEngine
from backend.rag.retrieval_system import RAGSystem
from backend.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
intent_classifier = None
ner_model = None
graph_builder = None
query_engine = None
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global intent_classifier, ner_model, graph_builder, query_engine, rag_system
    
    logger.info("Loading ML models...")
    
    # Load intent classifier
    intent_classifier = IntentClassificationPipeline()
    try:
        intent_classifier.load_model(settings.INTENT_MODEL_PATH)
        logger.info("Intent classifier loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load intent classifier: {e}")
        # Train a new model if not found
        df = intent_classifier.create_training_data()
        train_dataset, val_dataset = intent_classifier.prepare_data(df)
        intent_classifier.train_model(train_dataset, val_dataset)
        logger.info("New intent classifier trained")
    
    # Load NER model
    ner_model = MOSDACNERModel()
    try:
        ner_model.load_model(settings.NER_MODEL_PATH)
        logger.info("NER model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load NER model: {e}")
        # Train a new model if not found
        training_data = ner_model.create_training_data()
        ner_model.train_model(training_data)
        logger.info("New NER model trained")
    
    # Initialize knowledge graph
    graph_builder = KnowledgeGraphBuilder(
        neo4j_uri=settings.NEO4J_URI,
        neo4j_user=settings.NEO4J_USER,
        neo4j_password=settings.NEO4J_PASSWORD
    )
    query_engine = GraphQueryEngine(graph_builder)
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    logger.info("All models loaded successfully")
    
    yield
    
    # Shutdown
    if graph_builder:
        graph_builder.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="MOSDAC AI Help Bot API",
    description="AI-powered help bot for MOSDAC portal with knowledge graph and NLP capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    include_entities: bool = True
    include_relationships: bool = True

class QueryResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    knowledge_graph_results: List[Dict[str, Any]]
    sources: List[str]

class EntityExtractionRequest(BaseModel):
    text: str

class EntityExtractionResponse(BaseModel):
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

class KnowledgeGraphQuery(BaseModel):
    entity_name: str
    max_depth: int = 2

class KnowledgeGraphResponse(BaseModel):
    entity_details: Dict[str, Any]
    related_entities: List[Dict[str, Any]]

# API endpoints
@app.get("/")
async def root():
    return {"message": "MOSDAC AI Help Bot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": {
            "intent_classifier": intent_classifier is not None,
            "ner_model": ner_model is not None,
            "knowledge_graph": graph_builder is not None,
            "rag_system": rag_system is not None
        }
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return comprehensive response"""
    try:
        query = request.query
        
        # 1. Intent classification
        intent, intent_confidence = intent_classifier.predict_intent(query)
        logger.info(f"Intent: {intent} (confidence: {intent_confidence:.2f})")
        
        # 2. Entity extraction
        entities = ner_model.extract_entities(query)
        
        # 3. Relationship extraction
        relationship_extractor = EntityRelationshipExtractor(ner_model)
        relationships = relationship_extractor.extract_relationships(query)
        
        # 4. Knowledge graph search
        kg_results = query_engine.semantic_search(query)
        
        # 5. RAG-based response generation
        rag_response = rag_system.generate_response(
            query=query,
            intent=intent,
            entities=entities,
            context=request.context
        )
        
        return QueryResponse(
            response=rag_response["response"],
            intent=intent,
            confidence=intent_confidence,
            entities=entities,
            relationships=relationships,
            knowledge_graph_results=kg_results,
            sources=rag_response.get("sources", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-entities", response_model=EntityExtractionResponse)
async def extract_entities(request: EntityExtractionRequest):
    """Extract entities and relationships from text"""
    try:
        entities = ner_model.extract_entities(request.text)
        
        relationship_extractor = EntityRelationshipExtractor(ner_model)
        relationships = relationship_extractor.extract_relationships(request.text)
        
        return EntityExtractionResponse(
            entities=entities,
            relationships=relationships
        )
        
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge-graph/query", response_model=KnowledgeGraphResponse)
async def query_knowledge_graph(request: KnowledgeGraphQuery):
    """Query the knowledge graph for entity information"""
    try:
        entity_details = graph_builder.get_entity_details(request.entity_name)
        related_entities = graph_builder.find_related_entities(
            request.entity_name, 
            request.max_depth
        )
        
        return KnowledgeGraphResponse(
            entity_details=entity_details,
            related_entities=related_entities
        )
        
    except Exception as e:
        logger.error(f"Error querying knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-graph/export")
async def export_knowledge_graph():
    """Export knowledge graph data for visualization"""
    try:
        graph_data = graph_builder.export_graph_data()
        return graph_data
        
    except Exception as e:
        logger.error(f"Error exporting knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/stats")
async def get_analytics_stats():
    """Get system analytics and statistics"""
    try:
        # This would typically come from a database
        stats = {
            "total_queries": 12847,
            "active_users": 1429,
            "knowledge_entities": 8596,
            "avg_response_time": 1.2,
            "intent_accuracy": 0.94,
            "entity_accuracy": 0.91
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/query-types")
async def get_query_type_distribution():
    """Get distribution of query types"""
    try:
        distribution = [
            {"type": "Product Information", "count": 3240, "percentage": 35},
            {"type": "Download Procedures", "count": 2187, "percentage": 24},
            {"type": "Technical Support", "count": 1854, "percentage": 20},
            {"type": "Geospatial Queries", "count": 1236, "percentage": 13},
            {"type": "Documentation", "count": 730, "percentage": 8}
        ]
        
        return distribution
        
    except Exception as e:
        logger.error(f"Error getting query distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=True
    )
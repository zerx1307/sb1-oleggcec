#!/usr/bin/env python3
"""
Complete ML pipeline runner for MOSDAC AI Help Bot
This script orchestrates the entire ML pipeline from data ingestion to model deployment
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent))

from data_ingestion.web_scraper import DataIngestionPipeline
from ml_models.intent_classifier import IntentClassificationPipeline
from ml_models.ner_model import MOSDACNERModel, EntityRelationshipExtractor
from knowledge_graph.graph_builder import KnowledgeGraphBuilder
from rag.retrieval_system import RAGSystem
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MOSDACMLPipeline:
    def __init__(self):
        self.data_pipeline = DataIngestionPipeline(settings.SCRAPED_DATA_DIR)
        self.intent_classifier = IntentClassificationPipeline()
        self.ner_model = MOSDACNERModel()
        self.graph_builder = None
        self.rag_system = RAGSystem(persist_directory=settings.CHROMA_PERSIST_DIRECTORY)
        
    def run_data_ingestion(self):
        """Step 1: Scrape and process web content"""
        logger.info("Starting data ingestion...")
        
        # Create directories
        os.makedirs(settings.SCRAPED_DATA_DIR, exist_ok=True)
        os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
        
        # Run web scraper
        logger.info("Running web scraper...")
        self.data_pipeline.run_scraper()
        
        # Process scraped data
        logger.info("Processing scraped data...")
        processed_data = self.data_pipeline.process_scraped_data()
        
        logger.info(f"Data ingestion completed. Processed {len(processed_data)} documents.")
        return processed_data
    
    def train_ml_models(self):
        """Step 2: Train ML models"""
        logger.info("Starting ML model training...")
        
        # Train intent classifier
        logger.info("Training intent classifier...")
        df = self.intent_classifier.create_training_data()
        train_dataset, val_dataset = self.intent_classifier.prepare_data(df)
        self.intent_classifier.train_model(train_dataset, val_dataset, settings.INTENT_MODEL_PATH)
        
        # Train NER model
        logger.info("Training NER model...")
        training_data = self.ner_model.create_training_data()
        self.ner_model.train_model(training_data, output_dir=settings.NER_MODEL_PATH)
        
        logger.info("ML model training completed.")
    
    def build_knowledge_graph(self, processed_data):
        """Step 3: Build knowledge graph"""
        logger.info("Building knowledge graph...")
        
        # Initialize graph builder
        self.graph_builder = KnowledgeGraphBuilder(
            neo4j_uri=settings.NEO4J_URI,
            neo4j_user=settings.NEO4J_USER,
            neo4j_password=settings.NEO4J_PASSWORD
        )
        
        # Extract entities and relationships from processed data
        all_entities = []
        all_relationships = []
        
        relationship_extractor = EntityRelationshipExtractor(self.ner_model)
        
        for doc in processed_data:
            content = doc.get('content', '')
            if content:
                # Extract entities
                entities = self.ner_model.extract_entities(content)
                all_entities.extend(entities)
                
                # Extract relationships
                relationships = relationship_extractor.extract_relationships(content)
                all_relationships.extend(relationships)
        
        # Build and save knowledge graph
        self.graph_builder.build_graph_from_entities(all_entities, all_relationships)
        self.graph_builder.save_to_neo4j()
        
        logger.info(f"Knowledge graph built with {len(all_entities)} entities and {len(all_relationships)} relationships.")
    
    def setup_rag_system(self):
        """Step 4: Setup RAG system"""
        logger.info("Setting up RAG system...")
        
        # Initialize vector store
        self.rag_system.initialize_vectorstore()
        
        # Ingest documents
        if os.path.exists(settings.SCRAPED_DATA_DIR):
            self.rag_system.ingest_documents(settings.SCRAPED_DATA_DIR)
        
        logger.info("RAG system setup completed.")
    
    def run_full_pipeline(self):
        """Run the complete ML pipeline"""
        logger.info("Starting complete MOSDAC ML pipeline...")
        
        try:
            # Step 1: Data ingestion
            processed_data = self.run_data_ingestion()
            
            # Step 2: Train ML models
            self.train_ml_models()
            
            # Step 3: Build knowledge graph
            self.build_knowledge_graph(processed_data)
            
            # Step 4: Setup RAG system
            self.setup_rag_system()
            
            logger.info("Complete ML pipeline executed successfully!")
            
            # Test the system
            self.test_system()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        
        finally:
            if self.graph_builder:
                self.graph_builder.close()
    
    def test_system(self):
        """Test the complete system"""
        logger.info("Testing the complete system...")
        
        test_queries = [
            "How do I download INSAT-3D data?",
            "What is the resolution of Oceansat-2 OCM?",
            "Tell me about SCATSAT-1 mission",
            "Data available for Indian Ocean region",
            "API documentation for bulk access"
        ]
        
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            
            # Test intent classification
            intent, confidence = self.intent_classifier.predict_intent(query)
            logger.info(f"  Intent: {intent} (confidence: {confidence:.2f})")
            
            # Test entity extraction
            entities = self.ner_model.extract_entities(query)
            logger.info(f"  Entities: {[e['text'] for e in entities]}")
            
            # Test RAG response
            response = self.rag_system.generate_response(query, intent, entities)
            logger.info(f"  Response length: {len(response['response'])} characters")
            
            print(f"\nQuery: {query}")
            print(f"Intent: {intent} ({confidence:.2f})")
            print(f"Entities: {[e['text'] for e in entities]}")
            print(f"Response: {response['response'][:200]}...")
            print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="MOSDAC ML Pipeline Runner")
    parser.add_argument("--step", choices=["data", "models", "graph", "rag", "full", "test"], 
                       default="full", help="Pipeline step to run")
    parser.add_argument("--skip-scraping", action="store_true", 
                       help="Skip web scraping (use existing data)")
    
    args = parser.parse_args()
    
    pipeline = MOSDACMLPipeline()
    
    try:
        if args.step == "data":
            pipeline.run_data_ingestion()
        elif args.step == "models":
            pipeline.train_ml_models()
        elif args.step == "graph":
            # Load existing data for graph building
            processed_data = pipeline.data_pipeline.process_scraped_data()
            pipeline.build_knowledge_graph(processed_data)
        elif args.step == "rag":
            pipeline.setup_rag_system()
        elif args.step == "test":
            pipeline.test_system()
        elif args.step == "full":
            if args.skip_scraping:
                # Skip scraping, use existing data
                processed_data = pipeline.data_pipeline.process_scraped_data()
                pipeline.train_ml_models()
                pipeline.build_knowledge_graph(processed_data)
                pipeline.setup_rag_system()
                pipeline.test_system()
            else:
                pipeline.run_full_pipeline()
        
        logger.info("Pipeline execution completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
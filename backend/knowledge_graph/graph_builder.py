import networkx as nx
from neo4j import GraphDatabase
import json
from typing import Dict, List, Any, Tuple
import logging
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    id: str
    label: str
    type: str
    properties: Dict[str, Any]
    
@dataclass 
class Relationship:
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]

class KnowledgeGraphBuilder:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.graph = nx.MultiDiGraph()
        
        # Entity type mappings
        self.entity_types = {
            "SATELLITE": "Mission",
            "SENSOR": "Instrument", 
            "DATA_PRODUCT": "Product",
            "LOCATION": "GeographicArea",
            "PARAMETER": "MeasurementType",
            "ORGANIZATION": "Organization",
            "MISSION": "Mission",
            "FORMAT": "DataFormat",
            "RESOLUTION": "Specification"
        }
    
    def create_entity(self, text: str, entity_type: str, properties: Dict[str, Any] = None) -> Entity:
        """Create an entity node"""
        entity_id = str(uuid.uuid4())
        
        if properties is None:
            properties = {}
        
        # Add default properties
        properties.update({
            "name": text,
            "type": self.entity_types.get(entity_type, entity_type),
            "created_from": "ner_extraction"
        })
        
        entity = Entity(
            id=entity_id,
            label=text,
            type=entity_type,
            properties=properties
        )
        
        return entity
    
    def create_relationship(self, source_entity: Entity, target_entity: Entity, 
                          relation_type: str, properties: Dict[str, Any] = None) -> Relationship:
        """Create a relationship between entities"""
        rel_id = str(uuid.uuid4())
        
        if properties is None:
            properties = {}
        
        relationship = Relationship(
            id=rel_id,
            source_id=source_entity.id,
            target_id=target_entity.id,
            type=relation_type,
            properties=properties
        )
        
        return relationship
    
    def add_entity_to_graph(self, entity: Entity):
        """Add entity to NetworkX graph"""
        self.graph.add_node(
            entity.id,
            label=entity.label,
            type=entity.type,
            **entity.properties
        )
    
    def add_relationship_to_graph(self, relationship: Relationship):
        """Add relationship to NetworkX graph"""
        self.graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            id=relationship.id,
            type=relationship.type,
            **relationship.properties
        )
    
    def build_graph_from_entities(self, entities_data: List[Dict[str, Any]], 
                                 relationships_data: List[Dict[str, Any]]):
        """Build knowledge graph from extracted entities and relationships"""
        
        # Create entities
        entity_map = {}
        for entity_data in entities_data:
            entity = self.create_entity(
                text=entity_data["text"],
                entity_type=entity_data["label"],
                properties=entity_data.get("properties", {})
            )
            
            self.add_entity_to_graph(entity)
            entity_map[entity_data["text"].lower()] = entity
        
        # Create relationships
        for rel_data in relationships_data:
            subject_text = rel_data["subject"].lower()
            object_text = rel_data["object"].lower()
            
            if subject_text in entity_map and object_text in entity_map:
                source_entity = entity_map[subject_text]
                target_entity = entity_map[object_text]
                
                relationship = self.create_relationship(
                    source_entity=source_entity,
                    target_entity=target_entity,
                    relation_type=rel_data["predicate"],
                    properties={
                        "confidence": rel_data.get("confidence", 1.0),
                        "source_text": rel_data.get("source_text", "")
                    }
                )
                
                self.add_relationship_to_graph(relationship)
    
    def save_to_neo4j(self):
        """Save the knowledge graph to Neo4j database"""
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create entities
            for node_id, node_data in self.graph.nodes(data=True):
                query = """
                CREATE (n:Entity {
                    id: $id,
                    label: $label,
                    type: $type,
                    name: $name
                })
                SET n += $properties
                """
                
                properties = {k: v for k, v in node_data.items() 
                            if k not in ['label', 'type']}
                
                session.run(query, {
                    "id": node_id,
                    "label": node_data.get("label", ""),
                    "type": node_data.get("type", ""),
                    "name": node_data.get("name", node_data.get("label", "")),
                    "properties": properties
                })
            
            # Create relationships
            for source, target, edge_data in self.graph.edges(data=True):
                query = f"""
                MATCH (a:Entity {{id: $source_id}})
                MATCH (b:Entity {{id: $target_id}})
                CREATE (a)-[r:{edge_data.get('type', 'RELATED')} {{
                    id: $rel_id,
                    confidence: $confidence
                }}]->(b)
                SET r += $properties
                """
                
                properties = {k: v for k, v in edge_data.items() 
                            if k not in ['type', 'id']}
                
                session.run(query, {
                    "source_id": source,
                    "target_id": target,
                    "rel_id": edge_data.get("id", str(uuid.uuid4())),
                    "confidence": edge_data.get("confidence", 1.0),
                    "properties": properties
                })
    
    def query_graph(self, query: str) -> List[Dict[str, Any]]:
        """Query the knowledge graph"""
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    
    def find_related_entities(self, entity_name: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Find entities related to a given entity"""
        query = """
        MATCH (start:Entity)
        WHERE toLower(start.name) CONTAINS toLower($entity_name)
        MATCH path = (start)-[*1..$max_depth]-(related:Entity)
        RETURN DISTINCT related.name as name, 
               related.type as type,
               length(path) as distance,
               [r in relationships(path) | type(r)] as relationship_path
        ORDER BY distance, related.name
        LIMIT 20
        """
        
        with self.driver.session() as session:
            result = session.run(query, {
                "entity_name": entity_name,
                "max_depth": max_depth
            })
            return [record.data() for record in result]
    
    def get_entity_details(self, entity_name: str) -> Dict[str, Any]:
        """Get detailed information about an entity"""
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($entity_name)
        OPTIONAL MATCH (e)-[r]-(related:Entity)
        RETURN e.name as name,
               e.type as type,
               properties(e) as properties,
               collect(DISTINCT {
                   related_entity: related.name,
                   relationship: type(r),
                   direction: CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END
               }) as relationships
        LIMIT 1
        """
        
        with self.driver.session() as session:
            result = session.run(query, {"entity_name": entity_name})
            record = result.single()
            return record.data() if record else {}
    
    def export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        # Export nodes
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": node_data.get("label", ""),
                "type": node_data.get("type", ""),
                "properties": {k: v for k, v in node_data.items() 
                             if k not in ['label', 'type']}
            })
        
        # Export edges
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": edge_data.get("type", "RELATED"),
                "properties": {k: v for k, v in edge_data.items() 
                             if k not in ['type']}
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "node_types": list(set(node["type"] for node in nodes)),
                "relationship_types": list(set(edge["type"] for edge in edges))
            }
        }
    
    def close(self):
        """Close database connection"""
        self.driver.close()

class GraphQueryEngine:
    def __init__(self, graph_builder: KnowledgeGraphBuilder):
        self.graph_builder = graph_builder
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search on the knowledge graph"""
        # Extract key terms from query
        key_terms = self.extract_key_terms(query)
        
        results = []
        for term in key_terms:
            related_entities = self.graph_builder.find_related_entities(term)
            results.extend(related_entities)
        
        # Remove duplicates and rank by relevance
        unique_results = {}
        for result in results:
            key = result["name"]
            if key not in unique_results:
                unique_results[key] = result
            else:
                # Merge results, keeping the one with shorter distance
                if result["distance"] < unique_results[key]["distance"]:
                    unique_results[key] = result
        
        return list(unique_results.values())[:limit]
    
    def extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for graph search"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        import re
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "what", "how", "where", "when", "why"}
        
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms

if __name__ == "__main__":
    # Example usage
    from backend.config import settings
    
    # Initialize graph builder
    graph_builder = KnowledgeGraphBuilder(
        neo4j_uri=settings.NEO4J_URI,
        neo4j_user=settings.NEO4J_USER,
        neo4j_password=settings.NEO4J_PASSWORD
    )
    
    # Example entities and relationships
    entities = [
        {"text": "INSAT-3D", "label": "SATELLITE"},
        {"text": "Imager", "label": "SENSOR"},
        {"text": "Meteorological data", "label": "DATA_PRODUCT"}
    ]
    
    relationships = [
        {"subject": "INSAT-3D", "predicate": "PROVIDES", "object": "Meteorological data"},
        {"subject": "Imager", "predicate": "GENERATES", "object": "Meteorological data"}
    ]
    
    # Build graph
    graph_builder.build_graph_from_entities(entities, relationships)
    graph_builder.save_to_neo4j()
    
    print("Knowledge graph created successfully!")
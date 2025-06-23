import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
from typing import List, Dict, Tuple, Any
import json
import os

class MOSDACNERModel:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)
        
        # Add custom entity labels for MOSDAC domain
        self.entity_labels = [
            "SATELLITE",      # Satellite names (INSAT-3D, Oceansat-2, etc.)
            "SENSOR",         # Sensor types (Imager, Scatterometer, OCM)
            "DATA_PRODUCT",   # Data product types
            "MISSION",        # Mission names
            "LOCATION",       # Geographic locations
            "PARAMETER",      # Scientific parameters (wind speed, temperature)
            "RESOLUTION",     # Spatial/temporal resolution
            "FORMAT",         # Data formats (HDF5, NetCDF)
            "ORGANIZATION",   # Organizations (ISRO, MOSDAC)
            "DATE_RANGE"      # Time periods
        ]
        
        # Add labels to NER component
        ner = self.nlp.get_pipe("ner")
        for label in self.entity_labels:
            ner.add_label(label)
    
    def create_training_data(self) -> List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]]:
        """Create training data for MOSDAC-specific entities"""
        training_data = [
            # Satellite entities
            ("INSAT-3D provides meteorological data", {
                "entities": [(0, 8, "SATELLITE")]
            }),
            ("Oceansat-2 OCM sensor captures ocean color data", {
                "entities": [(0, 10, "SATELLITE"), (11, 14, "SENSOR")]
            }),
            ("SCATSAT-1 scatterometer measures wind speed", {
                "entities": [(0, 10, "SATELLITE"), (11, 24, "SENSOR"), (34, 44, "PARAMETER")]
            }),
            
            # Data products and formats
            ("Download INSAT-3D imager data in HDF5 format", {
                "entities": [(9, 17, "SATELLITE"), (18, 24, "SENSOR"), (33, 37, "FORMAT")]
            }),
            ("Ocean color data available in NetCDF format", {
                "entities": [(0, 16, "DATA_PRODUCT"), (30, 36, "FORMAT")]
            }),
            
            # Locations and coverage
            ("Satellite data coverage for Indian Ocean region", {
                "entities": [(29, 47, "LOCATION")]
            }),
            ("Data available for Mumbai and surrounding areas", {
                "entities": [(19, 25, "LOCATION")]
            }),
            
            # Resolutions and parameters
            ("1km spatial resolution imager data", {
                "entities": [(0, 22, "RESOLUTION")]
            }),
            ("Sea surface temperature measurements", {
                "entities": [(0, 23, "PARAMETER")]
            }),
            ("Wind vector data with 25km resolution", {
                "entities": [(0, 16, "DATA_PRODUCT"), (22, 37, "RESOLUTION")]
            }),
            
            # Organizations and missions
            ("ISRO's MOSDAC portal provides satellite data", {
                "entities": [(0, 4, "ORGANIZATION"), (7, 13, "ORGANIZATION")]
            }),
            ("Indian National Satellite System mission", {
                "entities": [(0, 40, "MISSION")]
            }),
            
            # Date ranges
            ("Data from 2020 to 2024 available", {
                "entities": [(10, 23, "DATE_RANGE")]
            }),
            ("Daily data products since launch", {
                "entities": [(0, 5, "DATE_RANGE")]
            }),
            
            # Complex examples
            ("INSAT-3D imager provides 1km resolution data over Indian subcontinent in HDF5 format", {
                "entities": [
                    (0, 8, "SATELLITE"),
                    (9, 15, "SENSOR"), 
                    (25, 40, "RESOLUTION"),
                    (51, 69, "LOCATION"),
                    (73, 77, "FORMAT")
                ]
            }),
            ("Oceansat-2 OCM captures ocean color data at 360m resolution for coastal monitoring", {
                "entities": [
                    (0, 10, "SATELLITE"),
                    (11, 14, "SENSOR"),
                    (24, 40, "DATA_PRODUCT"),
                    (44, 59, "RESOLUTION")
                ]
            }),
            ("SCATSAT-1 scatterometer wind vector data covers global oceans with 25km spatial resolution", {
                "entities": [
                    (0, 10, "SATELLITE"),
                    (11, 24, "SENSOR"),
                    (25, 41, "DATA_PRODUCT"),
                    (49, 62, "LOCATION"),
                    (68, 90, "RESOLUTION")
                ]
            })
        ]
        
        # Add more variations
        extended_data = []
        for text, annotations in training_data:
            extended_data.append((text, annotations))
            # Add lowercase version
            extended_data.append((text.lower(), annotations))
            # Add question format
            extended_data.append((f"What about {text.lower()}?", annotations))
        
        return extended_data
    
    def train_model(self, training_data: List[Tuple[str, Dict]], n_iter: int = 30, output_dir: str = "./models/ner_model"):
        """Train the NER model"""
        # Disable other pipes during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        with self.nlp.disable_pipes(*other_pipes):
            
            # Create training examples
            examples = []
            for text, annotations in training_data:
                doc = self.nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)
            
            # Training loop
            optimizer = self.nlp.resume_training()
            for i in range(n_iter):
                random.shuffle(examples)
                losses = {}
                
                # Batch training
                batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    self.nlp.update(batch, sgd=optimizer, losses=losses)
                
                if i % 10 == 0:
                    print(f"Iteration {i}, Losses: {losses}")
        
        # Save model
        os.makedirs(output_dir, exist_ok=True)
        self.nlp.to_disk(output_dir)
        print(f"Model saved to {output_dir}")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": getattr(ent, 'confidence', 1.0)
            })
        
        return entities
    
    def load_model(self, model_path: str):
        """Load trained model"""
        self.nlp = spacy.load(model_path)
    
    def evaluate_model(self, test_data: List[Tuple[str, Dict]]) -> Dict[str, float]:
        """Evaluate model performance"""
        examples = []
        for text, annotations in test_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        scores = self.nlp.evaluate(examples)
        return {
            "precision": scores["ents_p"],
            "recall": scores["ents_r"], 
            "f1": scores["ents_f"]
        }

class EntityRelationshipExtractor:
    def __init__(self, ner_model: MOSDACNERModel):
        self.ner_model = ner_model
        
        # Define relationship patterns
        self.relationship_patterns = [
            # Satellite -> provides -> Data Product
            {"pattern": r"(\w+)\s+(provides|generates|produces)\s+(.+)", 
             "relation": "PROVIDES"},
            
            # Sensor -> measures -> Parameter
            {"pattern": r"(\w+)\s+(measures|captures|monitors)\s+(.+)",
             "relation": "MEASURES"},
             
            # Data -> covers -> Location
            {"pattern": r"(.+)\s+(covers|over|for)\s+(.+)",
             "relation": "COVERS"},
             
            # Data -> available in -> Format
            {"pattern": r"(.+)\s+(in|format)\s+(\w+)\s+format",
             "relation": "FORMAT"},
        ]
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract entity relationships from text"""
        entities = self.ner_model.extract_entities(text)
        relationships = []
        
        import re
        for pattern_info in self.relationship_patterns:
            pattern = pattern_info["pattern"]
            relation_type = pattern_info["relation"]
            
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                object_text = match.group(3).strip()
                
                relationships.append({
                    "subject": subject,
                    "predicate": relation_type,
                    "object": object_text,
                    "confidence": 0.8,
                    "source_text": match.group(0)
                })
        
        return relationships

if __name__ == "__main__":
    # Train the NER model
    ner_model = MOSDACNERModel()
    
    # Create training data
    training_data = ner_model.create_training_data()
    print(f"Created {len(training_data)} training examples")
    
    # Train model
    ner_model.train_model(training_data)
    print("NER model training completed!")
    
    # Test the model
    test_text = "INSAT-3D imager provides 1km resolution meteorological data over India"
    entities = ner_model.extract_entities(test_text)
    print(f"Extracted entities: {entities}")
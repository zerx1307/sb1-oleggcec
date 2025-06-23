import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import json
import os

class IntentClassifier(nn.Module):
    def __init__(self, model_name: str, num_classes: int, dropout_rate: float = 0.3):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)

class IntentClassificationPipeline:
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.label_encoder = LabelEncoder()
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # MOSDAC-specific intent categories
        self.intent_categories = [
            "product_information",
            "data_download",
            "technical_support", 
            "mission_details",
            "geospatial_query",
            "documentation_request",
            "api_usage",
            "account_management",
            "data_processing",
            "general_inquiry"
        ]
    
    def create_training_data(self) -> pd.DataFrame:
        """Create synthetic training data for MOSDAC intents"""
        training_examples = [
            # Product Information
            ("What satellite data products are available?", "product_information"),
            ("Tell me about INSAT-3D imager data", "product_information"),
            ("What is the resolution of Oceansat-2 data?", "product_information"),
            ("List all available satellite missions", "product_information"),
            ("What sensors are available on SCATSAT-1?", "product_information"),
            
            # Data Download
            ("How do I download satellite data?", "data_download"),
            ("What is the procedure for data access?", "data_download"),
            ("I need to download INSAT-3D data for my research", "data_download"),
            ("Can you help me access ocean color data?", "data_download"),
            ("Where can I find the download links?", "data_download"),
            
            # Technical Support
            ("I'm having trouble accessing my account", "technical_support"),
            ("The download is not working", "technical_support"),
            ("Error in data processing", "technical_support"),
            ("Website is not loading properly", "technical_support"),
            ("I need help with data format conversion", "technical_support"),
            
            # Mission Details
            ("Tell me about INSAT-3D mission", "mission_details"),
            ("What is the orbit of Oceansat-2?", "mission_details"),
            ("When was SCATSAT-1 launched?", "mission_details"),
            ("Mission objectives of Indian satellites", "mission_details"),
            ("Satellite constellation information", "mission_details"),
            
            # Geospatial Query
            ("Data available for Indian Ocean region", "geospatial_query"),
            ("Satellite coverage for Mumbai area", "geospatial_query"),
            ("What data covers latitude 20N longitude 75E?", "geospatial_query"),
            ("Regional data availability", "geospatial_query"),
            ("Spatial resolution for my area of interest", "geospatial_query"),
            
            # Documentation
            ("Where is the user manual?", "documentation_request"),
            ("I need technical documentation", "documentation_request"),
            ("API documentation link", "documentation_request"),
            ("Product specification sheets", "documentation_request"),
            ("Training materials for beginners", "documentation_request"),
            
            # API Usage
            ("How to use the API?", "api_usage"),
            ("API key generation", "api_usage"),
            ("Bulk data access through API", "api_usage"),
            ("API rate limits", "api_usage"),
            ("Authentication for API calls", "api_usage"),
            
            # Account Management
            ("How to create an account?", "account_management"),
            ("Forgot my password", "account_management"),
            ("Update my profile information", "account_management"),
            ("Account verification process", "account_management"),
            ("Delete my account", "account_management"),
            
            # Data Processing
            ("How to process satellite data?", "data_processing"),
            ("Data calibration procedures", "data_processing"),
            ("Atmospheric correction methods", "data_processing"),
            ("Image enhancement techniques", "data_processing"),
            ("Quality assessment of data", "data_processing"),
            
            # General Inquiry
            ("What is MOSDAC?", "general_inquiry"),
            ("About Indian Space Research Organisation", "general_inquiry"),
            ("Contact information", "general_inquiry"),
            ("Latest news and updates", "general_inquiry"),
            ("How can I contribute?", "general_inquiry")
        ]
        
        # Expand with variations
        expanded_examples = []
        for text, intent in training_examples:
            expanded_examples.append((text, intent))
            # Add variations
            expanded_examples.append((text.lower(), intent))
            expanded_examples.append((text + "?", intent))
            expanded_examples.append(f"Can you help me with {text.lower()}", intent)
        
        return pd.DataFrame(expanded_examples, columns=['text', 'intent'])
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[torch.utils.data.Dataset, torch.utils.data.Dataset]:
        """Prepare data for training"""
        # Encode labels
        df['label'] = self.label_encoder.fit_transform(df['intent'])
        
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            df['text'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42
        )
        
        # Tokenize
        train_encodings = self.tokenizer(train_texts, truncation=True, padding=True, max_length=128)
        val_encodings = self.tokenizer(val_texts, truncation=True, padding=True, max_length=128)
        
        # Create datasets
        train_dataset = IntentDataset(train_encodings, train_labels)
        val_dataset = IntentDataset(val_encodings, val_labels)
        
        return train_dataset, val_dataset
    
    def train_model(self, train_dataset, val_dataset, output_dir: str = "./models/intent_classifier"):
        """Train the intent classification model"""
        num_classes = len(self.label_encoder.classes_)
        self.model = IntentClassifier(self.model_name, num_classes)
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        trainer.train()
        trainer.save_model()
        
        # Save label encoder
        import joblib
        joblib.dump(self.label_encoder, f"{output_dir}/label_encoder.pkl")
        
        # Save tokenizer
        self.tokenizer.save_pretrained(output_dir)
    
    def predict_intent(self, text: str) -> Tuple[str, float]:
        """Predict intent for a given text"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        self.model.eval()
        encoding = self.tokenizer(text, truncation=True, padding=True, max_length=128, return_tensors='pt')
        
        with torch.no_grad():
            outputs = self.model(**encoding)
            predictions = torch.nn.functional.softmax(outputs, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = predictions[0][predicted_class].item()
        
        intent = self.label_encoder.inverse_transform([predicted_class])[0]
        return intent, confidence
    
    def load_model(self, model_path: str):
        """Load trained model"""
        import joblib
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.label_encoder = joblib.load(f"{model_path}/label_encoder.pkl")
        
        num_classes = len(self.label_encoder.classes_)
        self.model = IntentClassifier(self.model_name, num_classes)
        self.model.load_state_dict(torch.load(f"{model_path}/pytorch_model.bin", map_location=self.device))
        self.model.to(self.device)

class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    
    def __len__(self):
        return len(self.labels)

if __name__ == "__main__":
    # Train the intent classifier
    pipeline = IntentClassificationPipeline()
    
    # Create training data
    df = pipeline.create_training_data()
    print(f"Created {len(df)} training examples")
    
    # Prepare data
    train_dataset, val_dataset = pipeline.prepare_data(df)
    
    # Train model
    pipeline.train_model(train_dataset, val_dataset)
    print("Intent classifier training completed!")
"""
Cloudflare Trace ETL Connector
Author: Pawan Kumar Ramnani    
Roll Number: 3122225001091

This ETL pipeline extracts data from Cloudflare's trace endpoint,
transforms it into a structured format, and loads it into MongoDB.
"""

import os
import requests
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env file
load_dotenv()

class CloudflareTraceETL:
    """ETL Pipeline for Cloudflare Trace API"""
    
    def __init__(self):
        """Initialize the ETL connector with configuration"""
        # API Configuration
        self.api_url = "https://www.cloudflare.com/cdn-cgi/trace"
        
        # MongoDB Configuration
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("DB_NAME", "etl_database")
        self.collection_name = os.getenv("COLLECTION_NAME", "cloudflare_trace_raw")
        
        # Connect to MongoDB
        self.client = None
        self.db = None
        self.collection = None
        self._connect_to_mongodb()
        
    def _connect_to_mongodb(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            # Test connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    def extract(self):
        """
        Extract data from Cloudflare Trace API
        Returns: Raw text response from the API
        """
        try:
            print("🔄 Extracting data from Cloudflare Trace API...")
            
            # Make GET request to the API
            response = requests.get(self.api_url, timeout=10)
            
            # Check if request was successful
            if response.status_code == 200:
                print(f"✅ Successfully extracted data (Status: {response.status_code})")
                return response.text
            else:
                print(f"⚠️ API returned status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - API took too long to respond")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - Unable to reach API")
            return None
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            return None
    
    def transform(self, raw_data):
        """
        Transform raw trace data into structured JSON format
        Args: raw_data (str) - Raw text response from API
        Returns: Dictionary with structured data
        """
        if not raw_data:
            print("⚠️ No data to transform")
            return None
        
        try:
            print("🔄 Transforming data...")
            
            # Parse the key=value format into a dictionary
            data_dict = {}
            for line in raw_data.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    data_dict[key.strip()] = value.strip()
            
            # Create transformed document
            transformed_data = {
                "ip_address": data_dict.get("ip", "N/A"),
                "timestamp": data_dict.get("ts", "N/A"),
                "visit_scheme": data_dict.get("visit_scheme", "N/A"),
                "uag": data_dict.get("uag", "N/A"),  # User Agent
                "colo": data_dict.get("colo", "N/A"),  # Cloudflare data center
                "sliver": data_dict.get("sliver", "N/A"),
                "http_version": data_dict.get("http", "N/A"),
                "location": data_dict.get("loc", "N/A"),  # Country code
                "tls_version": data_dict.get("tls", "N/A"),
                "sni": data_dict.get("sni", "N/A"),
                "warp": data_dict.get("warp", "N/A"),
                "gateway": data_dict.get("gateway", "N/A"),
                "rbi": data_dict.get("rbi", "N/A"),
                "kex": data_dict.get("kex", "N/A"),
                # Metadata
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "raw_data": data_dict,  # Store original parsed data
                "data_source": "Cloudflare Trace API"
            }
            
            print("✅ Data transformation completed")
            return transformed_data
            
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return None
    
    def load(self, transformed_data):
        """
        Load transformed data into MongoDB
        Args: transformed_data (dict) - Structured data to insert
        Returns: Inserted document ID or None
        """
        if not transformed_data:
            print("⚠️ No data to load")
            return None
        
        try:
            print("🔄 Loading data into MongoDB...")
            
            # Insert document into MongoDB
            result = self.collection.insert_one(transformed_data)
            
            print(f"✅ Successfully loaded data into MongoDB")
            print(f"   Collection: {self.collection_name}")
            print(f"   Document ID: {result.inserted_id}")
            
            return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error during loading: {e}")
            return None
    
    def run_pipeline(self):
        """Execute the complete ETL pipeline"""
        print("\n" + "="*60)
        print("🚀 Starting Cloudflare Trace ETL Pipeline")
        print("="*60 + "\n")
        
        start_time = time.time()
        
        # Step 1: Extract
        raw_data = self.extract()
        if not raw_data:
            print("\n❌ Pipeline failed at extraction stage")
            return False
        
        print()
        
        # Step 2: Transform
        transformed_data = self.transform(raw_data)
        if not transformed_data:
            print("\n❌ Pipeline failed at transformation stage")
            return False
        
        print()
        
        # Step 3: Load
        doc_id = self.load(transformed_data)
        if not doc_id:
            print("\n❌ Pipeline failed at loading stage")
            return False
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        print("\n" + "="*60)
        print(f"✅ ETL Pipeline completed successfully!")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print("="*60 + "\n")
        
        return True
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")


def main():
    """Main execution function"""
    etl = None
    try:
        # Initialize and run ETL pipeline
        etl = CloudflareTraceETL()
        etl.run_pipeline()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Clean up
        if etl:
            etl.close_connection()


if __name__ == "__main__":
    main()
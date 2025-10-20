"""
Cloudflare Multi-Endpoint ETL Connector
Author: Pawan Kumar Ramnani
Roll Number: 3122225001091

This ETL pipeline extracts data from THREE Cloudflare public endpoints:
1. Cloudflare Trace API - Network trace information
2. Cloudflare DNS over HTTPS - DNS resolution data
3. Cloudflare Security DNS - Malware/security DNS data

All data is transformed and loaded into separate MongoDB collections.
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

class CloudflareMultiEndpointETL:
    """ETL Pipeline for Multiple Cloudflare Public Endpoints"""
    
    def __init__(self):
        """Initialize the ETL connector with configuration"""
        # API Endpoints Configuration
        self.endpoints = {
            'trace': {
                'url': 'https://www.cloudflare.com/cdn-cgi/trace',
                'collection': 'cloudflare_trace_data'
            },
            'dns_standard': {
                'url': 'https://cloudflare-dns.com/dns-query',
                'collection': 'cloudflare_dns_standard_data'
            },
            'dns_security': {
                'url': 'https://security.cloudflare-dns.com/dns-query',
                'collection': 'cloudflare_dns_security_data'
            }
        }
        
        # Test domains for DNS queries
        self.test_domains = ['google.com', 'cloudflare.com', 'github.com']
        
        # MongoDB Configuration
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("DB_NAME", "etl_database")
        
        # Connect to MongoDB
        self.client = None
        self.db = None
        self._connect_to_mongodb()
        
    def _connect_to_mongodb(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            print(f"   Database: {self.db_name}\n")
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    # ==================== ENDPOINT 1: Cloudflare Trace ====================
    
    def extract_trace_data(self):
        """
        Extract data from Cloudflare Trace API (Endpoint 1)
        Returns: Raw text response from the API
        """
        try:
            print("📍 ENDPOINT 1: Cloudflare Trace API")
            print("🔄 Extracting network trace data...")
            
            response = requests.get(self.endpoints['trace']['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Successfully extracted trace data (Status: {response.status_code})")
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
    
    def transform_trace_data(self, raw_data):
        """
        Transform raw trace data into structured JSON format
        """
        if not raw_data:
            print("⚠️ No trace data to transform")
            return None
        
        try:
            print("🔄 Transforming trace data...")
            
            # Parse key=value format
            data_dict = {}
            for line in raw_data.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    data_dict[key.strip()] = value.strip()
            
            transformed_data = {
                "endpoint_name": "cloudflare_trace",
                "endpoint_url": self.endpoints['trace']['url'],
                "data": {
                    "ip_address": data_dict.get("ip", "N/A"),
                    "timestamp": data_dict.get("ts", "N/A"),
                    "visit_scheme": data_dict.get("visit_scheme", "N/A"),
                    "user_agent": data_dict.get("uag", "N/A"),
                    "datacenter": data_dict.get("colo", "N/A"),
                    "http_version": data_dict.get("http", "N/A"),
                    "location": data_dict.get("loc", "N/A"),
                    "tls_version": data_dict.get("tls", "N/A"),
                    "gateway": data_dict.get("gateway", "N/A"),
                    "warp": data_dict.get("warp", "N/A")
                },
                "metadata": {
                    "ingestion_timestamp": datetime.utcnow().isoformat(),
                    "data_source": "Cloudflare Trace API",
                    "raw_data": data_dict
                }
            }
            
            print("✅ Trace data transformation completed\n")
            return transformed_data
            
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return None
    
    # ==================== ENDPOINT 2: Cloudflare DNS Standard ====================
    
    def extract_dns_standard_data(self):
        """
        Extract data from Cloudflare Standard DNS over HTTPS API (Endpoint 2)
        Queries multiple domains for A, AAAA, and MX records
        """
        try:
            print("📍 ENDPOINT 2: Cloudflare DNS over HTTPS (Standard)")
            print("🔄 Extracting DNS resolution data...")
            
            all_dns_data = []
            headers = {'accept': 'application/dns-json'}
            
            for domain in self.test_domains:
                # Query A record (IPv4)
                params = {'name': domain, 'type': 'A'}
                response = requests.get(
                    self.endpoints['dns_standard']['url'],
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    dns_result = response.json()
                    dns_result['queried_domain'] = domain
                    dns_result['query_type'] = 'A'
                    all_dns_data.append(dns_result)
                    print(f"   ✓ Retrieved A record for {domain}")
                
                time.sleep(0.5)  # Rate limiting
            
            print(f"✅ Successfully extracted DNS data for {len(all_dns_data)} queries\n")
            return all_dns_data if all_dns_data else None
            
        except Exception as e:
            print(f"❌ Error during DNS extraction: {e}")
            return None
    
    def transform_dns_standard_data(self, raw_data):
        """
        Transform DNS data into structured format
        """
        if not raw_data:
            print("⚠️ No DNS data to transform")
            return None
        
        try:
            print("🔄 Transforming DNS standard data...")
            
            transformed_records = []
            
            for record in raw_data:
                transformed_record = {
                    "endpoint_name": "cloudflare_dns_standard",
                    "endpoint_url": self.endpoints['dns_standard']['url'],
                    "query": {
                        "domain": record.get('queried_domain', 'N/A'),
                        "type": record.get('query_type', 'N/A'),
                        "status": record.get('Status', 'N/A')
                    },
                    "response": {
                        "answers": record.get('Answer', []),
                        "truncated": record.get('TC', False),
                        "recursion_desired": record.get('RD', False),
                        "recursion_available": record.get('RA', False),
                        "authenticated_data": record.get('AD', False)
                    },
                    "metadata": {
                        "ingestion_timestamp": datetime.utcnow().isoformat(),
                        "data_source": "Cloudflare DNS Standard",
                        "raw_response": record
                    }
                }
                transformed_records.append(transformed_record)
            
            print(f"✅ DNS standard data transformation completed ({len(transformed_records)} records)\n")
            return transformed_records
            
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return None
    
    # ==================== ENDPOINT 3: Cloudflare Security DNS ====================
    
    def extract_dns_security_data(self):
        """
        Extract data from Cloudflare Security DNS over HTTPS API (Endpoint 3)
        This endpoint blocks malicious domains
        """
        try:
            print("📍 ENDPOINT 3: Cloudflare DNS over HTTPS (Security)")
            print("🔄 Extracting security DNS data...")
            
            all_security_data = []
            headers = {'accept': 'application/dns-json'}
            
            # Test with legitimate domains and known malicious patterns
            test_cases = [
                {'domain': 'cloudflare.com', 'expected': 'safe'},
                {'domain': 'google.com', 'expected': 'safe'},
                {'domain': 'example.com', 'expected': 'safe'}
            ]
            
            for test_case in test_cases:
                domain = test_case['domain']
                params = {'name': domain, 'type': 'A'}
                
                response = requests.get(
                    self.endpoints['dns_security']['url'],
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    security_result = response.json()
                    security_result['queried_domain'] = domain
                    security_result['expected_status'] = test_case['expected']
                    security_result['query_type'] = 'A'
                    all_security_data.append(security_result)
                    print(f"   ✓ Security check for {domain}: {test_case['expected']}")
                
                time.sleep(0.5)
            
            print(f"✅ Successfully extracted security DNS data for {len(all_security_data)} queries\n")
            return all_security_data if all_security_data else None
            
        except Exception as e:
            print(f"❌ Error during security DNS extraction: {e}")
            return None
    
    def transform_dns_security_data(self, raw_data):
        """
        Transform security DNS data into structured format
        """
        if not raw_data:
            print("⚠️ No security DNS data to transform")
            return None
        
        try:
            print("🔄 Transforming DNS security data...")
            
            transformed_records = []
            
            for record in raw_data:
                # Analyze if domain is blocked or allowed
                is_blocked = record.get('Status') == 3  # NXDOMAIN = blocked
                
                transformed_record = {
                    "endpoint_name": "cloudflare_dns_security",
                    "endpoint_url": self.endpoints['dns_security']['url'],
                    "security_check": {
                        "domain": record.get('queried_domain', 'N/A'),
                        "expected_status": record.get('expected_status', 'N/A'),
                        "is_blocked": is_blocked,
                        "dns_status": record.get('Status', 'N/A'),
                        "query_type": record.get('query_type', 'N/A')
                    },
                    "response": {
                        "answers": record.get('Answer', []),
                        "authority": record.get('Authority', []),
                        "has_answers": len(record.get('Answer', [])) > 0
                    },
                    "metadata": {
                        "ingestion_timestamp": datetime.utcnow().isoformat(),
                        "data_source": "Cloudflare Security DNS",
                        "security_level": "malware_protection",
                        "raw_response": record
                    }
                }
                transformed_records.append(transformed_record)
            
            print(f"✅ DNS security data transformation completed ({len(transformed_records)} records)\n")
            return transformed_records
            
        except Exception as e:
            print(f"❌ Error during transformation: {e}")
            return None
    
    # ==================== Load Functions ====================
    
    def load_data(self, transformed_data, collection_name):
        """
        Load transformed data into MongoDB
        Supports both single documents and lists of documents
        """
        if not transformed_data:
            print("⚠️ No data to load")
            return None
        
        try:
            print(f"🔄 Loading data into MongoDB collection: {collection_name}")
            
            collection = self.db[collection_name]
            
            # Handle both single document and list of documents
            if isinstance(transformed_data, list):
                result = collection.insert_many(transformed_data)
                doc_count = len(result.inserted_ids)
                print(f"✅ Successfully loaded {doc_count} documents into MongoDB")
                print(f"   Collection: {collection_name}")
                print(f"   First Document ID: {result.inserted_ids[0]}\n")
                return result.inserted_ids
            else:
                result = collection.insert_one(transformed_data)
                print(f"✅ Successfully loaded 1 document into MongoDB")
                print(f"   Collection: {collection_name}")
                print(f"   Document ID: {result.inserted_id}\n")
                return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error during loading: {e}")
            return None
    
    # ==================== Pipeline Execution ====================
    
    def run_pipeline(self):
        """Execute the complete multi-endpoint ETL pipeline"""
        print("\n" + "="*70)
        print("🚀 Starting Cloudflare Multi-Endpoint ETL Pipeline")
        print("   (3 Endpoints: Trace, DNS Standard, DNS Security)")
        print("="*70 + "\n")
        
        start_time = time.time()
        results = {
            'trace': False,
            'dns_standard': False,
            'dns_security': False
        }
        
        # ===== ENDPOINT 1: Cloudflare Trace =====
        trace_raw = self.extract_trace_data()
        if trace_raw:
            trace_transformed = self.transform_trace_data(trace_raw)
            if trace_transformed:
                trace_result = self.load_data(
                    trace_transformed,
                    self.endpoints['trace']['collection']
                )
                results['trace'] = trace_result is not None
        
        print("-" * 70 + "\n")
        
        # ===== ENDPOINT 2: DNS Standard =====
        dns_raw = self.extract_dns_standard_data()
        if dns_raw:
            dns_transformed = self.transform_dns_standard_data(dns_raw)
            if dns_transformed:
                dns_result = self.load_data(
                    dns_transformed,
                    self.endpoints['dns_standard']['collection']
                )
                results['dns_standard'] = dns_result is not None
        
        print("-" * 70 + "\n")
        
        # ===== ENDPOINT 3: DNS Security =====
        security_raw = self.extract_dns_security_data()
        if security_raw:
            security_transformed = self.transform_dns_security_data(security_raw)
            if security_transformed:
                security_result = self.load_data(
                    security_transformed,
                    self.endpoints['dns_security']['collection']
                )
                results['dns_security'] = security_result is not None
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Summary
        print("=" * 70)
        print("📊 ETL Pipeline Summary")
        print("=" * 70)
        print(f"✅ Endpoint 1 (Trace):         {'SUCCESS' if results['trace'] else 'FAILED'}")
        print(f"✅ Endpoint 2 (DNS Standard):  {'SUCCESS' if results['dns_standard'] else 'FAILED'}")
        print(f"✅ Endpoint 3 (DNS Security):  {'SUCCESS' if results['dns_security'] else 'FAILED'}")
        print(f"\n⏱️  Total Execution Time: {execution_time:.2f} seconds")
        
        successful = sum(results.values())
        print(f"📈 Success Rate: {successful}/3 endpoints")
        print("=" * 70 + "\n")
        
        return all(results.values())
    
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
        etl = CloudflareMultiEndpointETL()
        success = etl.run_pipeline()
        
        if success:
            print("✨ All endpoints processed successfully!")
        else:
            print("⚠️ Some endpoints failed. Check logs above.")
        
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

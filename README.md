# Cloudflare Trace ETL Connector

**Author:** Pawan Kumar Ramnani
**Roll Number:** 3122225001091 
**Course:** Software Architecture

---

## 📋 Overview

This ETL (Extract, Transform, Load) connector retrieves network trace information from Cloudflare's public trace endpoint and stores it in MongoDB. The connector extracts IP address details, geographic location, TLS version, HTTP version, and other network metadata.

---

## 🔌 API Details

**API Provider:** Cloudflare  
**Endpoint:** `https://www.cloudflare.com/cdn-cgi/trace`  
**Method:** GET  
**Authentication:** None required (public endpoint)  
**Rate Limit:** No strict limits (reasonable use expected)  
**Response Format:** Plain text (key=value pairs)

### Sample API Response:
```
fl=123f45
h=www.cloudflare.com
ip=203.0.113.1
ts=1234567890.123
visit_scheme=https
uag=Mozilla/5.0...
colo=BLR
sliver=none
http=http/2
loc=IN
tls=TLSv1.3
sni=plaintext
warp=off
gateway=off
```

---

## 🏗️ ETL Pipeline Architecture

### 1. **Extract**
- Connects to Cloudflare Trace API using HTTP GET request
- Retrieves raw trace data in plain text format
- Implements timeout handling (10 seconds)
- Handles connection errors and HTTP status codes

### 2. **Transform**
- Parses key=value pairs from plain text into structured dictionary
- Creates standardized JSON document structure
- Adds metadata fields (ingestion_timestamp, data_source)
- Handles missing or malformed fields gracefully

### 3. **Load**
- Establishes secure connection to MongoDB
- Inserts transformed document into designated collection
- Returns document ID for verification
- Handles insertion errors with detailed logging

---

## 📦 Project Structure

```
cloudflare-trace-etl/
├── etl_connector.py      # Main ETL script
├── .env                   # Environment variables (DO NOT COMMIT)
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MongoDB installed locally or MongoDB Atlas account
- pip package manager

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd <your-branch-name>
```

### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

**For Local MongoDB:**
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=etl_database
COLLECTION_NAME=cloudflare_trace_raw
```

**For MongoDB Atlas (Cloud):**
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DB_NAME=etl_database
COLLECTION_NAME=cloudflare_trace_raw
```

### Step 4: Run the ETL Pipeline
```bash
python etl_connector.py
```

---

## 💾 MongoDB Collection Schema

**Collection Name:** `cloudflare_trace_raw`

### Document Structure:
```json
{
  "_id": "ObjectId(...)",
  "ip_address": "203.0.113.1",
  "timestamp": "1234567890.123",
  "visit_scheme": "https",
  "uag": "Mozilla/5.0 ...",
  "colo": "BLR",
  "sliver": "none",
  "http_version": "http/2",
  "location": "IN",
  "tls_version": "TLSv1.3",
  "sni": "plaintext",
  "warp": "off",
  "gateway": "off",
  "rbi": "off",
  "kex": "X25519",
  "ingestion_timestamp": "2025-10-18T10:30:00.123456",
  "raw_data": { ... },
  "data_source": "Cloudflare Trace API"
}
```

---

## 🧪 Testing & Validation

### Test the Pipeline:

1. **Run the pipeline:**
   ```bash
   python etl_connector.py
   ```

2. **Verify data in MongoDB:**
   ```bash
   mongosh
   > use etl_database
   > db.cloudflare_trace_raw.find().pretty()
   > db.cloudflare_trace_raw.countDocuments()
   ```

3. **Test multiple runs:**
   ```bash
   python etl_connector.py
   python etl_connector.py
   python etl_connector.py
   ```

---

## 📊 Sample Output

```
============================================================
🚀 Starting Cloudflare Trace ETL Pipeline
============================================================

✅ Successfully connected to MongoDB
🔄 Extracting data from Cloudflare Trace API...
✅ Successfully extracted data (Status: 200)

🔄 Transforming data...
✅ Data transformation completed

🔄 Loading data into MongoDB...
✅ Successfully loaded data into MongoDB
   Collection: cloudflare_trace_raw
   Document ID: 507f1f77bcf86cd799439011

============================================================
✅ ETL Pipeline completed successfully!
⏱️  Execution time: 1.23 seconds
============================================================

🔒 MongoDB connection closed
```

---

## 🔒 Security Best Practices

- ✅ All credentials stored in `.env` file
- ✅ `.env` added to `.gitignore`
- ✅ No hardcoded secrets in code
- ✅ Environment variables loaded using `python-dotenv`

---

## 🛠️ Troubleshooting

### Issue: "MongoDB connection failed"
**Solution:** 
```bash
# Check MongoDB is running
sudo systemctl status mongod
sudo systemctl start mongod

# Verify connection string in .env
```

### Issue: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "API timeout"
**Solution:** 
- Check internet connection
- Verify Cloudflare API is accessible
- Try again after a few moments

---

## 📈 Future Enhancements

- [ ] Add scheduling using APScheduler
- [ ] Implement data deduplication
- [ ] Add email notifications for failures
- [ ] Create data visualization dashboard
- [ ] Implement data retention policies

---

## 📚 Resources

- [Cloudflare Trace API](https://www.cloudflare.com/cdn-cgi/trace)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Python Dotenv](https://pypi.org/project/python-dotenv/)
- [Requests Library](https://requests.readthedocs.io/)

---

## 📝 Assignment Compliance

This project follows all assignment guidelines:

✅ API documentation understood and documented  
✅ Secure credentials using `.env`  
✅ Complete ETL pipeline implementation  
✅ MongoDB integration with proper collection strategy  
✅ Error handling and validation  
✅ Proper Git structure and documentation  
✅ Clear README with usage instructions  
✅ Name and roll number in commits

**Last Updated:** October 18, 2025  
**Version:** 1.0  

🚀 Happy Coding!
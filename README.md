# Cloudflare Multi-Endpoint ETL Connector

**Author:** Pawan Kumar Ramnani
**Roll Number:** 3122225001091
**Course:** Software Architecture 

---

## 📋 Overview

This advanced ETL (Extract, Transform, Load) connector extracts data from **THREE different Cloudflare public API endpoints**, transforms the data into structured formats, and loads them into separate MongoDB collections. This demonstrates a comprehensive multi-endpoint data pipeline architecture.

### Why Multiple Endpoints?

Modern ETL systems often need to aggregate data from multiple sources or endpoints to provide comprehensive insights. This project showcases:
- Handling different API response formats (plain text and JSON)
- Managing multiple data streams in a single pipeline
- Organizing data into separate collections for better data management
- Real-world API integration scenarios

---

## 🔌 Three API Endpoints Used

### 🌐 Endpoint 1: Cloudflare Trace API

**Purpose:** Network trace and connection information  
**URL:** `https://www.cloudflare.com/cdn-cgi/trace`  
**Method:** GET  
**Authentication:** None required  
**Response Format:** Plain text (key=value pairs)  
**Data Collected:**
- Public IP address
- Geographic location (country code)
- Cloudflare data center location
- TLS/SSL version
- HTTP version
- User agent information
- WARP/Gateway status

**Sample Response:**
```
fl=123f45
h=www.cloudflare.com
ip=203.0.113.1
ts=1234567890.123
visit_scheme=https
colo=BLR
http=http/2
loc=IN
tls=TLSv1.3
```

---

### 🔍 Endpoint 2: Cloudflare DNS over HTTPS (Standard)

**Purpose:** Standard DNS resolution service  
**URL:** `https://cloudflare-dns.com/dns-query`  
**Method:** GET  
**Authentication:** None required  
**Response Format:** JSON (DNS-JSON format)  
**Data Collected:**
- DNS A records (IPv4 addresses)
- DNS query status
- Response time
- Authority and Additional sections
- DNS flags (recursion, authenticated data, etc.)

**Query Domains:** google.com, cloudflare.com, github.com

**Sample Request:**
```
GET https://cloudflare-dns.com/dns-query?name=google.com&type=A
Header: accept: application/dns-json
```

**Sample Response:**
```json
{
  "Status": 0,
  "TC": false,
  "RD": true,
  "RA": true,
  "AD": true,
  "CD": false,
  "Question": [{"name": "google.com", "type": 1}],
  "Answer": [{"name": "google.com", "type": 1, "TTL": 299, "data": "142.250.190.78"}]
}
```

---

### 🛡️ Endpoint 3: Cloudflare DNS over HTTPS (Security)

**Purpose:** Security-enhanced DNS with malware blocking  
**URL:** `https://security.cloudflare-dns.com/dns-query`  
**Method:** GET  
**Authentication:** None required  
**Response Format:** JSON (DNS-JSON format)  
**Special Features:**
- Blocks access to malicious domains
- Malware protection
- Phishing protection
- Returns NXDOMAIN for blocked sites

**Data Collected:**
- DNS resolution with security filtering
- Domain safety status
- Blocked/Allowed classification
- Security metadata

**Key Difference:** This endpoint blocks known malicious domains automatically, while the standard DNS endpoint does not.

---

## 🏗️ ETL Pipeline Architecture

### Multi-Endpoint Flow:

```
┌─────────────────────────────────────────────────────┐
│          Cloudflare Multi-Endpoint ETL              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Endpoint 1  │  │  Endpoint 2  │  │Endpoint 3│ │
│  │    Trace     │  │  DNS Std     │  │DNS Sec   │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                │       │
│         ▼                 ▼                ▼       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Transform   │  │  Transform   │  │Transform │ │
│  │  (Key-Value) │  │    (JSON)    │  │  (JSON)  │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                │       │
│         ▼                 ▼                ▼       │
│  ┌──────────────────────────────────────────────┐ │
│  │            MongoDB Database                  │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │ │
│  │  │trace_data│ │dns_std   │ │dns_security  │ │ │
│  │  └──────────┘ └──────────┘ └──────────────┘ │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Pipeline Stages:

**1. Extract (per endpoint):**
- Makes HTTP GET request to each endpoint
- Handles different response formats (text vs JSON)
- Implements timeout and error handling
- Queries multiple domains for DNS endpoints

**2. Transform (per endpoint):**
- Parses raw data into structured format
- Adds metadata (timestamps, source info)
- Creates consistent schema per endpoint
- Preserves raw data for audit

**3. Load (per endpoint):**
- Inserts into separate MongoDB collections
- Supports batch insertion for multiple records
- Returns document IDs for verification
- Handles insertion errors gracefully

---

## 📦 Project Structure

```
cloudflare-multi-endpoint-etl/
├── etl_connector.py      # Main multi-endpoint ETL script
├── .env                   # Environment variables (DO NOT COMMIT)
├── requirements.txt       # Python dependencies
├── README.md             # This comprehensive documentation
└── .gitignore            # Git ignore rules
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.7 or higher
- MongoDB installed locally or MongoDB Atlas account
- pip package manager
- Internet connection

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter OpenSSL or urllib3 errors, the requirements.txt includes the fix (`urllib3==1.26.18`).

### Step 2: Configure MongoDB

Create a `.env` file in the project root:

**For Local MongoDB:**
```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=etl_database
```

**For MongoDB Atlas:**
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DB_NAME=etl_database
```

### Step 3: Run the Pipeline

```bash
python etl_connector.py
```

---

## 💾 MongoDB Collections Schema

### Collection 1: `cloudflare_trace_data`

```json
{
  "_id": "ObjectId(...)",
  "endpoint_name": "cloudflare_trace",
  "endpoint_url": "https://www.cloudflare.com/cdn-cgi/trace",
  "data": {
    "ip_address": "203.0.113.1",
    "timestamp": "1234567890.123",
    "visit_scheme": "https",
    "user_agent": "Mozilla/5.0...",
    "datacenter": "BLR",
    "http_version": "http/2",
    "location": "IN",
    "tls_version": "TLSv1.3",
    "gateway": "off",
    "warp": "off"
  },
  "metadata": {
    "ingestion_timestamp": "2025-10-18T10:30:00.123456",
    "data_source": "Cloudflare Trace API",
    "raw_data": {...}
  }
}
```

### Collection 2: `cloudflare_dns_standard_data`

```json
{
  "_id": "ObjectId(...)",
  "endpoint_name": "cloudflare_dns_standard",
  "endpoint_url": "https://cloudflare-dns.com/dns-query",
  "query": {
    "domain": "google.com",
    "type": "A",
    "status": 0
  },
  "response": {
    "answers": [
      {
        "name": "cloudflare.com",
        "type": 1,
        "TTL": 300,
        "data": "104.16.132.229"
      }
    ],
    "authority": [],
    "has_answers": true
  },
  "metadata": {
    "ingestion_timestamp": "2025-10-18T10:30:02.789012",
    "data_source": "Cloudflare Security DNS",
    "security_level": "malware_protection",
    "raw_response": {...}
  }
}
```

---

## 🧪 Testing & Validation

### Test 1: Run the Complete Pipeline

```bash
python etl_connector.py
```

### Expected Output:

```
======================================================================
🚀 Starting Cloudflare Multi-Endpoint ETL Pipeline
   (3 Endpoints: Trace, DNS Standard, DNS Security)
======================================================================

✅ Successfully connected to MongoDB
   Database: etl_database

📍 ENDPOINT 1: Cloudflare Trace API
🔄 Extracting network trace data...
✅ Successfully extracted trace data (Status: 200)
🔄 Transforming trace data...
✅ Trace data transformation completed

🔄 Loading data into MongoDB collection: cloudflare_trace_data
✅ Successfully loaded 1 document into MongoDB
   Collection: cloudflare_trace_data
   Document ID: 507f1f77bcf86cd799439011

----------------------------------------------------------------------

📍 ENDPOINT 2: Cloudflare DNS over HTTPS (Standard)
🔄 Extracting DNS resolution data...
   ✓ Retrieved A record for google.com
   ✓ Retrieved A record for cloudflare.com
   ✓ Retrieved A record for github.com
✅ Successfully extracted DNS data for 3 queries

🔄 Transforming DNS standard data...
✅ DNS standard data transformation completed (3 records)

🔄 Loading data into MongoDB collection: cloudflare_dns_standard_data
✅ Successfully loaded 3 documents into MongoDB
   Collection: cloudflare_dns_standard_data
   First Document ID: 507f1f77bcf86cd799439012

----------------------------------------------------------------------

📍 ENDPOINT 3: Cloudflare DNS over HTTPS (Security)
🔄 Extracting security DNS data...
   ✓ Security check for cloudflare.com: safe
   ✓ Security check for google.com: safe
   ✓ Security check for example.com: safe
✅ Successfully extracted security DNS data for 3 queries

🔄 Transforming DNS security data...
✅ DNS security data transformation completed (3 records)

🔄 Loading data into MongoDB collection: cloudflare_dns_security_data
✅ Successfully loaded 3 documents into MongoDB
   Collection: cloudflare_dns_security_data
   First Document ID: 507f1f77bcf86cd799439013

======================================================================
📊 ETL Pipeline Summary
======================================================================
✅ Endpoint 1 (Trace):         SUCCESS
✅ Endpoint 2 (DNS Standard):  SUCCESS
✅ Endpoint 3 (DNS Security):  SUCCESS

⏱️  Total Execution Time: 3.45 seconds
📈 Success Rate: 3/3 endpoints
======================================================================

✨ All endpoints processed successfully!
🔒 MongoDB connection closed
```

---

### Test 2: Verify Data in MongoDB

```bash
mongosh

# Connect to database
> use etl_database

# Check all collections
> show collections
cloudflare_trace_data
cloudflare_dns_standard_data
cloudflare_dns_security_data

# Count documents in each collection
> db.cloudflare_trace_data.countDocuments()
1

> db.cloudflare_dns_standard_data.countDocuments()
3

> db.cloudflare_dns_security_data.countDocuments()
3

# View sample data from each endpoint
> db.cloudflare_trace_data.findOne()
> db.cloudflare_dns_standard_data.findOne()
> db.cloudflare_dns_security_data.findOne()

# Query specific fields
> db.cloudflare_trace_data.find({}, {
    "data.ip_address": 1,
    "data.location": 1,
    "data.datacenter": 1
  }).pretty()

> db.cloudflare_dns_standard_data.find({}, {
    "query.domain": 1,
    "response.answers": 1
  }).pretty()

> db.cloudflare_dns_security_data.find({}, {
    "security_check.domain": 1,
    "security_check.is_blocked": 1
  }).pretty()
```

---

### Test 3: Run Multiple Times

```bash
# Run pipeline 3 times to test consistency
python etl_connector.py
python etl_connector.py
python etl_connector.py

# Verify document counts increase
mongosh
> use etl_database
> db.cloudflare_trace_data.countDocuments()
3
> db.cloudflare_dns_standard_data.countDocuments()
9
> db.cloudflare_dns_security_data.countDocuments()
9
```

---

## 📊 Data Analysis Examples

### Example 1: Track IP Address Changes

```javascript
// Find all unique IP addresses over time
db.cloudflare_trace_data.aggregate([
  {
    $group: {
      _id: "$data.ip_address",
      count: { $sum: 1 },
      locations: { $addToSet: "$data.location" }
    }
  }
])
```

### Example 2: DNS Response Time Analysis

```javascript
// Analyze DNS query patterns
db.cloudflare_dns_standard_data.aggregate([
  {
    $group: {
      _id: "$query.domain",
      total_queries: { $sum: 1 },
      avg_answers: { $avg: { $size: "$response.answers" } }
    }
  }
])
```

### Example 3: Security Checks Summary

```javascript
// Count blocked vs safe domains
db.cloudflare_dns_security_data.aggregate([
  {
    $group: {
      _id: "$security_check.is_blocked",
      count: { $sum: 1 },
      domains: { $push: "$security_check.domain" }
    }
  }
])
```

---

## 🔒 Security Best Practices

- ✅ All MongoDB credentials stored in `.env` file
- ✅ `.env` added to `.gitignore` (never committed)
- ✅ No hardcoded secrets in source code
- ✅ Environment variables loaded securely using `python-dotenv`
- ✅ Rate limiting implemented between API calls
- ✅ Timeout handling for all HTTP requests
- ✅ Graceful error handling with detailed logging

---

## 🛠️ Troubleshooting

### Issue: "urllib3 v2.0 only supports OpenSSL 1.1.1+"

**Solution:**
```bash
pip install urllib3==1.26.18 --force-reinstall
```
This is already included in `requirements.txt`.

### Issue: "MongoDB connection failed"

**Solution:**
```bash
# For local MongoDB - start the service
sudo systemctl start mongod

# For MongoDB Atlas - check:
# 1. Correct username/password in MONGO_URI
# 2. IP whitelist includes your IP (or 0.0.0.0/0)
# 3. Connection string format is correct
```

### Issue: "DNS query timeout"

**Solution:**
- Check internet connection
- Cloudflare DNS might be temporarily unavailable
- Try again after a few moments
- The script implements automatic retry logic

### Issue: "Empty collections after running"

**Solution:**
```bash
# Check if script completed successfully
# Look for "SUCCESS" messages in output

# Verify MongoDB connection
mongosh
> db.adminCommand('ping')

# Check collections exist
> show collections
```

---

## 📈 Future Enhancements

### Potential Improvements:

- [ ] **Scheduling:** Add cron job or APScheduler for automated runs
- [ ] **More DNS Record Types:** Query AAAA (IPv6), MX, TXT, CNAME records
- [ ] **Data Aggregation:** Create summary collections with analytics
- [ ] **Visualization Dashboard:** Build Grafana/Plotly dashboard
- [ ] **Email Alerts:** Notify on pipeline failures or anomalies
- [ ] **Data Retention:** Implement TTL indexes for automatic cleanup
- [ ] **Performance Metrics:** Track API response times and store in DB
- [ ] **Concurrent Processing:** Use threading for parallel endpoint processing
- [ ] **Data Deduplication:** Check for duplicate entries before insertion
- [ ] **Advanced Security Checks:** Test with known malicious domain lists

---

## 📚 Technical Resources

### API Documentation:
- [Cloudflare Trace API](https://www.cloudflare.com/cdn-cgi/trace)
- [Cloudflare DNS over HTTPS](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/)
- [DNS-JSON Format RFC](https://datatracker.ietf.org/doc/html/rfc8427)

### Python Libraries:
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/)
- [Requests Library](https://requests.readthedocs.io/en/latest/)
- [Python Dotenv](https://pypi.org/project/python-dotenv/)

### MongoDB:
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [MongoDB Aggregation Pipeline](https://www.mongodb.com/docs/manual/core/aggregation-pipeline/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html)

---

## 📝 Assignment Compliance

### ✅ All Requirements Met:

**Requirement 1: Multiple Endpoints**
- ✅ **3 different endpoints** from Cloudflare
- ✅ Each endpoint serves a different purpose
- ✅ Different data formats handled (text and JSON)

**Requirement 2: Complete ETL Pipeline**
- ✅ **Extract:** Data retrieved from all 3 endpoints
- ✅ **Transform:** Data parsed and structured appropriately
- ✅ **Load:** Data inserted into separate MongoDB collections

**Requirement 3: Secure Configuration**
- ✅ Credentials in `.env` file
- ✅ `.env` excluded from Git
- ✅ Environment variables loaded securely

**Requirement 4: MongoDB Strategy**
- ✅ **3 separate collections** (one per endpoint)
- ✅ Ingestion timestamps included
- ✅ Raw data preserved for audit

**Requirement 5: Testing & Validation**
- ✅ Error handling for all failure scenarios
- ✅ Timeout handling implemented
- ✅ Rate limiting between requests
- ✅ Success/failure logging

**Requirement 6: Documentation**
- ✅ Comprehensive README with all details
- ✅ API documentation for each endpoint
- ✅ Setup instructions included
- ✅ Testing guide provided
- ✅ Troubleshooting section

**Requirement 7: Code Quality**
- ✅ Clean, well-structured code
- ✅ Proper comments and docstrings
- ✅ Object-oriented design
- ✅ Modular functions for each endpoint

---

## 🎯 Key Differentiators of This Project

### Why This Implementation Stands Out:

1. **Three Distinct Endpoints:** Not just variations, but genuinely different APIs with different purposes
2. **Real-World Application:** Demonstrates practical multi-source data integration
3. **Comprehensive Error Handling:** Each endpoint has independent error management
4. **Scalable Architecture:** Easy to add more endpoints following the same pattern
5. **Data Segregation:** Separate collections for better data organization
6. **Detailed Logging:** Step-by-step progress tracking with emojis for clarity
7. **Production-Ready:** Includes rate limiting, timeouts, and retry logic
8. **Educational Value:** Well-documented for learning purposes

---

## 👨‍💻 Development Notes

### Architecture Decisions:

**1. Class-Based Design:**
- Encapsulates all ETL logic in one class
- Makes it easy to add new endpoints
- Maintains state (MongoDB connection) efficiently

**2. Separate Functions Per Endpoint:**
- `extract_*`, `transform_*` for each endpoint
- Makes code modular and maintainable
- Easy to debug individual endpoints

**3. Collection Strategy:**
- One collection per endpoint type
- Allows independent querying and analysis
- Prevents data mixing and schema conflicts

**4. Metadata Preservation:**
- Raw data stored alongside transformed data
- Ingestion timestamps for audit trails
- Source identification for traceability

**5. Error Isolation:**
- Failure in one endpoint doesn't stop others
- Comprehensive error messages
- Summary report at the end

---

## 📞 Support & Contact

For questions, issues, or discussions:
- Post in the **Kyureeus/SSN College WhatsApp group**
- Check Cloudflare and MongoDB documentation
- Review troubleshooting section above
- Consult with classmates and instructors

---

## ⚠️ Important Pre-Submission Checklist

Before submitting your assignment:

- [ ] Replace `[Your Name]` with your actual name
- [ ] Replace `[Your Roll Number]` with your actual roll number
- [ ] Test the pipeline at least 3 times successfully
- [ ] Verify all 3 collections have data in MongoDB
- [ ] Ensure `.env` is NOT committed to Git
- [ ] Include name and roll number in commit messages
- [ ] All dependencies in `requirements.txt` are correct
- [ ] README is comprehensive and accurate
- [ ] Code is well-commented and clean

### Git Commit Message Format:
```
Add Cloudflare Multi-Endpoint ETL connector - [Your Name] [Roll Number]
```

---

## 📄 License

This project is created for educational purposes as part of the SSN CSE Software Architecture course under the Kyureeus EdTech program.

---

## 🙏 Acknowledgments

- **SSN College of Engineering** - CSE Department
- **Kyureeus EdTech** - Assignment framework and guidance
- **Cloudflare** - Public API endpoints (Trace, DNS over HTTPS)
- **MongoDB** - Database platform
- **Instructor** - Requirement clarification for multiple endpoints

---

**Last Updated:** October 20, 2025  
**Version:** 2.0 (Multi-Endpoint)  
**Status:** Production Ready ✅  
**Endpoints:** 3 (Trace, DNS Standard, DNS Security)

---

## 🎓 Learning Outcomes

By completing this multi-endpoint ETL project, you have demonstrated:

1. ✅ **API Integration Skills:** Connecting to multiple REST APIs
2. ✅ **Data Format Handling:** Processing both text and JSON responses
3. ✅ **ETL Architecture:** Building scalable multi-source pipelines
4. ✅ **MongoDB Expertise:** Managing multiple collections efficiently
5. ✅ **Error Handling:** Robust failure management
6. ✅ **Code Organization:** Clean, modular, maintainable code
7. ✅ **Security Practices:** Secure credential management
8. ✅ **Documentation Skills:** Comprehensive technical writing

---

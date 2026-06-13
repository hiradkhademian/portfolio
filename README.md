# 📁 Portfolio Projects

A collection of full-stack and specialized engineering projects showcasing expertise across distributed systems, real-time processing, mobile development, machine learning, and database systems.

---

## 🗂️ Projects Overview

### 1. **SmartGridSentinel** 🔋
**Distributed Real-Time Power Grid Monitoring System**

A production-grade, event-driven microservices architecture for real-time smart grid intelligence with 11 services (Ingestion, Analysis, Regional Trends, Action Gateway, DLQ Monitor, Kafka, PostgreSQL, Redis, Zookeeper, Management API).

**Key Features:**
- gRPC-based telemetry ingestion from smart meters
- Real-time anomaly detection (voltage spikes, consumption anomalies, blackouts)
- Regional trend analysis using Redis sliding windows
- Automated control dispatch with idempotency & audit logging
- Dead letter queue isolation for fault handling
- Professional Excel reporting with Turkish business language
- Comprehensive testing framework (24-point + 100% core functionality tests)
- Complete operational manual and logging infrastructure

**Stack:** Python 3.12, gRPC, Apache Kafka 7.4.0, PostgreSQL, Redis, Docker Compose, pandas, openpyxl

**Key Commands:**
```bash
./simple_start.sh              # Start system with logging
./simple_monitor.sh data       # View organized logs (data flow)
./simple_monitor.sh actions    # View organized logs (actions)
./core_functionality_test.sh   # Run 13-point test suite (100% passing)
```

**Documentation:**
- [README.md](SmartGridSentinel/README.md) - System architecture & design patterns
- [LOGGING_MANUAL.md](SmartGridSentinel/LOGGING_MANUAL.md) - Operational procedures
- [TESTING_GUIDE.md](SmartGridSentinel/TESTING_GUIDE.md) - Testing framework

---

### 2. **GaussianBlurParallel** 🖼️
**Parallel Image Processing with CUDA & OpenMP**

High-performance Gaussian blur implementation using parallel computing techniques for real-time image processing.

**Stack:** C++, CUDA, OpenMP, Image Processing

**Location:** `GaussianBlurParallel/`

---

### 3. **Smart_AgriTwin_Project** 🌾
**Digital Twin for Smart Agriculture**

IoT-enabled agricultural monitoring and automation system with sensor integration and real-time data visualization.

**Stack:** Python, IoT, Data Visualization, Real-time Monitoring

**Location:** `Smart_AgriTwin_Project-main/`

---

### 4. **DatabaseProject** 💾
**Advanced Database Design & Optimization**

Complex relational database design with optimization strategies, query performance tuning, and data integrity patterns.

**Stack:** SQL, Database Design, Optimization, Indexing

**Location:** `DatabaseProject/`

---

### 5. **EmergencyResponseApp** 📱
**Mobile Emergency Response Platform**

Cross-platform iOS application for emergency response coordination with real-time communication and location tracking.

**Quick Start:**

**Terminal 1: Backend**
```bash
cd EmergencyResponseApp
source venv/bin/activate
python app.py
```

**Terminal 2: Metro Bundler**
```bash
cd EmergencyResponseApp/mobil
npx react-native start --port 8081
```

**Terminal 3: iOS Simulator**
```bash
cd EmergencyResponseApp/mobil
npx react-native run-ios --simulator="iPhone 16"
```

**Stack:** Python (Flask), React Native, TypeScript, iOS

**Location:** `EmergencyResponseApp/`

---

### 6. **Transformer-Project** 🤖
**Transformer Model Implementation**

Deep learning project implementing transformer architecture for NLP tasks.

**Stack:** Python, PyTorch, Transformers, NLP

**Location:** `Transformer-Project/`

---

### 7. **MSGuidApp** 📍
**Mobile GPS-Based Guidance System**

Location-based services application with real-time navigation and geospatial features.

**Stack:** Mobile Development, GPS/GIS, Location Services

**Location:** `MSGuidApp/`

---

## 📊 Portfolio Statistics

| Metric | Count |
|--------|-------|
| Total Projects | 7 |
| Primary Languages | Python, C++, TypeScript/JavaScript, SQL |
| Architecture Patterns | Event-Driven, Microservices, Client-Server, Mobile |
| Database Systems | PostgreSQL, Redis, SQLite, SQL Server |
| Message Queues | Kafka, RabbitMQ |
| Container Technologies | Docker, Docker Compose |
| Mobile Frameworks | React Native |
| GPU Computing | CUDA |
| Machine Learning | PyTorch, Transformers |

---

## 🔧 Common Setup Instructions

### Prerequisites
- Git with SSH configured
- Docker & Docker Compose (for containerized projects)
- Python 3.10+ (for Python projects)
- Node.js 18+ (for JavaScript/TypeScript projects)
- XCode (for iOS development)

### Clone This Repository
```bash
git clone git@github.com:hiradkhademian/portfolio.git
cd portfolio
git checkout projects
```

### Navigate to a Project
```bash
cd SmartGridSentinel  # or any project folder
cat README.md         # Read project-specific instructions
```

---

## 🚀 Quick Project Launchers

**SmartGrid Sentinel (Recommended for complex system demo):**
```bash
cd SmartGridSentinel && ./simple_start.sh
```

**Emergency Response App (Mobile demo):**
```bash
cd EmergencyResponseApp && \
Terminal 1: python app.py & \
Terminal 2: cd mobil && npx react-native start & \
Terminal 3: cd mobil && npx react-native run-ios
```

**Run SmartGrid Tests:**
```bash
cd SmartGridSentinel && ./core_functionality_test.sh
```

---

## 📖 Documentation

Each project contains:
- **README.md** - Project overview, architecture, setup
- **Individual documentation** - Technical guides, API references, deployment instructions

For detailed documentation on SmartGrid Sentinel:
- [System Architecture](SmartGridSentinel/README.md#architecture--design-patterns)
- [Component Details](SmartGridSentinel/README.md#components)
- [Logging & Testing](SmartGridSentinel/README.md#logging-testing--reporting)
- [Operational Manual](SmartGridSentinel/LOGGING_MANUAL.md)
- [Testing Guide](SmartGridSentinel/TESTING_GUIDE.md)

---

## 🎯 Key Achievements

### SmartGridSentinel
- ✅ Complete microservices architecture (11 services)
- ✅ 100% passing core functionality tests (13/13)
- ✅ Professional Excel reporting with Turkish localization
- ✅ Production-grade logging infrastructure
- ✅ Zero-downtime operational design

### Multi-Project
- ✅ Full-stack development across 7 diverse projects
- ✅ Microservices, mobile, AI/ML, database, and parallel computing expertise
- ✅ Strong architectural patterns (event-driven, SOLID, design patterns)
- ✅ Production-ready code with comprehensive testing

---

## 🔗 Repository Structure

```
portfolio/
├── main              # Home documentation
├── projects (this branch)
│   ├── SmartGridSentinel/         # NEW: Distributed grid monitoring system
│   ├── GaussianBlurParallel/      # Parallel image processing
│   ├── Smart_AgriTwin_Project/    # Agricultural IoT digital twin
│   ├── DatabaseProject/            # Database design & optimization
│   ├── EmergencyResponseApp/       # Mobile emergency response
│   ├── Transformer-Project/        # NLP transformer models
│   ├── MSGuidApp/                  # GPS-based guidance
│   └── README.md (this file)
└── projects-backup   # Backup of projects branch
```

---

## 📝 Notes

- Each project is self-contained with its own dependencies and setup instructions
- See individual project README files for specific deployment & usage details
- SmartGrid Sentinel includes production-grade utilities: `simple_start.sh`, `simple_monitor.sh`, testing suites
- All projects follow professional software engineering practices with proper documentation

---

**Last Updated:** June 13, 2026  
**Maintained By:** Hirad Khademian

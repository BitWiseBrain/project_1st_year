# 🎓 Smart Campus Information System (SCIS)

A modern web-based Smart Campus Information System developed using **Python** and **NiceGUI**. The application integrates multiple academic management modules into a single platform for managing student records, course enrollments, fee calculations, file handling, directory scanning, and performance analytics.

## 📌 Project Overview

The Smart Campus Information System (SCIS) was developed as part of the Python Programming Laboratory coursework. The project combines all laboratory experiments into a single integrated application.

The system provides a centralized platform for:

* Student Registration and Grade Evaluation
* Course Enrollment Management
* Student Record Maintenance
* Searching and Sorting Student Data
* Fee Calculation and Management
* CSV-Based Academic Record Storage
* Directory Scanning and File System Analysis
* Student Performance Analytics

Unlike traditional console-based laboratory programs, SCIS is implemented as a full-stack web application using NiceGUI with persistent JSON storage.

---

## 🚀 Features

### 1. Student Registration

* Register students with examination scores.
* Automatic grade evaluation.
* Performance remarks generation.
* Student ID auto-generation.
* Grade visualization through score indicators.

### 2. Course Enrollment Management

* Course creation and enrollment.
* Student-wise enrollment tracking.
* Credit management.
* Maximum course limit enforcement.

### 3. Student Records & Event Analysis

* Academic record management.
* Event participation tracking.
* Set operations:

  * Union
  * Intersection
* Participant analytics.

### 4. Sorting & Searching

Implementation of:

#### Sorting Algorithms

* Bubble Sort
* Selection Sort

#### Searching Algorithms

* Linear Search
* Binary Search

Used for efficient student record retrieval.

### 5. Fee Management System

* Tuition fee calculation
* Hostel fee calculation
* Transport fee calculation
* Total fee computation
* Receipt generation
* Fee history storage

### 6. Academic Record Export

* Export student records to CSV.
* Generate academic summaries.
* Performance statistics.

### 7. Directory Scanner

* Recursive directory traversal.
* File count analysis.
* Folder count analysis.
* Tree structure visualization.
* Exception handling for inaccessible directories.

### 8. Performance Analytics

* Subject-wise performance analysis.
* Average score calculation.
* Top performer identification.
* Visual score comparison.
* Analytics dashboard.

---

## 🏗 System Architecture

SCIS follows a three-layer architecture:

### Presentation Layer

* NiceGUI Web Interface
* Sidebar Navigation
* Interactive Forms
* Real-time Notifications

### Business Logic Layer

* Grade Evaluation
* Fee Computation
* Search Algorithms
* Sorting Algorithms
* Event Analysis

### Data Layer

* JSON-based persistent storage
* CSV file export support

---

## 🛠 Technologies Used

| Technology          | Purpose                   |
| ------------------- | ------------------------- |
| Python              | Core Programming Language |
| NiceGUI             | Web User Interface        |
| JSON                | Persistent Data Storage   |
| CSV                 | Record Export             |
| os Module           | Directory Scanning        |
| collections.Counter | Analytics                 |
| functools.reduce    | Set Operations            |
| datetime            | Date Handling             |
| random              | Analytics Simulation      |

---

## 📂 Project Structure

```text
SCIS/
│
├── Main.py
├── campus_data.json
├── student_records.csv
├── README.md
│
├── Modules
│   ├── Student Registration
│   ├── Course Enrollment
│   ├── Student Records
│   ├── Sorting & Searching
│   ├── Fee Management
│   ├── File Handling
│   ├── Directory Scanner
│   └── Analytics
```

---

## ⚙ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/smart-campus-information-system.git
cd smart-campus-information-system
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install nicegui
```

---

## ▶ Running the Application

Execute:

```bash
python Main.py
```

The application will start on:

```text
http://localhost:8080
```

Open the URL in your browser to access the dashboard.

---

## 💾 Data Storage

### JSON Database

All data is stored in:

```text
campus_data.json
```

Stores:

* Student Records
* Course Information
* Fee Details
* Event Data

### CSV Export

Academic records can be exported to:

```text
student_records.csv
```

---

## 📊 Algorithms Implemented

### Sorting

* Bubble Sort
* Selection Sort

### Searching

* Linear Search
* Binary Search

### Set Operations

* Union
* Intersection

### Analytics

* Grade Distribution
* Average Score Calculation
* Subject-wise Performance Analysis

---

## 🎯 Learning Outcomes

This project demonstrates:

* Python Programming Fundamentals
* Data Structures
* Functions and Modular Programming
* File Handling
* Exception Handling
* Sorting Algorithms
* Searching Algorithms
* Set Operations
* Data Persistence
* GUI Development using NiceGUI
* Basic Analytics and Visualization

---

## 📸 Application Modules

1. Dashboard
2. Student Registration
3. Course Enrollment
4. Student Records & Events
5. Sorting & Searching
6. Fee Management
7. CSV Export
8. Directory Scanner
9. Performance Analytics

---

## 👨‍💻 Authors

### Varchas H V

USN: 1DS25AI121

### V Kailash

USN: 1DS25AI118

Department of Computer Science and Engineering

Dayananda Sagar College of Engineering, Bengaluru

Academic Year: 2025-26

---

## 👩‍🏫 Guided By

**Dr. Rohini T V**

Professor

Department of Computer Science and Engineering

Dayananda Sagar College of Engineering

---

## 📜 License

This project is developed for academic and educational purposes as part of the Python Programming Laboratory course at Dayananda Sagar College of Engineering.


# MatchVision

This project presents a **Football Analytics System**, a comprehensive real-time data processing and visualization platform. The system leverages modern big data technologies to provide actionable insights into football (soccer) matches, team performance, and player statistics. Designed with scalability and usability in mind, it features a robust data pipeline and an intuitive web interface.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [Data Pipeline Workflow](#data-pipeline-workflow)
- [Web Application Interfaces](#web-application-interfaces)
- [Challenges and Optimizations](#challenges-and-optimizations)
- [Getting Started](#getting-started)

---

## Project Overview

**MatchVision** handles football-related statistics in real time, providing a seamless experience for users seeking insights into matches, players, teams, and competitions. The platform integrates diverse technologies, combining real-time streaming, data processing, storage, and visualization.
![image](https://github.com/user-attachments/assets/127e245d-9c44-4505-9f4d-105cb64aa89c)
![image](https://github.com/user-attachments/assets/60bf50db-c747-4abc-9ece-1ca4228d3eaa)


### Key Features:
- **Real-time analytics** for football matches, players, and teams.
- Comprehensive **team and player profiles** with statistics and performance trends.
- Dynamic **league standings** with visual indicators for top positions.
- **Interactive dashboards** with dark mode and responsive design.
- Integration of **NoSQL and relational databases** for data management.

---

## Technologies Used

### Backend
- **Kafka**: For real-time message streaming.
- **Apache Spark**: For distributed data processing.
- **MongoDB**: For storing semi-structured data.
- **MySQL**: For storing structured data.
- **Django REST Framework (DRF)**: Backend API for data access.

### Frontend
- **React**: For building the user interface.
- **Chakra UI**: For responsive and accessible design.

### Other Tools
- **Docker**: For deploying services across environments.
- **Python**: For scripting and pipeline development.

---

## System Architecture

The system consists of the following components:
![image](https://github.com/user-attachments/assets/52ab1b23-3f3a-474f-bf50-00ada5601580)

1. **Data Ingestion**: Polls external APIs and publishes data into Kafka topics.
2. **Real-Time Processing**: Uses Spark to process and transform data.
3. **Intermediate Storage**: Stores semi-structured data in MongoDB.
4. **Transformation**: Converts MongoDB data to a relational format using Python scripts.
5. **Persistent Storage**: Stores structured data in MySQL.
6. **Visualization**: Provides real-time analytics via the React frontend and Django API.

---

## Data Pipeline Workflow

1. **Data Ingestion**:
   - External API → Kafka Producers → Kafka Topics.

2. **Real-Time Processing**:
   - Kafka Topics → Spark Streaming → MongoDB Collections.

3. **Transformation to Relational Format**:
   - MongoDB → Python Script → MySQL Tables.

4. **Visualization and Reporting**:
   - MySQL → Django API → React Frontend.

---

## Web Application Interfaces

### Key Views:
- **Dashboard**: Overview of key metrics and trends.
- **Matches**: Insights into match statistics.
- **Teams**: Team profiles with historical and real-time data.
- **Players**: Detailed player analytics.
- **Standings**: Real-time league rankings.

---


## Getting Started

### Prerequisites
- Docker installed on your system.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/username/football-analytics-system.git
   ```
2. Navigate to the project directory:
   ```bash
   cd football-analytics-system
   ```
3. Start the services using Docker Compose:
   ```bash
   docker-compose up
   ```
4. Access the web application at `http://localhost:3000`.

---

Feel free to contribute to the project by submitting pull requests or reporting issues. Enjoy exploring football analytics in real time! 🌟

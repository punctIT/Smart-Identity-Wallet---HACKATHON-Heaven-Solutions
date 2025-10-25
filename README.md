# Smart Identity Wallet

A secure, AI-powered digital identity and document management solution built for the HackHeaven hackathon.

---

## 🏆 Project Overview

**Smart Identity Wallet** is an innovative mobile application that combines military-grade encryption with cutting-edge AI to revolutionize how users manage their identity documents and access legal assistance. Developed by a team of three developers, this project demonstrates the power of modern tech stack integration for solving real-world problems.

---

## 🏗️ Architecture

### Backend Service (Rust)
- **Framework**: [Axum](https://github.com/tokio-rs/axum) – High-performance async web framework
- **Security**:
  - AES-256 encryption for document storage
  - HTTPS/TLS certificates for secure communication
  - Encrypted data transmission
- **Database**: PostgreSQL (with encrypted fields)
- **Design**: Asynchronous microservices architecture
- **Performance**: Non-blocking I/O for optimal scalability

### AI Microservice (Python)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) – Modern async API framework
- **OCR Engine**: Advanced document text extraction
- **AI Provider**: Google Gemini API
- **Capabilities**:
  - Natural language processing
  - Legal query interpretation

### Mobile Client (Kivy)
- **Platform**: Cross-platform (Android/iOS)
- **Communication**: HTTPS REST API
- **Security**: Certificate pinning for API calls
- **UI/UX**: Intuitive document management interface

---

## ✨ Features

### 📱 Document Scanning
- Camera-based document capture

### 🔐 Security
- **Encryption**: AES-256 for data at rest
- **Transport**: HTTPS/TLS 1.3 for data in transit
- **Authentication**: Secure token-based authentication
- **Certificates**: SSL/TLS certificates for all endpoints

### 🤖 AI-Powered Assistant
- **Legal Q&A**: Ask questions about your documents and legal procedures
- **Multi-language Support**: Powered by Gemini AI

---

## 🛠️ Tech Stack

| Component     | Technology                                 |
| ------------- | ------------------------------------------ |
| Backend       | Rust (Axum), PostgreSQL, AES-256           |
| AI Service    | Python (FastAPI), Google Gemini API, OCR   |
| Mobile Client | Python (Kivy), Android/iOS, REST/HTTPS     |

---


## 🤝 Credits

Developed by a team of three at HackHeaven Hackathon.

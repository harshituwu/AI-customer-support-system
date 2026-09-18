TRAINING ASSIGNMENT

AI Customer Support Agent

Student Name: Harshit singh chauhan

Program: B.Tech CSE
Institute: Delhi Technical Campus

1. Project Overview

The AI Customer Support Agent is a Retrieval-Augmented Generation (RAG) based customer support application. It allows users to ask questions about products, orders, delivery, refunds, returns, payments, warranty, and other information stored in a PDF-based knowledge base.

Instead of relying only on the language model's general knowledge, the application first retrieves relevant information from the organization's knowledge base using ChromaDB and then provides that context to Google Gemini through LangChain.

This approach helps the system provide knowledge-grounded responses and clearly indicate when the requested information is not available in the current knowledge base.

2. Objectives

Build an AI-powered customer support assistant.

Implement a Retrieval-Augmented Generation (RAG) pipeline.

Store and search document embeddings using ChromaDB.

Use Google Gemini for natural-language response generation.

Provide a professional web-based chat interface.

Allow administrators/users to upload PDF knowledge documents.

Allow the knowledge base to be reindexed when new documents are uploaded.

Display the source document and page associated with retrieved information.

Reduce unsupported or hallucinated responses by restricting answers to retrieved knowledge.

3. Technologies Used

Technology

Purpose

Python

Backend and application development

FastAPI

REST API and backend server

LangChain

RAG orchestration and LLM integration

Google Gemini

Large Language Model

ChromaDB

Vector database

PDF / PyPDF

PDF document loading

HTML

Frontend structure

CSS

Frontend styling

JavaScript

Frontend interaction and API communication

Uvicorn

ASGI application server

4. System Architecture

                    ┌───────────────────────┐
                    │       User            │
                    │  Customer Question    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Web Frontend        │
                    │ HTML + CSS + JS        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      FastAPI          │
                    │      /api/chat        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     RAG Engine        │
                    │      LangChain        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      ChromaDB         │
                    │ Vector Similarity     │
                    │      Search           │
                    └───────────┬───────────┘
                                │
                         Relevant Context
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Google Gemini      │
                    │   Response Generation │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Answer + Sources      │
                    │      to User          │
                    └───────────────────────┘

Knowledge Base Pipeline

PDF Document
     │
     ▼
PDF Loading
     │
     ▼
Text Extraction
     │
     ▼
Document Chunking
     │
     ▼
Embeddings
     │
     ▼
ChromaDB
     │
     ▼
Semantic Retrieval
     │
     ▼
Relevant Context
     │
     ▼
Gemini

5. Project Structure

AI-Customer-Support-Agent/
│
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── ingest.py
│   └── rag.py
│
├── knowledge_base/
│   └── README.md
│
├── chroma_db/
│
├── uploads/
│   └── .gitkeep
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

6. Main Components

app/app.py

The FastAPI application provides:

Home page

Health check

Chat API

PDF upload API

Knowledge-base reindex API

Project information API

app/ingest.py

Responsible for processing PDF knowledge-base documents:

Finding PDF files.

Loading PDF pages.

Splitting documents into chunks.

Creating embeddings.

Storing the resulting vectors in ChromaDB.

app/rag.py

Implements the RAG engine:

Receives the user's question.

Searches ChromaDB for relevant documents.

Builds the retrieved context.

Sends the context and question to Gemini.

Generates a knowledge-grounded response.

Returns the answer and source information.

app/config.py

Contains application configuration such as:

API configuration

ChromaDB directory

Knowledge-base directory

Upload directory

Collection name

Embedding model

Gemini model

Retrieval settings

static/index.html

Provides the customer support interface, including:

SupportAI branding

Chat interface

Suggested questions

Knowledge-base controls

System architecture information

PDF upload interface

static/style.css

Provides the modern dark/glassmorphism interface and responsive styling.

static/script.js

Handles:

Chat requests

API communication

Suggested questions

New conversations

Typing indicator

Health checking

PDF uploads

Knowledge-base reindexing

Toast notifications

Source rendering

7. API Endpoints

Health Check

GET /api/health

Checks whether the backend is online.

Chat

POST /api/chat

Example request:

{
  "question": "What is the refund and return policy?"
}

Example response:

{
  "answer": "The return policy information available in the knowledge base is ...",
  "sources": [
    {
      "source": "customer_support_demo.pdf",
      "page": 1
    }
  ]
}

Upload PDF

POST /api/upload

Uploads a PDF and places it into the knowledge-base directory.

Reindex Knowledge Base

POST /api/reindex

Reads the PDFs in the knowledge base and updates the ChromaDB vector database.

Project Information

GET /api/info

Returns the project's architecture and technology information.

8. How to Run the Project

Step 1: Open the project

cd ~/AI-Customer-Support-Agent

Step 2: Activate the virtual environment

source venv/bin/activate

Step 3: Install dependencies

pip install -r requirements.txt

Step 4: Configure environment variables

Create/update .env with the required Google Gemini API key.

Example:

GOOGLE_API_KEY=your_api_key_here

Never commit the real API key to GitHub.

Step 5: Ingest the knowledge base

python -m app.ingest

Step 6: Start the FastAPI server

uvicorn app.app:app --reload

Step 7: Open the application

Open the local application in your browser at:

http://127.0.0.1:8000

9. Testing

The following questions can be used to demonstrate the RAG system:

Refund

What is the refund processing time after a returned product is approved?

Delivery

How long does standard delivery take?

Payment

What payment methods are supported?

Warranty

Does the warranty cover accidental damage?

Return Policy

How many days do I have to return a product?

Knowledge Boundary Test

What is the capital of France?

For information that is not present in the knowledge base, the system is designed to state that the information is not available rather than inventing company-specific information.

10. PDF Knowledge Base Management

The application provides two knowledge-base management operations from the frontend.

Upload

Select Upload Knowledge PDF and choose a PDF document.

The file is uploaded to the backend and copied into the knowledge-base directory.

Reindex

After uploading a new document, select Reindex Knowledge Base.

The ingestion pipeline processes the available PDFs and updates ChromaDB.

After reindexing, questions about the newly added document can be asked through the chat interface.

11. Key Features

Modern AI customer support dashboard

Retrieval-Augmented Generation

PDF-based knowledge base

Semantic document retrieval

Persistent ChromaDB vector database

Google Gemini response generation

Source and page references

PDF upload

Knowledge-base reindexing

Backend health monitoring

Suggested questions

Typing animation

New conversation functionality

Responsive frontend

Error handling

Knowledge-grounded responses

12. RAG Approach

The project follows the standard Retrieval-Augmented Generation workflow:

User Question
     ↓
Question Processing
     ↓
Vector Similarity Search
     ↓
Relevant Document Chunks
     ↓
Context Construction
     ↓
Gemini Prompt
     ↓
AI Generated Answer
     ↓
Answer + Source Information

The system prompt instructs the AI customer support agent to use only the retrieved knowledge-base context and to avoid inventing company policies, prices, refunds, delivery information, or product details.

13. Learning Outcomes

Through this training assignment, the project demonstrates practical experience with:

Generative AI

Retrieval-Augmented Generation

Large Language Models

Vector databases

Semantic search

Document processing

LangChain

FastAPI

REST APIs

Frontend-backend integration

PDF ingestion

AI application architecture

Knowledge-grounded response generation

14. Conclusion

The AI Customer Support Agent demonstrates how modern Generative AI can be combined with a structured knowledge base to create a practical customer-support application.

The project integrates a web frontend, FastAPI backend, LangChain-based RAG pipeline, ChromaDB vector database, PDF document processing, and Google Gemini to create an end-to-end AI support system.

15. Student Details

Name: Harshit singh chauhan
Course: B.Tech CSE
Institute: Delhi Technical Campus
Assignment: Training Assignment
Project: AI Customer Support Agent

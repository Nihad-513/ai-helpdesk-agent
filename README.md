# Bean & Brew – AI Helpdesk Agent

An AI-powered customer support platform for a fictional online coffee store, built with **Python, Streamlit, Retrieval-Augmented Generation (RAG), Groq, ChromaDB, and SQLite**.

The application combines an AI customer-support assistant with customer account management, support ticket workflows, and dedicated staff dashboards.

## Features

### AI Customer Support
- Retrieval-Augmented Generation (RAG) for knowledge-grounded responses.
- Hybrid information retrieval combining BM25 keyword search and semantic search.
- Reciprocal Rank Fusion (RRF) to combine retrieval results.
- Context-aware follow-up question handling.
- Product catalogue and store-policy knowledge base.
- Source-document tracking for retrieved information.
- Groq-powered response generation.

### Customer Portal
- Customer registration and authentication.
- Dedicated customer dashboard.
- AI-powered support chat.
- Persistent conversation history.
- Support ticket creation and tracking.

### Staff Portal
- Separate staff authentication.
- Administrator and support-agent roles.
- Staff dashboard for ticket management.
- Agent-specific ticket access and assignment controls.
- Ticket status management.
- Restrictions preventing agents from modifying tickets assigned to other agents.
- Resolved tickets cannot be reopened through the normal workflow.

### Data and Security
- SQLite database for application data.
- Password hashing using bcrypt.
- Customer and staff authentication kept separate.
- Customer-level ticket access restrictions.
- Persistent ChromaDB vector storage.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.13.3 |
| Frontend | Streamlit |
| LLM response generation | Groq |
| Additional LLM integration | Google Gemini SDK |
| Embedding model | Sentence Transformers – all-MiniLM-L6-v2 |
| Vector database | ChromaDB |
| Keyword retrieval | BM25 |
| Retrieval fusion | Reciprocal Rank Fusion |
| Application database | SQLite |
| Password security | bcrypt |
| Environment configuration | python-dotenv |

## System Architecture

### RAG Pipeline

The knowledge base is processed through the following stages:

1. **Document Loading:** Loads product and store-policy information.
2. **Text Splitting:** Divides documents into smaller chunks for retrieval.
3. **Embedding Generation:** Converts text chunks into semantic vectors using Sentence Transformers.
4. **Vector Storage:** Stores embeddings in ChromaDB.
5. **Hybrid Retrieval:** Combines BM25 keyword retrieval and semantic similarity search.
6. **Rank Fusion:** Uses Reciprocal Rank Fusion to combine retrieval results.
7. **Response Generation:** Supplies retrieved context to the Groq-powered LLM to generate responses.

### High-Level Architecture

```text
             Customer
                |
                v
         Streamlit Interface
                |
       +--------+---------+
       |                  |
       v                  v
  Customer Portal    Staff Portal
       |                  |
       v                  v
  AI Support Chat    Staff Dashboard
       |                  |
       v                  v
   RAG Pipeline       Ticket Management
       |
       v
  Hybrid Retrieval
   /           \
  BM25       Semantic Search
                |
             ChromaDB
                |
                v
        Retrieved Context
                |
                v
          Groq LLM
                |
                v
        AI Support Response

       SQLite Database
  (Users, Conversations, Tickets)
```

## Project Structure



```text
ai-helpdesk-agent/
│
├── app/
│   ├── auth.py
│   ├── chat.py
│   ├── dashboard.py
│   ├── staff_auth.py
│   ├── staff_dashboard.py
│   └── __init__.py
│
├── data/
│   └── knowledge_base/
│       ├── product_catalogue.txt
│       └── store_policy.txt
│
├── rag/
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── rag_pipeline.py
│   ├── retriever.py
│   ├── text_splitter.py
│   └── vector_store.py
│
├── scripts/
│   ├── check_groq.py
│   ├── ingest_knowledge_base.py
│   ├── list_gemini_models.py
│   ├── manual_rag_smoke_test.py
│   ├── manual_retrieval_smoke_test.py
│   ├── manual_ticket_lookup.py
│   └── manual_ticket_update.py
│
├── tests/
│   ├── conftest.py
│   ├── run_regression.py
│   ├── test_agent_security.py
│   ├── test_auth.py
│   ├── test_customer_data.py
│   ├── test_database.py
│   ├── test_embeddings.py
│   ├── test_loader.py
│   ├── test_rag_followups.py
│   ├── test_rag_responses.py
│   ├── test_retrieval_edge_cases.py
│   ├── test_retrieval_quality.py
│   ├── test_retriever_fallback.py
│   ├── test_saved_conversation.py
│   ├── test_splitter.py
│   ├── test_tickets.py
│   └── test_vector_store.py
│
├── create_first_admin.py
├── create_staff_agent.py
├── database.py
├── llm.py
├── streamlit_app.py
├── chat_cli.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```


## Installation and Setup

### 1. Clone the repository

```bash
git clone <https://github.com/Nihad-513/ai-helpdesk-agent.git>
cd ai-helpdesk-agent
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model_name
GEMINI_FALLBACK_MODELS=your_fallback_model_names
GROQ_API_KEY=your_groq_api_key

BEAN_BREW_DB_PATH=bean_brew.db
CHROMA_DB_PATH=chroma_db
```

Add your own API credentials. Never commit `.env` or expose API keys publicly.

**Note:** The RAG pipeline currently uses Groq for response generation. Gemini is configured as an additional LLM integration.

### 5. Ingest the knowledge base

Before launching the application, process and index the product catalogue and store-policy documents:

```powershell
python -m scripts.ingest_knowledge_base
```

This command loads the documents from `data/knowledge_base/`, splits them into chunks, generates embeddings using Sentence Transformers, and synchronises the resulting vectors with ChromaDB.

Run this command whenever you add, modify, or remove knowledge-base documents.

### 6. Initialise the administrator account

Run:

```powershell
python create_first_admin.py
```

Follow the prompts to create the initial administrator account.

### 7. Create support-agent accounts

After initial setup, create additional support agents using:

```powershell
python create_staff_agent.py
```

### 8. Launch the application

```powershell
streamlit run streamlit_app.py
```
### 9. Persistent Storage

The application uses two local storage locations:

- `BEAN_BREW_DB_PATH`: SQLite database containing customer accounts, staff accounts, conversations, messages, and support tickets.
- `CHROMA_DB_PATH`: ChromaDB directory containing the knowledge-base embeddings.

For hosted deployments, configure both paths to point to persistent storage locations or mounted volumes provided by the hosting platform.

**Important:** Do not rely on temporary application storage for production data. Without persistent storage, customer records, conversations, tickets, and indexed knowledge-base data may be lost when the application is restarted or redeployed.



## Testing

The project includes automated tests and dedicated RAG regression evaluations covering:

- Retrieval quality and relevance.
- Retrieval edge cases and out-of-scope questions.
- RAG response quality and knowledge grounding.
- Context-aware follow-up questions.
- Authentication and access control.
- Customer data isolation.
- Ticket operations.
- Embedding generation and document processing.
- Vector-store synchronisation and retrieval fallback.

### Run automated tests

```powershell
python -m pytest -v
```

**Latest result:** 40 passed, 0 failed.

### Run RAG regression evaluations

```powershell
python -m tests.run_regression
```

**Latest result:** 26/26 checks passed across four suites:

| Regression suite | Passed |
|---|---:|
| Retrieval quality | 6/6 |
| Retrieval edge cases | 8/8 |
| RAG response evaluation | 8/8 |
| RAG follow-up handling | 4/4 |
| **Total** | **26/26** |

The regression evaluations overlap with some of the automated test coverage; these results are reported separately.

## Current Development Status

The core application is implemented and functional, with the following components completed:

- Customer registration, authentication, and dashboard.
- AI-powered support chat using a hybrid RAG pipeline.
- Persistent conversation history and support-ticket management.
- Separate administrator and support-agent workflows.
- Role-based access controls and customer data isolation.
- Automated testing and dedicated RAG regression evaluations.

**Latest verification results:**
- Automated test suite: 40 passed.
- RAG regression evaluations: 26/26 checks passed.

### Potential Future Improvements

- More comprehensive automated integration tests.
- Expanded knowledge-base ingestion and document management.
- Further evaluation of retrieval relevance and answer quality.
- Optional public deployment with persistent storage.
- Monitoring, logging, and support-operation analytics.

## Project Objective

This project explores how Retrieval-Augmented Generation can be integrated into a practical customer-support workflow, combining semantic search, keyword retrieval, LLM-based responses, authentication, and role-based ticket management in a single application.

## Application Screenshots

### Customer Interface

AI Support Chat – Customers can ask product and policy questions and receive context-grounded responses.
![Customer Chat](screenshots/customer-chat.png)

Customer Dashboard – Customers can access their support interface and manage their support tickets.
![Customer Dashboard](screenshots/customer-dashboard.png)

### Staff Interface

Admin Dashboard – Administrators can oversee support operations and manage staff.
![Admin Dashboard](screenshots/admin-dashboard.png)

Agent Workspace – Support agents can view assigned tickets and manage customer requests.
![Agent Workspace](screenshots/agent-workspace.png)
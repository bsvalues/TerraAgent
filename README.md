# PACS-Training Assistant

An AI-driven assistant for PACS-Training that connects to SQL Server, translates natural language to SQL, and provides document retrieval capabilities through a chat interface.

## Features

- **NL2SQL Agent**: Converts natural language questions into SQL queries
- **RAG Pipeline**: Retrieves relevant documents and generates answers
- **Chat UI**: Interactive web interface using Flask and Chainlit
- **Windows Authentication**: Secure database access using Kerberos/AD
- **dbatools.ai Integration**: PowerShell tools for advanced database management
- **Monitoring & Alerting**: Structured logging and Prometheus metrics
- **Custom Analysis Chains**: Specialized tools for levy calculations and neighborhood trends

## Prerequisites

- Python 3.10+
- SQL Server ODBC Driver 18+
- Access to jcharrispacs SQL Server with pacs_training database
- OpenAI API Key (or Azure OpenAI endpoint + key)
- PowerShell with dbatools.ai module installed

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/pacs-training-assistant.git
   cd pacs-training-assistant
   
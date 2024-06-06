# Chatbot Backend

This is the backend part of an intelligent academic chatbot developed for the Faculty of Science and Technology of Tangier (FSTT). The chatbot leverages advanced AI technologies, including Retrieval Augmented Generation (RAG) and fine-tuned language models, to provide accurate and contextually relevant responses to students' and instructors' inquiries.

## Features

- **Retrieval Augmented Generation (RAG)**: Combines retrieval-based and generation-based techniques for accurate and natural responses.
- **Fine-tuned Language Model**: The LLaMA 3 language model is fine-tuned on a custom corpus related to FSTT, ensuring domain-specific understanding.
- **High-performance Backend**: Built with Flask, a lightweight and efficient Python web framework.
- **Model Serving**: Serves the fine-tuned language model and RAG model for real-time inference.
- **Docker Containerization**: The backend is containerized using Docker for easy deployment and scalability.

## Technologies Used

- **Flask**: A micro web framework for Python, used for building the backend API.
- **Hugging Face Transformers**: A library for state-of-the-art natural language processing.
- **PyTorch**: A deep learning framework for model training and serving.
- **ChromaDB**: A vector database for efficient data retrieval.
- **Docker**: A platform for building, deploying, and running containerized applications.

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-username/chatbot_Backend.git
```
2. Clone the repository:
```bash
docker build -t chatbot-backend .
```
3. Run the Docker container:
```bash
docker run -p 5000:5000 chatbot-backend
```
The server will start running on http://localhost:5000.

**Configuration**

The backend can be configured by modifying the following environment variables:

- MODEL_PATH: Path to the fine-tuned language model (e.g., model-unsloth.Q4_K_M.gguf).
- RAG_MODEL_PATH: Path to the RAG model.
- CHROMA_DB_PATH: Path to the ChromaDB database.

**License**

This project is licensed under the MIT License.

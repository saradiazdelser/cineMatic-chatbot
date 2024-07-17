# (Cine)Matic - A Chatbot for All Your Movie Trivia

## Description

Welcome to Matic Chatbot, a comprehensive demonstration of the NeMo Guardrails framework's capabilities. This project highlights how guardrails technology can effectively maintain the language model (LLM) focus, particularly in the context of Retrieval-Augmented Generation (RAG) for answering movie-related questions.

Matic is designed to be an engaging and informative tool for movie enthusiasts, providing accurate answers to a wide range of movie-related trivia. By leveraging LLMs and robust moderation tools, Matic ensures that conversations remain on-topic and informative, showcasing the potential of the NeMo Guardrails framework in real-world applications.

## Technical Details

- **Model:** `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **User Interface (UI):** [ChainLit](https://github.com/Chainlit/chainlit)
- **Inference:** [Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference)
- **Moderation:** [NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- **Vector Store (RAG):** [Qdrant](https://qdrant.tech/)
- **Fact-Checking:** [AlignScore](https://github.com/yuh-zha/AlignScore)

> ### Important Note
>
> Guardrails by NVIDIA NeMo is designed to enhance model behavior by enforcing topic-specific constraints during inference. This ensures more relevant and accurate responses in specific domains like movies.
>
> Guardrails technologies are continually refined but may still exhibit unexpected or inaccurate responses. Please bear this in mind when interacting with the system.

## Installation

We are working with a Python 3.10 environment with the following [dependencies](./requirements.txt). For NeMo Guardrails specifically, please check their [prerequisites page](https://github.com/NVIDIA/NeMo-Guardrails?tab=readme-ov-file#requirements) before installing all our requirements (which includes NeMo Guardrails version). On the official [repo](https://github.com/NVIDIA/NeMo-Guardrails), you can find more information on how to use Guardrails technologies.

### Launching the Demo

1. Clone the repo

    ```bash
    git clone git@github.com:saradiazdelser/guardrails-demo.git
    ```

2. Navigate to the repository

    ```bash
    cd guardrails-demo
    ```

3. Launch Docker Compose
    Start Docker Compose to build and run the services defined in docker-compose.yml:

    ```bash
    docker-compose up -d
    ```

    This command will build the necessary Docker images (if not already built) and start the containers for the Guardrails Demo.

4. Access the Demo
    Once Docker Compose has successfully started the services, you can access the Guardrails Demo

    - **Chatbot**: Visit <http://localhost:8000/> to interact with the deployed Guardrails Demo application.

    - **API**: To interact with the API endpoints, you can use tools like curl or Postman. Here’s a basic example using curl:

    ```bash
    curl -X GET http://localhost:8000/api/health
    ```

5. Stopping the Demo
    To stop the services launched by Docker Compose, press Ctrl + C in the terminal where docker-compose up is running. Alternatively, run the following command in the same directory as docker-compose.yml:

    ```bash
    python app.py
    ```

> Additional Notes
>
> - This setup includes configurations for the backend app, frontend interface and Qdrant DB for RAG.
> - Make sure `docker` and `docker compose` are installed on your machine before proceeding.

### Accessing the Demo

Visit [http://localhost:8000/](http://localhost:8000/) to interact with the deployed chatbot.

Once on the demo site, you can ask movie-related questions to see how the Guardrails keep the model focused on the specified topic.

## Credits

All icons are from [uxwing.com](https://uxwing.com), used under their license allowing free use, modification, and no required attribution.
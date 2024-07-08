# Guardrails-demo

This is our go-to demo to showcase the properties of guardrails.

## Table of contents

1. [Scope](#scope)
2. [Instructions](#instructions)

## Scope

The scope of this project is to showcase the basic functionalities of [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails/tree/main). The rails are programmed to make the LLM stay on topic: the bot will only answer movie-related questions.
i
> **Note**
> Guardrails technologies are not perfect and are still on refinement. Unexpected or inaccurate responses may occur.

The deployed model is the `mistralai/Mixtral-8x7B-Instruct-v0.1` model.

## Instructions

We are working with a Python 3.10 environment with the follwing [dependencies](./requirements.txt). For nemoguardrails speciffically, please check their pre-requisites [page](https://github.com/NVIDIA/NeMo-Guardrails?tab=readme-ov-file#requirements) before installing all our requirements (which includes nemoguardrails version). On the official [repo](https://github.com/NVIDIA/NeMo-Guardrails) you can find more information of how to use guardrails technologies. Steps to launch the demo:

1. Clone repo

    ```bash
    git clone git@github.com:saradiazdelser/guardrails-demo.git
    ```

2. Create a virtual environment

    ```bash
    python -m venv </path/to/new/virtual/environment>
    ```

3. Install [dependencies](./requirements.txt)

    ```bash
    pip install -r requirements.txt
    ```

4. On root directory run

    ```bash
    python app.py
    ```

5. Chat with the deployed [app](http://localhost:8000/).

    ```bash
    http://localhost:8000/
    ```


# Guardrails-demo

This is our go-to demo to showcase the properties of guardrails.

## Table of contents

1. [Scope](#scope)
1. [Instructions](#instructions)
1. [Contributors](#contributors)

## Scope

The scope of this project is to showcase the basic functionalities of [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails/tree/main). The rails are programmed to make the LLM stay on topic, being such topic HPE related questions.

> **Note**
> Guardrails technologies are not perfect and are still on refinement. Unexpected or inaccurate responses may occur.

The deployed model is a `mistral` model.

## Instructions

We are working with a Python 3.11 environment with the follwing [dependencies](./requirements.txt). For nemoguardrails speciffically, please check their pre-requisites [page](https://github.com/NVIDIA/NeMo-Guardrails?tab=readme-ov-file#requirements) before installing all our requirements (which includes nemoguardrails version). On the official [repo](https://github.com/NVIDIA/NeMo-Guardrails) you can find more information of how to use guardrails technologies. Steps to launch the demo

1. Clone repo
1. Install [dependencies](./requirements.txt)

    ```console
    pip install -r requirements.txt
    ```

1. On root directory run

```console
chainlit run app.py -w
```

## Contributors

Big shoutout to Sara Díaz and José González.

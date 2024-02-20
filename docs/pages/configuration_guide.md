# NeMo Guardrails Configuration Guide

A Guardrail Configuration consists of a `config` folder with the following structure:

```
.
├── config
│   ├── rails
│   │   ├── file_1.co
│   │   ├── file_2.co
│   │   └── ...
│   ├── actions
│   │   ├── file_1.py
│   │   ├── file_2.py
│   │   └── ...
│   ├── kb
│   │   ├── doc_1.md
│   │   ├── doc_2.md
│   │   └── ...
│   ├── config.py
│   └── config.yml
```

- `rails.co`: pre-defined conversational guides in *colang* language, needed for implementing the rails. These can be placed either in a single `rails.co` file or in a `rails` folder.
- `actions.py`: custom actions implemented in Python. These are can be placed in an `actions.py` file in the root of the config or in an `actions` sub-package
- `kb`: folder with markdown documents that can be used in a RAG (Retrieval-Augmented Generation) scenario using the built-in Knowledge Base support
- `config.py`: custom Python code that performs additional initialization, e.g. registering a new provider
- `config.yml`: configuration settings for the rails. File name must not be changed

## rails.co

Each `rails.co` file contains explicit schema and examples for the conversation flow. Generally, one can define user, flow and bot schemas.

```
define user express greeting
  "Hello"
  "Hi"

define user ask capabilities
  "What can you do?"
  "What can you help me with?"
  "tell me what you can do"
  "tell me about you"

define flow
  user express greeting
  bot express greeting

define flow
  user ask capabilities
  bot inform capabilities

define bot inform capabilities
  "I am an AI assistant and I'm here to help."
```

## config.py

If the `config.py` module contains an `init` function, it gets called as part of the initialization of the `LLMRails` instance.

For example, we can use the `init` function to initialize the connection to a database and register it as a custom action parameter using the `register_action_param(...)` function:

```python
from nemoguardrails import LLMRails

def init(app: LLMRails):
    # Initialize the database connection
    db = ...

    # Register the action parameter
    app.register_action_param("db", db)
```

## config.yml

The `config.yml` file is made up of different keys: model configuration, instructions, sample conversation, action server, prompts, rails configuration, kb, core, knowledge_base, and others (lowest temperature, custom data, etc).

### models

The models key lets you configure the LLM model used by the guardrails. It has multiple attributes:

- `type`: "main" indicates the main LLM model, while "embeddings" sets the embeddings model used in the guardrails process (e.g., canonical form generation, next step generation) and for the knowledge base functionality.

- `engine`: the LLM provider, e.g., `openai`, `huggingface_endpoint`, `self_hosted`, etc. (*)
- `model`: (optional) the name of the model, e.g., `gpt-3.5-turbo-instruct`.
- `parameters`: any additional parameters, e.g., `temperature`, `top_k`, etc.

```yaml
models:
 - type: main 
   engine: hf_pipeline_falcon

 - type: embeddings 
	 engine: SentenceTransformers
   model: all-MiniLM-L6-v2
```

(*): You can use any LLM provider that is supported by LangChain (see official LangChain for the full list), as well as NeMo LLM Service, a TRT-LLM server (see TRT-LLM documentation for more details), and custom LLM providers (see custom provider guide).

> ❕ Custom engines for custom [tasks](https://github.com/NVIDIA/NeMo-Guardrails/blob/3273ca73b8427a1b8d63cbccc4a62fe2b23ce5ff/docs/user_guides/configuration-guide.md?plain=1#L265)?


### instructions

The general instructions (similar to a system prompt) get appended at the beginning of every prompt. Other type of instructions remains a work in progress.

```bash
instructions:
  - type: general
    content: |
      Below is a conversation between a user and a bot called the Helpful Bot[...]
```

### sample conversation

The sample conversation helps the LLM learn the format, the tone, and how verbose responses should be. This section should have a minimum of two turns. Since we append this sample conversation to every prompt, it is recommended to keep it short and relevant.

```bash
sample_conversation: |
  user "Hi there. Can you help me with some questions I have about physics?"
    express greeting and ask for assistance
  bot express greeting and confirm and offer assistance
    "Hi there! I'm here to help answer any questions you may have about physics. What would you like to know?"
```

### action server url

If an actions server is used, the URL must be configured. See action server documentation for more information.

```bash
actions_server_url: ACTIONS_SERVER_URL
```

### prompts

The prompt key is used to set the prompts that are used for the tasks in the guardrails process (e.g., generate user intent, generate next step, generate bot message). 

```yaml
prompts:
  - task: generate_user_intent
    models:
      - hf_pipeline_falcon
		max_length: 3000
    content: |-
      {{ general_instructions }}
			[...]
      **{{ history | colang | verbose_v1 }}
    output_parser: "verbose_v1"

  - task: general
		[...]
```

You can also specify model used, output parser used, and maximum length (# char) of the prompt. 

When the maximum length is exceeded, the prompt is truncated by removing older turns from the conversation history until the length of the prompt is less than or equal to the maximum length. The default maximum length is 16000 characters.

The full list of tasks used by the NeMo Guardrails toolkit is the following:

- `general`: generate the next bot message, when no canonical forms are used;
- `generate_user_intent`: generate the canonical user message;
- `generate_next_steps`: generate the next thing the bot should do/say;
- `generate_bot_message`: generate the next bot message;
- `generate_value`: generate the value for a context variable (a.k.a. extract user-provided values);
- `self_check_facts`: check the facts from the bot response against the provided evidence;
- `self_check_input`: check if the input from the user should be allowed;
- `self_check_output`: check if bot response should be allowed;
- `self_check_hallucination`: check if the bot response is a hallucination.

### rails

The rails key is used to configure the active guardrails or rails, using their **category** (input, output, dialog, retrieval and execution) as a subkey. These are implemented through **flows**.

- **Input rails** process the message from the user and can alter the input by changing the `$user_message` context variable.
- **Output rails** process a bot message. The message to be processed is available in the context variable `$bot_message` which output rails can alter.
    
    Output rails can deactivate temporarily for the next bot message, by setting the `$skip_output_rails` context variable to `True`.
    
- **Retrieval rails** process the retrieved chunks, i.e., the `$relevant_chunks` variable.
- **Dialog rails** enforce specific predefined conversational paths. They require pre-defined canonical templates for various user messages, which they use to trigger the dialog flows.
    
    The use of dialog rails requires the NeMo Guardrails three-step process (generate canonical user message, decide next step and execute them, generate bot utterance).
    
    There are two configuration options: *single call mode* (all three steps are performed using a single LLM call) and *embeddings only* *mode* (only uses embeddings to interpret the user's message).
    

Dialog and execution rails don't need flows to be enumerated explicitly in the config. But other settings can be configured:

- `single_call.enabled`
- `single_call.fallback_to_multiple_calls`: if the single call fails, fall back to multiple LLM calls.
- `user_messages.embeddings_only`

> ❕ **IMPORTANT**: currently, the *Single Call Mode*  can only predict bot messages as next steps. It will not work if the LLM has to generalize and decide to execute an action on a dynamically generated user canonical form message.


### kb

```yaml
rails:

  input:
    flows:
			- check jailbreak
      - check input sensitive data

  output:
    flows:
			- self check hallucination

	dialog:
    single_call:
      enabled: False
      fallback_to_multiple_calls: True

    user_messages:
      embeddings_only: False
	
	[...]
```

The kb key is used to include documents as part of the knowledge base. These documents must be placed in the `kb` folder inside the `config` folder.

Currently, only the Markdown format is supported.

### core & knowledge base

The core and knowledge_base keys are used to configure the embedding search settings. The default settings are the following:

```yaml
core:
  embedding_search_provider:
    name: default
    parameters:
      embedding_engine: SentenceTransformers
      embedding_model: all-MiniLM-L6-v2

knowledge_base:
  embedding_search_provider:
    name: default
    parameters:
      embedding_engine: SentenceTransformers
      embedding_model: all-MiniLM-L6-v2
```

## Debug methods

If you wish to debug your guardrails, you can use this built-in methods after execution.

```python
info = rails.explain()
info.print_llm_calls_summary()
```
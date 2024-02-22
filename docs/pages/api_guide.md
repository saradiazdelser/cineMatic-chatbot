# Python API

> This is based on the [official documentation](https://web.archive.org/web/20240220104443/https://raw.githubusercontent.com/NVIDIA/NeMo-Guardrails/develop/docs/user_guides/python-api.md) from NeMo Guardrails.
> 

The simplest way for using guardrails in a project is:

1. Create a `RailsConfig` object.
2. Create an `LLMRails` instance which provides an interface to the LLM that automatically applies the configured guardrails.
3. Generate LLM responses using the `LLMRails.generate(...)` or `LLMRails.generate_async(...)` methods.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("path/to/config")
rails = LLMRails(config)

new_message = rails.generate(messages=[{
    "role": "user",
    "content": "Hello! What can you do for me?"
}])
```

## RailsConfig

The `RailsConfig` class contains the key bits of information for configuring guardrails.

- `models`: The list of models used by the rails configuration.
- `user_messages`: The list of user messages that should be used for the rails.
- `bot_messages`: The list of bot messages that should be used for the rails.
- `flows`: The list of flows that should be used for the rails.
- `instructions`: List of instructions in natural language (currently, only general instruction is supported).
- `docs`: List of documents included in the knowledge base.
- `sample_conversation`: The sample conversation to be used inside the prompts.
- `actions_server_url`: The actions server to be used. If specified, the actions will be executed through the actions server.

## Message Generation

The `generate` methods take as input either a `prompt` or a `messages` array. When a prompt is provided, the guardrails apply as in a single-turn conversation. 

The structure of a message is the following:

```yaml
properties:
  role:
    type: "string"
    enum: ["user", "assistant", "context"]
  content:
    oneOf:
      - type: "string"
      - type: "object"

```

An example of conversation history with user, assistant and context messages:

```json
[
  {
    "role": "context",
    "content": {
      "user_name": "John",
      "access_level": "admin"
    }
  },
  {
    "role": "user",
    "content": "Hello!"
  },
  {
    "role": "assistant",
    "content": "Hello! How can I help you?"
  },
  {
    "role": "user",
    "content": "I want to know if my insurance covers certain expenses."
  }
]

```

## Actions

Actions are a key component of the Guardrails toolkit. Actions enable the execution of python code inside guardrails.

### Default Actions

The following are the default actions included in the toolkit:

Core actions:

- `generate_user_intent`: Generate the canonical form for what the user said.
- `generate_next_step`: Generates the next step in the current conversation flow.
- `generate_bot_message`: Generate a bot message based on the desired bot intent.
- `retrieve_relevant_chunks`: Retrieves the relevant chunks from the knowledge base and adds them to the context.

Guardrail-specific actions:

- `self_check_facts`: Check the facts for the last bot response w.r.t. the extracted relevant chunks from the knowledge base.
- `self_check_input`: Check if the user input should be allowed.
- `self_check_output`: Check if the bot response should be allowed.
- `self_check_hallucination`: Check if the last bot response is a hallucination.

For convenience, this toolkit also includes a selection of [LangChain tools](https://web.archive.org/web/20240220100948/https://github.com/NVIDIA/NeMo-Guardrails/blob/develop/docs/user_guides/python-api.md), wrapped as actions.

### Chains as Actions

You can register a Langchain chain as an action using the [LLMRails.register_action](notion://www.notion.so/api/nemoguardrails.rails.llm.llmrails.md#method-llmrailsregister_action) method:

```python
rails.register_action(some_chain, name="some_chain")
```

When a chain is invoked as an action, the parameters of the action correspond to the input keys of the chain. For the return value, if the output of the chain has a single key, the value will be returned. If the chain has multiple output keys, the dictionary of output keys and their values is returned. See the [LangChain Integration Guide](https://web.archive.org/web/20240220104846/https://raw.githubusercontent.com/NVIDIA/NeMo-Guardrails/develop/docs/user_guides/langchain/langchain-integration.md) for more details.

### Custom Actions

You can register any python function as a custom action, using the `action` decorator or with the `register_action()` method. 

By default, the name of the action is set to the name of the function. However, you can change it by specifying a different name.

```python
from nemoguardrails.actions import action

@action()
async def some_action(name="my_action"):
    # Do something
    return "some_result"
```

Actions can take any number of parameters. However, since actions are invoked from Colang flows the parameters' type can only be: *string*, *integer*, *float*, *boolean*, *list* and *dictionary*.

### Special parameters

The following parameters are special and are provided automatically by the NeMo Guardrails toolkit, if they appear in the signature of an action:

| Parameters | Description | Type | Example |
| --- | --- | --- | --- |
| events | The history of events so far; the last one is the one triggering the action itself. | List[dict] | [     {'type': 'UtteranceUserActionFinished', ...},     {'type': 'StartInternalSystemAction', 'action_name': 'generate_user_intent', ...},      {'type': 'InternalSystemActionFinished', 'action_name': 'generate_user_intent', ...} ] |
| context | The context data available to the action. | dict | { 'last_user_message': ...,  'last_bot_message': ..., 'retrieved_relevant_chunks': ... } |
| llm | Access to the LLM instance (BaseLLM from LangChain). | BaseLLM | OpenAI(model="gpt-3.5-turbo-instruct",...) |
| config | The full guardrails configuration instance. | RailsConfig  |  |

# Event-based API

> For more details on the event API, see the [official documentation](https://web.archive.org/web/20240220104411/https://raw.githubusercontent.com/NVIDIA/NeMo-Guardrails/develop/docs/user_guides/advanced/event-based-api.md).


You can use a guardrails configuration through an event-based API using the `generate_events` and  `generate_events_async` methods:

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("path/to/config")
rails= LLMRails(config)

new_events = app.generate_events(events=[{
    "type": "UtteranceUserActionFinished",
    "final_transcript": "Hello! What can you do for me?"
}])
```

## Implementation

To fully implement this event-based API, you'll need to store the events history in a database and continuously update it. The steps are the following:

1. Persist the events history for a particular user in a database.
2. Whenever there is a new message or another event, fetch the history and append the new event.
3. Use the guardrails API to generate the next events.
4. Filter the `StartUtteranceBotAction` events and return them to the user.
5. Persist the history of events back into the database.

## Event Types

NeMo Guardrails supports multiple types of events. Some are meant for internal use (e.g., `UserIntent`, `BotIntent`), while others represent the "public" interface (e.g., `UtteranceUserActionFinished`, `StartUtteranceBotAction`).

| Event | Description |
| --- | --- |
| UtteranceUserActionFinished | The raw message from the user. |
| UserIntent | The computed intent (a.k.a. canonical form) for what the user said. |
| BotIntent | The computed intent for what the bot should say. |
| StartUtteranceBotAction | The final message from the bot. |
| StartInternalSystemAction | An action needs to be started. |
| InternalSystemActionFinished | An action has finished. |
| ContextUpdate | The context of the conversation has been updated. |
| listen | The bot has finished processing the events and is waiting for new input. |

## Custom Events

You can also use custom events. However, you'll need to make sure that the guardrails logic can handle the custom event. Update your flows to deal with the new events where needed. Otherwise, the custom event will just be ignored.
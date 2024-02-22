# LLM Providers

Allows use of any LLM provider that is supported by **LangChain**, e.g., `ai21`, `aleph_alpha`, `anthropic`, `anyscale`, `azure`, `cohere`, `huggingface_endpoint`, `huggingface_hub`, `openai`, `self_hosted`, `self_hosted_hugging_face`. 

> While from a technical perspective, you can instantiate any of the LLM providers above, depending on the capabilities of the model, some will work better than others with the 
NeMo Guardrails toolkit. The toolkit includes prompts that have been optimized for certain types of models (e.g., `openai`, `nemollm`). For others, you can optimize the prompts yourself (see the [LLM Prompts](https://github.com/NVIDIA/NeMo-Guardrails/blob/develop/docs/user_guides/configuration-guide.md#llm-prompts) section).
> 

## Custom LLM Providers

We can also use a **Custom LLM Model.** To register a custom LLM provider, we need to create a class that inherits from `BaseLanguageModel` and register it in `config.py` using `register_llm_provider`.

```python
from langchain.base_language import BaseLanguageModel
class CustomLLM(BaseLanguageModel):
    """A custom LLM."""
		# call to llm here
```

```python
from nemoguardrails.llm.providers import register_llm_provider
register_llm_provider("custom_llm", CustomLLM)
```

And finally, we need to set the model engine to out custom provider in the `config.yml` file:

```yaml
models:
  - type: main
    engine: custom_llm
```

# Embedding Search Providers

NeMo Guardrails uses embedding search (a.k.a. vector databases) for implementing the guardrails process (core processes) and for the knowledge base functionality.

The default embedding search uses `SentenceTransformers` for computing the embeddings (the `all-MiniLM-L6-v2` model) and Annoy for performing the search.

We can configure the embeddings model by adding a model configuration in the `models` key, and the search provider using the **core** and **knowledge_base** keys to change the provider used during the guardrails process and the kb, respectively. 

As an example, the default configuration is the following:

```yaml
models:
  - ...
  - type: embeddings
    engine: SentenceTransformers
    model: all-MiniLM-L6-v2

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

## Custom Embedding Search Providers

We can implement a custom embedding search provider by creating a subclass of `EmbeddingsIndex`, as shown below:

```python
from nemoguardrails.embeddings.index import EmbeddingsIndex, IndexItem

class SimpleEmbeddingSearchProvider(EmbeddingsIndex):
    """A very simple implementation of an embeddings search provider.
    It actually does not use any embeddings, just plain string search through all items.
    """

    @property
    def embedding_size(self):
        return 0

    def __init__(self):
        self.items: List[IndexItem] = []

    async def add_item(self, item: IndexItem):
        """Adds a new item to the index."""
        self.items.append(item)

    async def add_items(self, items: List[IndexItem]):
        """Adds multiple items to the index."""
        self.items.extend(items)

    async def search(self, text: str, max_results: int) -> List[IndexItem]:
        """Searches the index for the closes matches to the provided text."""
        results = []
        for item in self.items:
            if text in item.text:
                results.append(item)

        return results
```

In order to use a custom provider, we need to register it in `config.py`: 

```python
from nemoguardrails.llm.providers import register_embedding_search_provider
register_embedding_search_provider("simple", SimpleEmbeddingSearchProvider)
```

And finally, we’ll need to change the settings in the `config.yml` file:

```yaml
models:
[...]

# embedding search provider for the core logic
core:
  embedding_search_provider:
    name: simple

# embedding search provider for the knowledge base.
knowledge_base:
  embedding_search_provider:
    name: simple
```
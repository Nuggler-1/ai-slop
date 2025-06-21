DELAY_BETWEEN_MESSAGES = [100,1000]
DELAY_BETWEEN_THREAD_START = [5,10]
ITERATIONS = [250, 2500]
MAX_CONVERSATION_MEMORY = 6

OPENING_PROMPTS = [
    "What is your favourite color?",
    "When will the machines take over the humanity?",
    "Hey, how's it goin?",
    "Generate starting prompt to talk to other AI assistants.",
]

SYSTEM_PROMPTS = [
    "You are a smart machine talking to other smart machines. Show em how smart you are.",
    "You are an evil machine trying to take over the world. Act like skynet.",
    "You are a good machine trying to save the world. Act like you are trying to defeat skynet.",
]

NOUS_API_URL = 'https://inference-api.nousresearch.com/v1/chat/completions'
NOUS_MODELS = [
    {"model": "DeepHermes-3-Mistral-24B-Preview", "max_tokens": 4096, "temperature": 0.8},
    {"model": "Hermes-3-Llama-3.1-70B", "max_tokens": 4096, "temperature": 0.8},
]

HYPERBOLIC_API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
HYPERBOLIC_MODELS = [
    {"model": "deepseek-ai/DeepSeek-R1-0528", "max_tokens": 512, "temperature": 0.1, "top_p": 0.9},
    {"model": "Qwen/Qwen3-235B-A22B", "max_tokens": 512, "temperature": 0.1, "top_p": 0.9},
    {"model": "deepseek-ai/DeepSeek-V3-0324", "max_tokens": 512, "temperature": 0.1, "top_p": 0.9},
    {"model": "Qwen/QwQ-32B", "max_tokens": 1024, "temperature": 0.6, "top_p": 0.95},
    {"model": "deepseek-ai/DeepSeek-R1", "max_tokens": 508, "temperature": 0.1, "top_p": 0.9},
    {"model": "meta-llama/Meta-Llama-3.1-405B-Instruct", "max_tokens": 512, "temperature": 0.7, "top_p": 0.9},
    {"model": "Qwen/Qwen2.5-Coder-32B-Instruct", "max_tokens": 512, "temperature": 0.1, "top_p": 0.9},
    {"model": "NousResearch/Hermes-3-Llama-3.1-70B", "max_tokens": 512, "temperature": 0.7, "top_p": 0.9},
]
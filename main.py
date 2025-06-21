import random
import time
import threading
import signal
import os
import ctypes
from typing import Dict, Tuple, Literal
from consts import *
from nous import Nous
from hyperbolic import Hyperbolic
from loguru import logger
from config import *
from consts import logo, PROJECT
import sys

class Runner:
    
    def __init__(self):
        self.hyperbolic_accounts = []
        self.nous_accounts = []
        self._get_accounts()
        self.pairs = self.create_pairs()
    
    def _get_accounts(self,):
        with open(HYPERBOLIC_API_FILE_PATH, "r", encoding="utf-8") as f:
            self.hyperbolic_accounts = f.read().splitlines()
        with open(NOUS_API_FILE_PATH, "r", encoding="utf-8") as f:
            self.nous_accounts = f.read().splitlines()
        with open(PROXY_FILE_PATH, "r", encoding="utf-8") as f:
            proxies = f.read().splitlines()
        if max(len(self.hyperbolic_accounts), len(self.nous_accounts)) > len(proxies):
            logger.error(f"Not enough proxies. Please add at least {max(len(self.hyperbolic_accounts), len(self.nous_accounts))} proxies")
            sys.exit(1)
        
        self.nous_accounts = [
            Nous(
                api_key, 
                random.choice(NOUS_MODELS), 
                random.choice(SYSTEM_PROMPTS), 
                self.get_proxy_for_api_key("nous", api_key)
            ) 
            for api_key in self.nous_accounts
        ]
        self.hyperbolic_accounts = [
            Hyperbolic(
                api_key, 
                random.choice(HYPERBOLIC_MODELS), 
                random.choice(SYSTEM_PROMPTS), 
                self.get_proxy_for_api_key("hyperbolic", api_key)
            ) 
            for api_key in self.hyperbolic_accounts
        ]

    def create_pairs(self):
        account_list = self.nous_accounts + self.hyperbolic_accounts
        random.shuffle(account_list)    
        pairs = []
        for i in range(0, len(account_list)-1, 2):
            pairs.append((account_list[i], account_list[i + 1]))

        if len(account_list) % 2 == 1:
            logger.warning(f"Odd number of accounts. Account {account_list[-1].api_key} will not be used.")
        return pairs

    def get_proxy_for_api_key(self, api_type: Literal["nous", "hyperbolic"], api_key: str) -> Dict[str, str]:

        with open(PROXY_FILE_PATH, "r", encoding="utf-8") as f:
            proxies = f.read().splitlines()
        with open(f"user_files/{api_type}_api.txt", "r", encoding="utf-8") as f:
            api_keys = f.read().splitlines()
        
        if not proxies or not api_keys:
            return {}

        proxy = proxies[api_keys.index(api_key)]
        
        return {
            "http": f"http://{proxy}" if not "http" in proxy else proxy,
            "https": f"http://{proxy}" if not "http" in proxy else proxy
        }


    def run_chat_conversation(
        self,
        conversation_id: int,
        pair: Tuple[Nous | Hyperbolic, Nous | Hyperbolic],
    ):

        
        # Initialize with opening prompt
        initial_prompt = random.choice(OPENING_PROMPTS)
        iterations = random.randint(*ITERATIONS)

        ai_1, ai_2 = pair
        
        # Thread-safe printing with conversation ID
        logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] " + "="*40)
        logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] Starting conversation with {iterations} iterations:")
        logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] " + "="*40)
        
        # Print the initial prompt
        logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] Initial prompt: {initial_prompt}")
        
        try:
            
            conversation_for_ai_1 = []
            conversation_for_ai_2 = []

            # First AI agent generates a response to the initial prompt
            response_1 = ai_1.complete_prompt(
                [{"role": "user", "content": initial_prompt}]
            )
            if not response_1:
                logger.opt(colors=True).error(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #1 ({ai_1.api_key[:20]}...)</blue> failed to respond to initial prompt. Exiting.")
                raise Exception(f"AI #1 ({ai_1.api_key[:20]}...) failed to respond to initial prompt.")
                
            logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #1 ({ai_1.api_key[:20]}...)</blue>:")
            logger.info(response_1)
            conversation_for_ai_2.append({"role": "user", "content": response_1})  # AI #1's message becomes the first user message for AI #2
            
            # Begin the conversational loop
            for i in range(iterations):
                    
                conversation_for_ai_1 = conversation_for_ai_1[-MAX_CONVERSATION_MEMORY:]
                conversation_for_ai_2 = conversation_for_ai_2[-MAX_CONVERSATION_MEMORY:]
                # Add a separator between iterations
                logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] " + "-"*40)
                logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] Iteration {i+1}/{iterations}")
                
                # AI #2 responds to AI #1's message
                response_2 = ai_2.complete_prompt(conversation_for_ai_2)
                if response_2:
                    logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #2 ({ai_2.api_key[:20]}...)</blue>:")
                    logger.info(response_2)
                    conversation_for_ai_2.append({"role": "assistant", "content": response_2})
                    # AI #1 responds to AI #2's message
                    # We need to swap the roles for AI #1's perspective: AI #2's message becomes the user message
                    conversation_for_ai_1.append({"role": "user", "content": response_2})
                else:
                    logger.opt(colors=True).error(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #2 ({ai_2.api_key[:20]}...)</blue> failed to respond.")
                    continue
                
                response_1 = ai_1.complete_prompt(conversation_for_ai_1)
                if response_1:
                    logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #1 ({ai_1.api_key[:20]}...)</blue>:")
                    logger.info(response_1)
                    conversation_for_ai_1.append({"role": "assistant", "content": response_1})
                    conversation_for_ai_2.append({"role": "user", "content": response_1})
                else:
                    logger.opt(colors=True).error(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #1 ({ai_1.api_key[:20]}...)</blue> failed to respond.")
                    continue
                    
                delay = random.randint(*DELAY_BETWEEN_MESSAGES)
                logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] <blue>AI #2 ({ai_2.api_key[:20]}...)</blue> will respond in {delay} seconds.")
                time.sleep(delay)
                    
            logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] " + "="*40)
            logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] Conversation completed!")
            logger.opt(colors=True).info(f"[Conversation <cyan>#{conversation_id}</cyan>] " + "="*40)

        except Exception as e:
            logger.opt(colors=True).error(f"[Conversation <cyan>#{conversation_id}</cyan>] Error: {e}")
    
    def run_parallel_conversations(self): 
        """
        Run multiple chat conversations in parallel using threads.
        Each conversation runs in its own thread allowing for concurrent execution.
        """
        threads = []
        
        for i, pair in enumerate(self.pairs):
            thread = threading.Thread(
                target=self.run_chat_conversation,
                args=(i+1, pair),
                daemon=True, 
            )
            threads.append(thread)
            thread.start()
            logger.opt(colors=True).info(f"[Conversation <cyan>#{i+1}</cyan>] created a separate thread")
            time.sleep(random.randint(*DELAY_BETWEEN_THREAD_START))
        

        # Just wait for threads without blocking Ctrl+C
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
        logger.info("All conversations completed!")

def keyboard_interrupt_handler(sig, frame):
    logger.warning("Ctrl+C pressed. Terminating all threads...")
    os._exit(0)  # Force exit immediately

def main():
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> |  <level>{message}</level>",
        colorize=True
    )
    logger.opt(raw = True).info(logo)
    logger.opt(raw = True, colors=True).info(f'<lm>{PROJECT}</lm>')
    
    try:
        runner = Runner()
        runner.run_parallel_conversations()
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Exiting program.")

if __name__ == "__main__":
    main()

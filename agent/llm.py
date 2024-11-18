import os
import asyncio

# import google.generativeai as genai
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from vertexai.preview import tokenization


class LLM:
    def init_model(self, model_name: str):
        """Not Implemented Error"""
        raise NotImplementedError

    async def get_llm(self, prompt: str):
        """Not Implemented Error"""
        raise NotImplementedError

    async def get_llm(self, prompt: str = None):
        for model in self.model_data:
            model["request_usage"] += 1
            if model["request_usage"] > model["max_request"]:
                model["is_used"] = True
            if model["is_used"] == False:
                return self.init_model(model["model_name"])
        self.reset_model_data()
        raise Exception("No available models")

    def reset_model_data(self):
        for model in self.model_data:
            model["request_usage"] = 0
            model["is_used"] = False


class GroqLLM(LLM):
    def __init__(self):
        self.model_data = self.get_model_data

    @property
    def get_model_data(self):
        return [
            {
                "model_name": "mixtral-8x7b-32768",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "gemma-7b-it",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "gemma2-9b-it",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama-3.1-70b-versatile",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "lama-3.1-8b-instant",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama-3.2-11b-text-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 7000,
            },
            {
                "model_name": "lama-3.2-3b-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 7000,
            },
            {
                "model_name": "llama-3.2-90b-text-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 7000,
            },
            {
                "model_name": "llama-guard-3-8b",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama-3.2-1b-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama3-groq-70b-8192-tool-use-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama3-8b-8192",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
            {
                "model_name": "llama3-groq-8b-8192-tool-use-preview",
                "request_used": 0,
                "is_used": False,
                "max_request": 14400,
            },
        ]  # Need to call the property as a method

    def init_model(self, model_name: str):  # Changed parameter type hint
        llm = ChatGroq(
            model=model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )
        return llm


class GeminiLLM(LLM):
    def __init__(self):
        self.model_data = self.get_model_data  # Need to call the property as a method
        # self.model = genai.GenerativeModel(model_name)
        # self.token = Token(model_name)

    @property
    def get_model_data(self):
        return [
            {
                "model_name": "gemini-1.5-flash",
                "request_usage": 0,
                "is_used": False,
                "max_request": 1500,
            },
            # {
            #     "gemini-1.5-pro": {
            #         "request_usage": 0,
            #         "is_used": False,
            #         "max_request": 50,
            #     }
            # },
            {
                "model_name": "gemini-1.5-flash-8b",
                "request_usage": 0,
                "is_used": False,
                "max_request": 1500,
            },
            {
                "model_name": "gemini-1.0-pro",
                "request_usage": 0,
                "is_used": False,
                "max_request": 1500,
            },
        ]

    def init_model(self, model_name: str):  # Changed parameter type hint
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )
        return llm


class Token:
    def __init__(self, model_name: str):
        self.tokenizer = tokenization.get_tokenizer_for_model(model_name)

    def count_token(self, contents: str):
        return self.tokenizer.count_tokens(contents).total_tokens

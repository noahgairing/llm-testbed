from ..interfaces import LLMInterface
from typing import List
from transformers import pipeline
from utils.models import Message


class localLLMAdapter(LLMInterface):

    def __init__(self, model: str, systemPrompt: str, messageHistory: List[Message]):
        if not self.__validateMessageHistory(messageHistory):
            raise ValueError("Message history not in correct format for this model")

        super().__init__(
            model,
            systemPrompt,
            messageHistory,
            exceptionsForRetry=[]
        )

    def ask(self, message: str, textToComplete: str) -> str:
        pipe = pipeline("text-generation", model=self.model)
        messageHistory = self.getMessageHistory()
        messages = messageHistory + [
            {"role": "system", "content": self.systemPrompt},
            {"role": "user", "content": message},
            {"role": "assistant", "content": textToComplete}
        ]
        
        assistantResponse = pipe(messages=messages)
        
        answer = textToComplete + assistantResponse[0]["generated_text"][3]["content"]

        self.setMessageHistory(messageHistory + [
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": answer
            }
        ])

        return answer

    def __validateMessageHistory(self, messageHistory: List[Message]):
        user = True
        for message in messageHistory:
            if user and message["role"] == "assistant" or not user and message["role"] == "user":
                return False
            user = not user
        return True
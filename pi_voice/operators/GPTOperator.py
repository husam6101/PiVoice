from transformers import GPT2Tokenizer, GPT2ForSequenceClassification
import torch
import random
# from pi_voice.operators import logger
from pi_voice.config import config, get_path_from


class GPTOperator:
    def __init__(self):
        self.model_path = get_path_from(
            config["gpt2"]["model"]
        )
        self.label_map = config["gpt2"]["labelMap"]
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self._load_model()

    def random_command(self, transcript):
        # replace with your list of strings
        command_list = [
            "light_on",
            "light_off",
            # "tv_on",
            # "tv_off",
            "fan_on",
            "fan_off",
            # "do_nothing"
        ]
        return random.choice(command_list)
    
    def _load_model(self):
        model = GPT2ForSequenceClassification.from_pretrained(self.model_path)
        self.model = model
    
    def _encode(self, text):
        return self.tokenizer(text, return_tensors="pt")
    
    def _prediction_to_label(self, predicted_class_index):
        reverse_label_map = {v: k for k, v in self.label_map.items()}
        return reverse_label_map.get(predicted_class_index, "Unknown")  
    
    def predict(self, text):
        inputs = self._encode(text)
        with torch.no_grad():
            outputs = self.model(**inputs)
        predicted_class_index = outputs.logits.argmax(-1).item()
        prediction = self._prediction_to_label(predicted_class_index)
        return prediction

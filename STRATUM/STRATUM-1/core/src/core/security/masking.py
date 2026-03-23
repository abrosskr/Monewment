import sys
import re

class MaskingStream:
    def __init__(self, stream):
        self.stream = stream
        self.patterns = [
            # JSON/KV/Env 모두 대응: 콜론(:)과 등호(=)를 모두 포함
            (re.compile(r'(?i)(password|pwd|secret|token|api_key|key)(["\s:=]+)([ "\']?)([^ "\',}]+)([ "\']?)'), r"\1\2\3[MASKED]\5"),
            # URL Credentials
            (re.compile(r"(://[^:]+):([^@]+)(@)"), r"\1:[MASKED]\3"),
        ]

    def write(self, message):
        masked_message = message
        if message.strip():
            for pattern, replacement in self.patterns:
                masked_message = pattern.sub(replacement, masked_message)
        self.stream.write(masked_message)

    def flush(self):
        self.stream.flush()

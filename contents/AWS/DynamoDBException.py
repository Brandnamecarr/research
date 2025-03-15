
'''
List of error codes:
    5: Insert Error with emplace() function.
'''

class DynamoDBException(Exception):
    def __init__(self, message=None, code=None):
        self.message = message or "An error occurred"
        self.code = code or 69420
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[Error {self.code}]: {self.message}"
        return self.message
class StatusCodeException(Exception):
    def __init__(self, api_response, message="Non 200 Status Code") -> None:
        self.api_response = api_response
        self.message = message
        super().__init__(self.message)

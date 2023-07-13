# Create a derived class for the client errors
class ClientError(Exception):
    # For initiallizing the client error with a message
    def __init__(self, value: str):
        self.value = value
    # For print with the error
    def __str__(self):
        return(repr(self.value))
    

# Method to validate the syntax of a subsrciber nickname
def validate_nickname(nickname: str):
    # Check if it is lower than two characters
    if len(nickname)<2:
        raise ClientError("INVALID Subsriber NICKNAME: shorter than two characters")
    # Check if the first character is not a letter (alphabetical)
    if not nickname[0].isalpha():
        raise ClientError("INVALID Subscriber NICKNAME: first character must be a letter")
    # Check if there is no nickname passed
    if not nickname: 
        raise ClientError("INVALID ARGUMENTS: expected {{nickname}} argument")
    
# Same as previous method addressed for channel nickname errors
def validate_channel(channel: str):
    if len(channel)<2:
        raise ClientError("INVALID Channel NICKNAME: shorter than two characters")
    if not channel[0].isalpha():
        raise ClientError("INVALID Channel NICKNAME: first character must be a letter")
    if not channel: 
        raise ClientError("INVALID ARGUMENTS: expected {{nickname}} argument")
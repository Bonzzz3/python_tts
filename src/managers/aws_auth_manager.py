import keyring

class AWSAuthenticationManager:
    """Handles AWS credential storage and retrieval"""
    SERVICE_NAME = "aws_tts_app"

    def __init__(self, access_key_var, secret_key_var):
        self.access_key_var = access_key_var
        self.secret_key_var = secret_key_var

    def load_credentials(self):
        """Load saved credentials from secure storage"""
        try:
            access_key = keyring.get_password(self.SERVICE_NAME, "access_key_id")
            secret_key = keyring.get_password(self.SERVICE_NAME, "secret_access_key")
            
            if access_key and secret_key:
                self.access_key_var.set(access_key)
                self.secret_key_var.set(secret_key)
                return True
        except Exception as e:
            print(f"Error loading credentials: {e}")
        return False

    def save_credentials(self, remember):
        """Save credentials to secure storage if remember is True"""
        if remember:
            try:
                keyring.set_password(self.SERVICE_NAME, "access_key_id", self.access_key_var.get())
                keyring.set_password(self.SERVICE_NAME, "secret_access_key", self.secret_key_var.get())
                return True
            except Exception as e:
                print(f"Error saving credentials: {e}")
                return False
        return True
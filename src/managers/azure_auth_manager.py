import keyring

class AzureAuthenticationManager:
    """Handles Azure Speech Services credential storage and retrieval"""
    SERVICE_NAME = "azure_tts_app"

    def __init__(self, api_key_var, endpoint_var):
        self.api_key_var = api_key_var
        self.endpoint_var = endpoint_var

    def load_credentials(self):
        """Load saved credentials from secure storage"""
        try:
            api_key = keyring.get_password(self.SERVICE_NAME, "subscription_key")
            endpoint = keyring.get_password(self.SERVICE_NAME, "endpoint")
            
            if api_key and endpoint:
                self.api_key_var.set(api_key)
                self.endpoint_var.set(endpoint)
                return True
        except Exception as e:
            print(f"Error loading Azure credentials: {e}")
        return False

    def save_credentials(self, remember):
        """Save credentials to secure storage if remember is True"""
        if remember:
            try:
                keyring.set_password(self.SERVICE_NAME, "subscription_key", self.api_key_var.get())
                keyring.set_password(self.SERVICE_NAME, "endpoint", self.endpoint_var.get())
                return True
            except Exception as e:
                print(f"Error saving Azure credentials: {e}")
                return False
        return True

    def has_saved_credentials(self):
        """Check if credentials are saved in secure storage"""
        try:
            api_key = keyring.get_password(self.SERVICE_NAME, "subscription_key")
            endpoint = keyring.get_password(self.SERVICE_NAME, "endpoint")
            return bool(api_key and endpoint)
        except Exception as e:
            print(f"Error checking Azure credentials: {e}")
            return False

import subprocess
import platform
import tkinter as tk
from tkinter import ttk, scrolledtext
import boto3
from datetime import datetime
import os

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech App")
        self.root.geometry("800x800")
        
        # AWS Credentials Frame
        cred_frame = ttk.LabelFrame(root, text="AWS Configuration", padding=10)
        cred_frame.pack(pady=10, fill="x", padx=10)
        
        # AWS Access Key ID
        ttk.Label(cred_frame, text="AWS Access Key ID:").grid(row=0, column=0, sticky="w")
        self.access_key_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.access_key_var, width=40).grid(row=0, column=1, sticky="ew")
        
        # AWS Secret Access Key
        ttk.Label(cred_frame, text="AWS Secret Access Key:").grid(row=1, column=0, sticky="w")
        self.secret_key_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.secret_key_var, width=40, show="*").grid(row=1, column=1, sticky="ew")
        
        # AWS Region
        ttk.Label(cred_frame, text="AWS Region:").grid(row=2, column=0, sticky="w")
        self.region_var = tk.StringVar(value="ap-southeast-1")
        ttk.Entry(cred_frame, textvariable=self.region_var, width=40).grid(row=2, column=1, sticky="ew")
        
        # Text Input Frame
        text_frame = ttk.LabelFrame(root, text="Text to Convert", padding=10)
        text_frame.pack(pady=10, fill="both", expand=True, padx=10)
        
        # Text Input
        ttk.Label(text_frame, text="Enter Text:").pack(pady=5)
        self.text_input = scrolledtext.ScrolledText(text_frame, width=60, height=10)
        self.text_input.pack(pady=5, fill="both", expand=True)
        
        # Voice Selection
        ttk.Label(text_frame, text="Select Voice:").pack(pady=5)
        self.voice_var = tk.StringVar(value="Joanna")
        self.voice_dropdown = ttk.Combobox(text_frame, textvariable=self.voice_var)
        self.voice_dropdown['values'] = ['Joanna', 'Matthew', 'Amy', 'Brian']
        self.voice_dropdown.pack(pady=5)
        
        # Generate Button
        self.generate_btn = ttk.Button(text_frame, text="Generate Speech", command=self.generate)
        self.generate_btn.pack(pady=10)
        
        # Status Label
        self.status_label = ttk.Label(text_frame, text="", foreground="green")
        self.status_label.pack(pady=5)

    def generate(self):
        text = self.text_input.get("1.0", tk.END)
        voice = self.voice_var.get()
        
        if not text.strip():
            self.status_label.config(text="Please enter text.", foreground="red")
            return
            
        access_key = self.access_key_var.get()
        secret_key = self.secret_key_var.get()
        region = self.region_var.get()
        
        if not all([access_key, secret_key, region]):
            self.status_label.config(text="AWS credentials are missing.", foreground="red")
            return
            
        try:
            polly = boto3.client(
                'polly',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_path = os.path.join(output_dir, f"tts_output_{voice}_{timestamp}.mp3")
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
                
            self.status_label.config(text=f"Audio saved to: {output_path}", foreground="green")
            
            # Open file to generated audio
            if platform.system() == "Darwin":
                subprocess.run(["open", "-R", output_path])
            # elif platform.system() == "Windows":
            #     subprocess.run(["explorer", "/select,", output_path])
            # elif platform.system() == "Linux":
            #     subprocess.run(["xdg-open", os.path.dirname(output_path)])
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
# Python TTS (Text-to-Speech) App
A Python Text-to-Speech App using Amazon Polly TTS Service. This app takes text from the user and generates audio for it.

<img src="images/Ui.png" width="800" style="border: 2px solid grey; border-radius: 10px;"><br>


## Features
- Convert text to speech using AWS Polly
- Outputs MP3 files to your Downloads folder
- (Coming soon...) Plays converted audio without saving audio

## Setup Guide

### 1. AWS Account Setup

#### Create AWS Account
1. Go to [AWS Homepage](https://aws.amazon.com/)
2. Click "Create Account"
3. Provide:
   - Email address
   - Password
   - Contact information
   - Credit card (for verification)

---

### 2. Configure IAM User

#### Access IAM Console
1. Log in to [AWS Management Console](https://console.aws.amazon.com/)
2. Search for "IAM" in the top search bar
3. Click on **IAM** under Services

#### Create New User
1. Under **Access management**, click **Users**
2. Click **Create user**
3. Enter a username (e.g., `tts-app-user`)
4. Click **Next**

#### Set Permissions
1. Under **Permission options**, select:
   - ☑ **Attach policies directly**
2. Search for `AmazonPollyFullAccess`
3. Check the policy box
4. Click **Next** → **Create user**

---

### 3. Get Security Credentials

1. In the **Users** list, click your new user
2. Go to **Security credentials** tab
3. Under **Access keys**, click **Create access key**
4. Select:
   - ☑ **Application running outside AWS**
5. Click **Next**
6. (Optional) Add description
7. Click **Create access key**

#### Save Credentials
1. Click **Download .csv file**
2. Store the .csv file securely which contains your:
   - `AWS Access key ID`
   - `AWS Secret access key`


## App Installation
1. Go to Releases then to the latest release
2. Click on the .zip file to download it
3. Double click on the zip file to open it
4. Double click on the TTSApp to open the app

## Usage
### 1. Enter AWS Credentials:
- Open the app
- In the "AWS Configuration" section, enter:
    - AWS Access Key ID (from your downloaded .csv)
    - AWS Secret Access Key (from your downloaded .csv)
    - AWS Region (default: `ap-southeast-1`)

### 2. Enter Text
Type or paste your text into the large text box.

### 3. Select Voice
Choose from available voices:
- Joanna (Female, English)
- Matthew (Male, English)
- Amy (Female, English)
- Brian (Male, English)

### 4. Generate Audio
Click "Generate Speech" to:
1. Convert text to speech using AWS Polly
2. Save as MP3 in your Downloads folder with filename format: tts_output_[VOICE]_[TIMESTAMP].mp3
3. The app will show the save path in the status message

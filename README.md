# Task1_HiringHood
# Text-to-Speech Web Application : 

A full-featured Text-to-Speech application using Amazon Polly that converts text to natural-sounding speech.

# Reason of using Amazon Polly
- I chose Amazon Polly for this project due to its high-quality, natural-sounding voices and extensive language support, which are critical for delivering a professional and accessible user experience. While open-source TTS solutions offer flexibility and cost-effectiveness, they often struggle to match Polly's level of voice clarity, prosody, and the sheer breadth of available languages and dialects. For applications requiring a polished, production-ready output, especially in multilingual contexts, Polly's advanced neural TTS models provide a significant advantage in terms of audio quality and user engagement.

## Features

- **Text-to-Speech Conversion**: Convert text to high-quality speech using Amazon's Polly service
- **Multiple Voice Options**: Choose from 12 different voices with various accents:
  - US English (Matthew, Joanna, Kevin, Kimberly, Salli, Joey)
  - UK English (Amy, Emma, Brian)
  - Australian English (Olivia)
  - Indian English (Kajal)
  - South African English (Ayanda)
- **Customization Options**:
  - Adjust speech rate (slow, medium, fast)
  - Control volume level (low, medium, high)
- **Text Validation**: Validate input text for special characters and length
- **Audio Controls**: Play, pause, and download generated audio
- **User-Friendly Interface**: Built with Streamlit for an intuitive user experience

## Prerequisites

- Python 3.7+
- AWS account with Amazon Polly access
- AWS credentials configured

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Johnwick-400/Task1_HiringHood.git
   cd Task1_HiringHood
   ```

2. Install required dependencies:
   ```
   pip install -r Requirements.txt
   ```

3. Configure AWS credentials:
   - Create an AWS IAM user with Amazon Polly access
   - Configure credentials using one of these methods:
     - AWS CLI: `aws configure`
     - Environment variables: 
       ```
       export AWS_ACCESS_KEY_ID=your_access_key
       export AWS_SECRET_ACCESS_KEY=your_secret_key
       export AWS_DEFAULT_REGION=us-east-1
       ```
     - Credentials file: `~/.aws/credentials`
## Demo Video

https://github.com/user-attachments/assets/5c3b77ed-a15f-4d76-9190-8771b19f3950

## Usage

1. Run the Streamlit application:
   ```
   streamlit run ttsamazon.py
   ```

2. Access the application in your web browser at `http://localhost:8501`

3. Enter your text, choose voice settings, and generate speech

4. Download the generated audio file or play it directly in your browser

## Application Workflow

1. Enter text in the input area
2. Click "Validate Text" to check for potential issues (optional)
3. Select voice, speech rate, and volume settings
4. Click "Generate Speech" to create the audio
5. Listen to the generated audio or download it as an MP3 file

### Adjusting Speech Parameters

Modify the `rate_values` and `volume_values` dictionaries in the `generate_speech` method to add more options.

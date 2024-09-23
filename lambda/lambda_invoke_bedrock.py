import base64
import json
import boto3
import logging
import os
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
sqs = boto3.client('sqs')
bedrock = boto3.client('bedrock-runtime', region_name='eu-central-1')

QUEUE_URL = os.environ['SQS_QUEUE_URL']
MODEL_ID = os.environ['BEDROCK_MODEL_ID']

def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        if not object_key.lower().endswith(('.png')):
            logger.info(f"Skipping non-image file: {object_key}")
            return

        image_data = s3.get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        prompt = generate_prompt()
        response = invoke_claude_3_multimodal(prompt, base64_image)
        
        # Parse the JSON response
        extracted_data = json.loads(response['content'][0]['text'])
        
        logger.info(f"Extracted data from image: {json.dumps(extracted_data, indent=2)}")

        if extracted_data:
            send_message_to_sqs(extracted_data)
            logger.info(f"Successfully processed image: {object_key}")
        else:
            logger.warning(f"No relevant data extracted from image: {object_key}")
        
    except KeyError as e:
        logger.error(f"Invalid event structure: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Bedrock response: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

def generate_prompt():
    return """
    Analyze the provided image of a medical bill receipt and extract the following information:
    
    1. Receipt Details:
       - Receipt Number
       - Receipt Date
       - Medical Institution Name
       - Practitioner Name
       - License Number
       - Full Address (including State, Zip Code, and City)
    
    2. Patient Information:
       - Patient Name
       - Patient Address (including City, State, and Zip Code)
    
    3. Official Receipt:
       - Total Price in Ringgit Malaysia (Text)
       - Total Price in RM (Number)       
       - Consultation
       - Cash Charger
    
    Instructions:
    - Extract the information as accurately as possible.
    - If a field is not present or unclear, leave it blank.
    - If the image is not a medical bill receipt, return an empty JSON object.
    - Ensure all currency values are in RM (Ringgit Malaysia).
    
    Return the extracted data in the following JSON format:
    {
        "receiptDetails": {
            "receiptNumber": "",
            "receiptDate": "",
            "medicalInstitution": "",
            "practitionerName": "",
            "licenseNumber": "",
            "address": "",
            "state": "",
            "zipCode": "",
            "city": ""
        },
        "patientInformation": {
            "patientName": "",
            "patientAddress": "",
            "patientCity": "",
            "patientState": "",
            "patientZipCode": ""
        },
        "officialReceipt": {
            "priceinRinggit": "",
            "priceinRM": "",
            "consultation": "",
            "cashcharger": "",

        },
    }
    """

def invoke_claude_3_multimodal(prompt, base64_image_data):
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image_data,
                        },
                    },
                ],
            }
        ],
    }

    try:
        response = bedrock.invoke_model(modelId=MODEL_ID, body=json.dumps(request_body))
        return json.loads(response['body'].read())
    except bedrock.exceptions.ClientError as err:
        logger.error(f"Bedrock ClientError: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
        raise
    except json.JSONDecodeError as err:
        logger.error(f"Failed to parse Bedrock response: {str(err)}")
        raise

def send_message_to_sqs(message_body):
    try:
        # Log the message body
        logger.info(f"Sending message to SQS. Message body: {json.dumps(message_body, indent=2)}")
        
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(message_body))
        logger.info("Message sent successfully to SQS")
    except sqs.exceptions.ClientError as e:
        logger.error(f"SQS ClientError: {e.response['Error']['Code']}: {e.response['Error']['Message']}")
        raise
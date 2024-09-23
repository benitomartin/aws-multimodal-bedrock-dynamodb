import json
import boto3
import logging
import os
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'invoices')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    if not event.get('Records'):
        logger.error("No records found in the event")
        return {'statusCode': 400, 'body': json.dumps('No records in the event')}

    for record in event['Records']:
        try:
            # Parse the SQS message
            message_body = json.loads(record['body'])
            
            data = message_body
            event_id = record['messageId']

            # Extract data from the parsed JSON
            receipt_details = data.get('receiptDetails', {})
            patient_information = data.get('patientInformation', {})
            official_receipt = data.get('officialReceipt', {})  # Changed from official_receipt

            # Prepare item for DynamoDB
            item = {
                'id': event_id,
                'receiptNumber': receipt_details.get('receiptNumber', ''),
                'receiptDate': receipt_details.get('receiptDate', ''),
                'medicalInstitution': receipt_details.get('medicalInstitution', ''),
                'practitionerName': receipt_details.get('practitionerName', ''),
                'licenseNumber': receipt_details.get('licenseNumber', ''),
                'address': receipt_details.get('address', ''),
                'state': receipt_details.get('state', ''),
                'zipCode': receipt_details.get('zipCode', ''),
                'city': receipt_details.get('city', ''),
                
                'patientName': patient_information.get('patientName', ''),
                'patientAddress': patient_information.get('patientAddress', ''),
                'patientCity': patient_information.get('patientCity', ''),
                'patientState': patient_information.get('patientState', ''),
                'patientZipCode': patient_information.get('patientZipCode', ''),
                
                'priceinRinggit': official_receipt.get('priceinRinggit', ''),
                'priceinRM': official_receipt.get('priceinRM', ''),
                'consultation': official_receipt.get('consultation', ''),
                'cashcharger': official_receipt.get('cashcharger', ''),
            }

            # # Remove any empty string values
            # item = {k: v for k, v in item.items() if v != ''}

            # Insert item into DynamoDB
            table.put_item(Item=item)
            logger.info(f"Successfully inserted item with Id: {event_id}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
        except ClientError as e:
            logger.error(f"DynamoDB ClientError: {e.response['Error']['Code']}: {e.response['Error']['Message']}")
        except KeyError as e:
            logger.error(f"Missing key in data structure: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

    return {'statusCode': 200, 'body': json.dumps('Processing complete')}
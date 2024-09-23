# Multimodal Bill Scan System with Claude Sonnet 3, AWS CDK, Bedrock, DynamoDB 🗽

<p align="center">
<img width="811" alt="bedrock-dynamo" src="https://github.com/user-attachments/assets/8e25a02e-653e-439a-a201-a0d41f75c6f5">
</p>

This repository contains a full multimodal application using AWS CDK as IaC, Claude 3 Sonnet as multimodal model, and DynamoDB as storage.

For detailed project descriptions, refer to this [Medium article](https://medium.com/@benitomartin/multimodal-bill-scan-system-with-claude-sonnet-3-aws-cdk-bedrock-dynamodb-0f6d0b6d46f2).

Main Steps

- **Data Ingestion**: Load data to an S3 Bucket
- **Model**: Claude 3 Sonnet in AWS Bedrock
- **Messaging**: AWS SQS
- **Storage**: AWS DynamoDB
- **Notifications**: AWS SNS
- **IaC**: AWS CDK
  
Feel free to ⭐ and clone this repo 😉

## Tech Stack

![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=for-the-badge&logo=anaconda&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)


## Project Structure

The project has been structured with the following files:

- `data:` sample scanned bill
- `app.py:` AWS CDK synthesizer
- `aws_multimodal_bedrock_dynamodb_stack:` script to create the constructs and stack
- `lambda:` lambda functions
- `requirements.txt:` project requirements

## Project Set Up

The Python version used for this project is Python 3.11. You can follow along the medium article.

1. Create an empty respository locally. This is necessary to initialize CDK. Afterwards you can copy the files from this repository.

2. Initialize AWS CDK to create the project structure:

   ```bash
   cdk init app --language python
   ```

3. Create the virtual environment named `main-env` using Conda with Python version 3.11:

   ```bash
   conda create -n main-env python=3.11
   conda activate main-env
   ```
   
4. Install the requirements.txt:

    ```bash
    pip install -r requirements.txt
    ```

5. Synthesize the app:

   ```bash
   cdk synth
   ```

6. Bootstrap the app to provision S3, and IAM roles:
   
   ```bash
   cdk bootstrap aws://{Account ID:}/{region}
    ```

7. Deploy the app on AWS CDK
 
    ```bash
    cdk deploy
    ```

8. Upload the scanned bill into the S3 Bucket and check that you receive a notification in your email (add your email in the aws_multimodal_bedrock_dynamodb_stack file before deployment)


9. Clean up

    ```bash
    cdk destroy
    ```

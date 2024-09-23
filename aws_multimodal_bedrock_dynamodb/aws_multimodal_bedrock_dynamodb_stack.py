from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,  
    aws_s3_notifications as s3n,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)

from aws_cdk.aws_lambda_event_sources import SqsEventSource, DynamoEventSource

class ImageProcessingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(
            self, "bedrock-multimodal-s3",
            bucket_name="bedrock-multimodal-s3", 
            removal_policy=RemovalPolicy.DESTROY,  
            auto_delete_objects=True  
        )

        # Create SQS queue
        queue = sqs.Queue(
            self, "bedrock-multimodal-sqs",
            queue_name="bedrock-multimodal-sqs",
            visibility_timeout=Duration.seconds(300) ,
            removal_policy=RemovalPolicy.DESTROY   
        )

        # Create DynamoDB table
        table = dynamodb.Table(
            self, "invoices",
            table_name="invoices",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            stream=dynamodb.StreamViewType.NEW_IMAGE  

        )

        # Create IAM role for Lambda functions
        lambda_role_bedrock = iam.Role(
            self, "invoke-bedrock-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Add necessary permissions to the Lambda role
        lambda_role_bedrock.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["arn:aws:bedrock:eu-central-1::foundation-model/*"]
        ))

        # Add inline policy to the Lambda role
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::bedrock-multimodal-s3/*"]
        ))
        
        # Add inline policy to the Lambda role
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["sqs:SendMessage"],
            resources=[f"arn:aws:sqs:{self.region}:{self.account}:bedrock-multimodal-sqs"]
        ))


        # Create Lambda function for image processing
        image_processor = lambda_.Function(
            self, "invoke-bedrock",
            function_name="invoke-bedrock",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_invoke_bedrock.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "SQS_QUEUE_URL": queue.queue_url,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0"
            },
            timeout=Duration.seconds(300),
            role=lambda_role_bedrock
        )
        
        # Create IAM role for Lambda functions
        lambda_role_sqs = iam.Role(
            self, "invoke-sqs-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Add necessary permissions to the Lambda role
        lambda_role_sqs.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        

        # Add specific permissions as per the provided policy
        lambda_role_sqs.add_to_policy(iam.PolicyStatement(
            sid="VisualEditor0",
            effect=iam.Effect.ALLOW,
            actions=["dynamodb:PutItem"],
            resources=[table.table_arn]
        ))
        
        # Add inline policy to the Lambda role
        lambda_role_sqs.add_to_policy(iam.PolicyStatement(
            sid="VisualEditor1",
            effect=iam.Effect.ALLOW,
            actions=[
                "sqs:DeleteMessage",
                "sqs:ReceiveMessage",
                "sqs:GetQueueAttributes"
            ],
            resources=[f"arn:aws:sqs:{self.region}:{self.account}:bedrock-multimodal-sqs"]
        ))

        
        # Create Lambda function for message processing
        message_processor = lambda_.Function(
            self, "insert-dynamodb",
            function_name="insert-dynamodb",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_insert_dynamodb.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(60),
            role=lambda_role_sqs
        )

        # Add S3 notification to trigger Lambda
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(image_processor),
            s3.NotificationKeyFilter(suffix=".png")
        )
        
        # Create SNS topic
        topic = sns.Topic(
            self, "InvoiceNotificationTopic",
            topic_name="invoice-notification-topic",
        )

        # Create a DynamoDB stream to SNS rule
        rule = DynamoEventSource(table, 
            starting_position=lambda_.StartingPosition.TRIM_HORIZON,
            batch_size=1,
            retry_attempts=10
        )

        # Create Lambda function to process DynamoDB stream and send SNS notification
        notification_processor = lambda_.Function(
            self, "notification-processor",
            function_name="notification-processor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_notification_processor.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "SNS_TOPIC_ARN": topic.topic_arn
            }
        )

        # Grant permissions to the Lambda function
        table.grant_stream_read(notification_processor)
        topic.grant_publish(notification_processor)

        # Add email subscription to the topic
        topic.add_subscription(sns_subscriptions.EmailSubscription("email@gmail.com"))

        # Add DynamoDB stream as event source for the notification processor Lambda
        notification_processor.add_event_source(rule)        

        # Add SQS as event source for message processor Lambda
        message_processor.add_event_source(SqsEventSource(queue))
        
        
      



import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_multimodal_bedrock_dynamodb.aws_multimodal_bedrock_dynamodb_stack import AwsMultimodalBedrockDynamodbStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_multimodal_bedrock_dynamodb/aws_multimodal_bedrock_dynamodb_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsMultimodalBedrockDynamodbStack(app, "aws-multimodal-bedrock-dynamodb")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

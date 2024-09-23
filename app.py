#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_multimodal_bedrock_dynamodb.aws_multimodal_bedrock_dynamodb_stack import ImageProcessingStack


app = cdk.App()
ImageProcessingStack(app, "ImageProcessingStack",
    )

app.synth()

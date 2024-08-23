# CloudConnexa Log Streaming to Cloudwatch logs

## Table of contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Script Logic](#script-logic)
* [Prerequisites](#prerequisites)
* [Setup](#setup)

## Introduction
Lambda function script that pulls files placed in an S3 bucket from CloudConnexa and places the logs into CloudWatch logs.

**Please note** that only new files placed in the S3 buckets after setting up the Lambda function will be transferred into CloudWatch. Any previously uploaded files in the S3 bucket will not be populated into CloudWatch.

## Technologies
Code:
- Python
  
AWS:
- CloudFormation
- CloudWatch
- IAM Roles
- Lambda
- S3

CloudConnexa:
- Log Streaming

## Script Logic
The Lambda function gets the file upon a trigger set in the S3 bucket. This file is compressed in a .gz file; the function decompresses it and gets the JSON line file content to push it to the defined CloudWatch Log Group.

## Prerequisites
- An IAM role with specific permissions must be attached to the Lambda function to send the logs to CloudWatch Logs. If you used the CloudFormation template, then you can skip this role creation:

1. Permissions:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::*",
            "Effect": "Allow"
        },
        {
            "Action": [
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": [
                "arn:aws:logs:*:{Account-ID}:*"
            ],
            "Effect": "Allow"
        }
    ]
}
```
Replace "**{Account-ID}**" with your AWS Account ID.

2. Trust Relationships:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
- You must set a trigger into the S3 Bucket where the CloudConnexa logs are being pushed. You can perform this operation directly from the Lambda Function console:

<img src="https://github.com/GabrielPalmar/CloudConnexa-Log-Streaming-to-CloudWatch/blob/main/S3-Trigger.png?raw=true" alt="S3 Trigger" width="700"/>

<img src="https://github.com/GabrielPalmar/CloudConnexa-Log-Streaming-to-CloudWatch/blob/main/S3-Trigger-2.png?raw=true" alt="S3 Trigger" width="700"/>

- Have configured the Log Streaming from CloudConnexa to an S3 bucket: https://openvpn.net/cloud-docs/tutorials/configuration-tutorials/log-streaming/tutorial--configure-aws-s3-bucket-for-cloudconnexa-log-streaming.html.

## Setup
You can copy the [Lambda script](/Lambda/Lambda-Function.py) or use the CloudFormation template to allocate the Lambda Function and required IAM roles:

[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=Lambda-Stack&templateURL=https://aws-cloudconnexa-resource-monitor.s3.us-east-2.amazonaws.com/CloudFormation-Template.yaml)

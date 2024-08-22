# CloudConnexa Log Streaming to Cloudwatch logs

## Table of contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Script Logic](#script-logic)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Usage](#usage)

## Introduction
Lambda function script that pulls files placed in an S3 bucket from CloudConnexa and places the logs into CloudWatch logs.
	
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
An IAM role with specific permissions must be attached to the Lambda function to send the logs to CloudWatch Logs.

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
You must set a trigger into the S3 Bucket where the CloudConnexa logs are being pushed. You can perform this operation directly from the Lambda Function console:

![](https://github.com/GabrielPalmar/CloudConnexa-Log-Streaming-to-CloudWatch/blob/main/S3-Trigger.png?raw=true)

![](https://github.com/GabrielPalmar/CloudConnexa-Log-Streaming-to-CloudWatch/blob/main/S3-Trigger-2.png)

## Setup
You can copy the Lambda script or use the CloudFormation template to allocate the Lambda Function and required IAM roles.

## Usage

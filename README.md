# CloudConnexa Log Streaming to Cloudwatch logs

## Table of contents
* [Introduction](#introduction)
* [Technologies](#technologies)
* [Script Logic](#script-logic)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Usage](#usage)
* [CloudFormation Templates](#cloudformation-templates)
* [Caveats](#caveats)

## Introduction
Lambda function script that pulls files placed in S3 bucket from CloudConnexa and places the logs into CloudWatch logs.
	
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
The Lambda function gets the file upon a trigger set in the S3 bucket. This file is compressed in a .gz file, the function follows on decopressing this file and get the JSON line file content to then push it to the defined CloudWatch Log Group.

## Prerequisites
To send the logs to CloudWatch Logs, an IAM role with specific permissions must be attached to the Lambda function.
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
                "arn:aws:logs:{Region-ID}:{Account-ID}:*"
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
You must set a trigger into the S3 Bucket where the CloudConnexa logs are being pushed.

## Setup
The stand-alone script is supported for Ubuntu 22.04. While it might work on other Ubuntu versions, most dependencies installations are optimized for this specific version.

To launch the script, use the following on the EC2's terminal:

```
wget -q raw.githubusercontent.com/GabrielPalmar/AWS-CloudConnexa-Resource-Monitor/main/Stand-alone%20Script/CC-Monitor-Script.sh
chmod +x CC-Monitor-Script.sh
sudo ./CC-Monitor-Script.sh
```

You can also consider using the [CloudFormation Template](#cloudformation-templates) to launch all the settings, including a new EC2.

## Usage

- An interactive mode is used when launching the script, requesting the following information:
1. **Interval (minutes) where the monitoring script repeats**: Dictates the interval in minutes for the cronjob to be repeated.
2. **How many times would the connection test be repeated against the resource IP or Domain?**: Test count for the MTR should be repeated. A higher value yields better average results but increases completion time.
3. **Threshold for the Latency value (ms) to monitor**: Threshold value for the latency tests to be compared. For example, if you choose 75, any report yielding higher latency than 75ms will trigger the flag.
4. **Threshold for the Loss value (%) to monitor**: Threshold value for the latency tests to be compared. For example, if you choose 5, any report yielding higher packet loss than 5% will trigger the flag.
5. **Resource IPs or Domains to monitor, comma separated [no space in between]**: Domains or IPs of the CloudConnexa resources you want to monitor, for example, "_privatedomain.com,192.168.1.15,10.10.1.10_'.

NOTE: If this script is placed in a fresh EC2, it will ask for a [Host Token](https://openvpn.net/cloud-docs/owner/tutorials/configuration-tutorials/connectors/operating-systems.html#tutorial--install-a-connector-on-linux) to install the CloudConnexa session.

- Once the script is installed, you can manually edit the values over the script file:
```
/home/ubuntu/connexa-script.sh
```

- Also, you can edit the cronjob interval or remove the job by using the following command:
```
crontab -e
```

- Remember to set up the CloudWatch alarm and configure the required SNS topic to receive alerts when a flag is triggered: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Alarm-On-Logs.html.

## CloudFormation Templates
1. Template to launch the Monitor script, including EC2, IAM roles, and CloudWatch [configuration](#dios):
   
[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=CC-Resource-Monitor&templateURL=https://aws-cloudconnexa-resource-monitor.s3.us-east-2.amazonaws.com/CF-CC-Monitor-Template.yaml)

2. Template to create the CloudWatch Log Group and Filter:
   
[![Launch Stack](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=CC-CloudWatch&templateURL=https://aws-cloudconnexa-resource-monitor.s3.us-east-2.amazonaws.com/CF-CC-CloudWatch-Template.yaml)

## Caveats
The monitoring script depends on the MTR application. While creating it, I discovered a bug in the report mode used to review the hops. I have submitted a bug request. You can follow this request by using this link: https://bugs.launchpad.net/ubuntu/+source/mtr/+bug/2070685. 

Based on this, a PING test checks the latency and packet loss to the destination as failover to ensure the script works properly.

import json
import boto3
import os
import jmespath
from datetime import datetime

client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    pass_on = True
    time_difference = ""
    response = client.list_executions(
        stateMachineArn= os.environ['StateMachineARN'],
        statusFilter='RUNNING',
        maxResults=123,
    )
    for execution in response['executions']:
        payload = describe_execution(execution['executionArn'])
        if payload['full_url'] == event['full_url'] and payload['current_state'] == 'DOWN':
            stop_execution(execution['executionArn'])
            time_difference = time_difference_check(event, payload)
            pass_on = False
        else:
            pass
    return {
        "check_name": event['check_name'],
        "check_type": event['check_type'],
        "state_changed_timestamp": event['state_changed_timestamp'],
        "state_changed_utc_time": event['state_changed_utc_time'],
        "long_description": event['long_description'],
        "current_state": event['current_state'],
        "full_url":event['full_url'],
        "pass_on": pass_on,
        "time_difference": time_difference,
        "tag": event['tag'],
    }
    
def describe_execution(execution_arn):
    response = client.describe_execution(
        executionArn=execution_arn
    )
    payload = json.loads(response['input'])
    return payload

def stop_execution(execution_arn):
    response = client.stop_execution(
        executionArn=execution_arn
    )

def time_difference_check(event, payload):
    # convert time string to datetime
    t1 = payload['state_changed_utc_time']
    t1 = t1.replace("T", " ")
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    t2 = event['state_changed_utc_time']
    t2 = t2.replace("T", " ")
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    delta = t2 - t1
    time_difference = f"The site was down for {delta.total_seconds()} seconds"
    return time_difference

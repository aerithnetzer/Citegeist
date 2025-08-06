import boto3
import os


def lambda_handler(event, context):
    amplify = boto3.client("amplify")

    app_id = os.environ.get("AMPLIFY_APP_ID")
    branch_name = os.environ.get("AMPLIFY_BRANCH_NAME")

    response = amplify.start_job(
        appId=app_id,
        branchName=branch_name,
        jobType="RELEASE",
    )
    return {
        "statusCode": 200,
        "body": f"Triggered redeploy: {response['jobSummary']['jobId']}",
    }


if __name__ == "__main__":
    lambda_handler({}, {})

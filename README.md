# serverless

Lambda function to send an email with a verification link to user before creating his account

Flow:
User sends post request to create account
-> In post API a message is send to an SNS topic in AWS
-> The SNS topic, triggers the lambda function
-> The Lambda function sends an email with a verification link
-> User clicks link to complete registration
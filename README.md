<span style="color:red">
This is a test repository, use at your own risks.

Requirements:
python 3.10
</span>

## Required Lambda Parameters
- `aws_region`
- `kendra_index_id`
- `model_id`
- `prompt`
- `question`

### Increase Lambda Timeout
1. Navigate to the Lambda function configuration.
2. Click on "General Configuration".
3. Click on "Edit".
4. Increase the timeout value. 10 seconds seems to work, but it should be tested.

### Grant Lambda Permissions
**For testing purposes only, this should be restricted to the minimum required permissions.**

In the Lambda execution role, grant the following permissions:
- `AmazonBedrockFullAccess`
- `AmazonKendraFullAccess`

***If the Lambda function needs to access Kendra in another account:***
1. Add the following policy into the destination account:
```json
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": "arn:aws:iam::222222222222:role/role-on-source-account"
    }
}
```

2. Modify your cross-account IAM role's trust policy to allow your Lambda function to assume the role
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111111111111:role/my-lambda-execution-role"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
3) Add an environment variable key ***KENDRA_ROLE_ARN*** with the destination role ARN as value

### Create lambda layers

1. Set Up Your Environment

    Create a virtual environment:
    
    ```
    python3.10 -m venv lambda-layer-env
    source lambda-layer-env/bin/activate
    ```
    
    Install the necessary packages:
    ```
    pip install langchain langchain-aws langchain-community
    ```
    
2. Create the Lambda Layers
    
    Layer 1: langchain Dependencies
    
    Create the directory structure:
    ```
    mkdir -p langchain-layer/python/lib/python3.10/site-packages
    ```
    
    Copy the langchain package and its dependencies:
    ```
    pip install --target langchain-layer/python/lib/python3.10/site-packages langchain
    ```
    
    Zip the layer:
    ```
    cd langchain-layer
    zip -r9 ../langchain-layer.zip .
    cd ..
    ```
    
    Layer 2: langchain-aws Dependencies
    
    Create the directory structure:
    ```
    mkdir -p langchain-aws-layer/python/lib/python3.10/site-packages
    ```
    
    Copy the langchain-aws package and its dependencies:
    ```
    pip install --target langchain-aws-layer/python/lib/python3.10/site-packages langchain-aws
    ```
    
    Zip the layer:
    ```
    cd langchain-aws-layer
    zip -r9 ../langchain-aws-layer.zip .
    cd ..
    ```
    
    Layer 3: langchain-community Dependencies
    
    Create the directory structure:
    ```
    mkdir -p langchain-community-layer/python/lib/python3.10/site-packages
    ```
    
    Copy the langchain-community package and its dependencies:
    ```
    pip install --target langchain-community-layer/python/lib/python3.10/site-packages langchain-community
    ```
    
    Zip the layer:
    ```
    cd langchain-community-layer
    zip -r9 ../langchain-community-layer.zip .
    cd ..
    ```

3. Upload Layers to AWS Lambda

    * Go to the AWS Lambda Console.
    * Navigate to the Layers section.
    * Create a new layer for each zip file:
        * Upload langchain-layer.zip.
        * Upload langchain-aws-layer.zip.
        * Upload langchain-community-layer.zip. (not used for now so you can skip)
    
    Step 5: Attach Layers to Your Lambda Function
    * Navigate to your Lambda function.
    * In the Function configuration, add the layers:
        * Add langchain-layer.
        * Add langchain-community-layer.
        * Add langchain-aws-layer. (not used for now so you can skip)
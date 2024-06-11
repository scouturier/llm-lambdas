import os
import boto3
from botocore.config import Config
from langchain.chains import ConversationalRetrievalChain
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_community.chat_models import BedrockChat

class CustomConversationalRetrievalChain(ConversationalRetrievalChain):
    @property
    def output_keys(self):
        return ["result"]

    def _call(self, inputs):
        result = super()._call(inputs)
        return {"result": f"{result['answer']}\nSources: {', '.join([doc.metadata['source'] for doc in result['source_documents']])}"}

def lambda_handler(event, context):
    # Get the required parameters from the event
    aws_region = event['aws_region']
    kendra_index_id = event['kendra_index_id']
    model_id = event['model_id']
    prompt = event['prompt']
    question = event['question']
    chat_history = event.get('chat_history', [])

    # Role ARN of the role to assume in the other account
    role_arn = os.environ['KENDRA_ROLE_ARN']

    # Assume the role
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='KendraAccessSession'
    )

    # Extract the temporary credentials
    credentials = assumed_role['Credentials']
    kendra_client = boto3.client(
        'kendra',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=aws_region
    )

    # Create the Amazon Kendra retriever using the temporary credentials
    retriever = AmazonKendraRetriever(
        index_id=kendra_index_id,
        top_k=5,
        client=kendra_client
    )

    # Configure the Bedrock client with timeouts and retries
    bedrock_config = Config(
        connect_timeout=120,
        read_timeout=120,
        retries={'max_attempts': 0}
    )
    bedrock_client = boto3.client('bedrock-runtime', config=bedrock_config, region_name=aws_region)

    # Create the Bedrock LLM
    credentials_profile_name = os.environ.get("AWS_PROFILE", "")
    llm = BedrockChat(
        credentials_profile_name=credentials_profile_name,
        model_id=model_id,
        client=bedrock_client,
        model_kwargs={
            "max_tokens": 2048,
            "temperature": 1,
            "top_k": 250,
            "top_p": 0.999,
            "stop_sequences": ["\n\nHuman"],
        }
    )

    # Create the Conversational Retrieval Chain
    qa = CustomConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )

    # Run the chain with the input prompt
    result = qa({"question": question, "prompt": prompt, "chat_history": chat_history})

    return {
        'statusCode': 200,
        'body': {
            'result': result['result']
        }
    }
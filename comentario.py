import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Obtener variables de entorno
    table_name = os.environ['TABLE_NAME']
    bucket_name = os.environ['BUCKET_NAME']
    table = dynamodb.Table(table_name)

    # Parsear cuerpo JSON recibido por POST
    body = json.loads(event['body'])
    tenant_id = body.get('tenant_id')
    comentario = body.get('comentario')

    # Generar UUID y timestamp
    uuid_val = str(uuid.uuid1())
    timestamp = datetime.utcnow().isoformat()

    # Guardar en DynamoDB
    item = {
        'tenant_id': tenant_id,
        'uuid': uuid_val,
        'comentario': comentario,
        'fecha': timestamp
    }
    table.put_item(Item=item)

    # Guardar también en S3 como archivo JSON
    s3_key = f"{tenant_id}/{uuid_val}.json"
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(item),
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'mensaje': f'Comentario guardado y subido a {bucket_name}/{s3_key}',
            'uuid': uuid_val
        })
    }

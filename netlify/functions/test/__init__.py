import json

def handler(event, context):
    print("TEST FUNCTION CALLED")
    print(f"Event: {json.dumps(event, default=str)}")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Test function works!',
            'event': event
        })
    }


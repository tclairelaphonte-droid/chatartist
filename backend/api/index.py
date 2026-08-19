from http import HTTPStatus

def handler(request):
    path = request.path or "/"

    if path == "/":
        return {
            "statusCode": HTTPStatus.OK,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": '{"status":"OK","message":"ArtistChat backend fonctionne"}',
        }

    if path == "/health":
        return {
            "statusCode": HTTPStatus.OK,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": '{"status":"healthy"}',
        }

    return {
        "statusCode": HTTPStatus.NOT_FOUND,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": '{"error":"Not found"}',
    }
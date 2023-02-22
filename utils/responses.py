from rest_framework import status
from rest_framework.response import Response

def success_response(data):
    return Response(data, status=status.HTTP_200_OK)

def created_response(data):
    return Response(data, status=status.HTTP_201_CREATED)

def not_content(data):
    return Response(data, status=status.HTTP_204_NO_CONTENT)

def bad_request(data):
    return Response(data, status=status.HTTP_400_BAD_REQUEST)

def unauthorized_response(data):
    return Response(data, status=status.HTTP_401_UNAUTHORIZED)

def forbidden_response(data):
    return Response(data, status=status.HTTP_403_FORBIDDEN)

def not_found(data):
    return Response(data, status=status.HTTP_404_NOT_FOUND)

def conflict_response(data):
    return Response(data, status=status.HTTP_409_CONFLICT)

def expectation_failed(data):
    return Response(data, status=status.HTTP_417_EXPECTATION_FAILED)

def server_error(data):
    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def not_suported_response(data):
    return Response(data, status=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED)
import json
import requests
import jwt
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
from rest_framework import authentication, exceptions
from pac.settings.settings import AZURE_TENANT_ID
import requests
import logging

logging.getLogger().setLevel(logging.INFO)
from core.models import Persona, User
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

def get_access_from_secret (client_id, client_secret):
    if client_id is None or client_secret is None:
        return None
    # send the authentication request to Azure to get a token
    try:
        payload=f'grant_type=client_credentials&client_id={client_id}&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret={client_secret}'
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        auth_response = requests.get(f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token',
            headers=headers, data=payload, timeout=2) # 2 second timeout
        if auth_response.content is not None:
            content_json = json.loads(auth_response.content.decode('utf8'))
            token_str = content_json.get('access_token', '')
            return token_str
        else:
            return None
    except Exception as rest_errors:
        raise exceptions.AuthenticationFailed(
            {"status": "Failure", "message": "App Client is not authorized to use this service."})

def get_app_as_user(token_str):
    alg = jwt.get_unverified_header(token_str)['alg']
    decodedAccessToken = jwt.decode(token_str, algorithms=[alg], options={"verify_signature": False})
    app_name = decodedAccessToken.get('app_displayname')
    app_id = decodedAccessToken.get('appid')
    # lookup entries in dbo.User that match on app_id and pull an effective user for SalesForce from there
    return User.objects.filter(azure_id=app_id).first()

class AzureActiveDirectoryAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token_str = request.META.get('HTTP_X_CSRFTOKEN', '')
        flow_type = request.META.get('HTTP_FLOW_TYPE', '')
        if flow_type == 'access-token':
            # from an app access token, check if the external app is authorized to make requests
            user = get_app_as_user(token_str)
            if not user:
                return None
            return (user, {'access_token': token_str})
        elif flow_type == 'client-secret':
            req_client_id = request.META.get('HTTP_CLIENT_ID')
            req_client_secret = request.META.get('HTTP_CLIENT_SECRET')
            token_str = get_access_from_secret(req_client_id, req_client_secret)
            if token_str is None:
                return None
            user = get_app_as_user(token_str)
            if user is None:
                return None
            request.META['HTTP_X_CSRFTOKEN'] = token_str
            return (user, {'access_token': token_str})
        else:
            if not token_str:
                raise exceptions.AuthenticationFailed({"status": "Failure", "message": "No authorization token provided."})
            # regular REST requests will include user information from the Azure AD profile
            user_dict = self.get_user({'access_token': token_str})
            if not user_dict or "userPrincipalName" not in user_dict:
                # Uncomment below line for swagger to work
                # if not user_dict:
                raise exceptions.AuthenticationFailed(
                    {"status": "Failure", "message": "Invalid token."})
            user = User.objects.filter(
                user_email=user_dict.get("userPrincipalName")).first()
            if not user:
                try:
                    # Uncomment below line for swagger to work
                    # user = get_user_model().objects.first()
                    user = self.create_user(user_dict)
                except Exception as e:
                    raise exceptions.AuthenticationFailed(
                        {"status": "Failure", "message": "User doesn't exist and can't create user.",
                         "error": f'{type(e).__name__} {e.args}'})

            user.user_name = user_dict.get("userPrincipalName")  # also include user's name for auditing purposes
            if False in [user.is_active, user.azure_is_active]:
                raise exceptions.AuthenticationFailed(
                    {"status": "Failure", "message": "User is unlicensed."})
            return (user, {'access_token': token_str})

    def get_user(self, token):
        graph_client = OAuth2Session(token=token)
        graph_url = 'https://graph.microsoft.com/v1.0'
        user = graph_client.get(f'{graph_url}/me')
        return user.json()

    def create_user(self, user_dict):
        # TODO: partner users from other domains will also have to be allowed in so this restriction might be removed
        if not any(email in user_dict["userPrincipalName"] for email in
                   ["@dayandrossinc.ca", "@mccain.ca", "@dayross.com", "@sameday.ca"]):
            raise Exception
        user_kwargs = {"user_name": user_dict["displayName"], "user_email": user_dict["userPrincipalName"],
                       "azure_id": user_dict["id"],
                       "persona": Persona.objects.get_or_create(persona_name="Pricing Manager")[0]}
        user = User(**user_kwargs)
        user.save()
        return user

class BackendAuthentication(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        # Swagger authentication can now work with the client_id/client_secret credentials
        token_str = get_access_from_secret(username, password)
        if token_str is None:
            return None
        user = get_app_as_user(token_str)
        if user is None:
            return None
        return user

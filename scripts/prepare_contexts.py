#!/usr/bin/env python3
import sys
import toml
import json
import requests

# Strip white spaces from data
def strip_spaces(obj):
  result = obj
  if type==None:
    result = 'No value found.'
  else:
    str(result).strip()
  return result

#Get data from toml file
creds = toml.load('credentials.toml').get('keys')
CIRCLE_TOKEN = strip_spaces(creds.get('circleci_token'))
CIRCLECI_ORG_SLUG = strip_spaces(creds.get('circleci_org_slug'))
CIRCLECI_VCS_USER = CIRCLECI_ORG_SLUG.rsplit('/',1)[1]  #Get the users vcs name from the slug
CIRCLECI_ORG_ID = strip_spaces(creds.get('circleci_org_id'))
CIRCLECI_BASE_URL = strip_spaces('http://circleci.com/api/v2/')
CIRCLECI_CONTEXT_NAME_PREFIX = strip_spaces('CICD_WORKSHOP_')

SNYK_TOKEN = strip_spaces(creds.get('snyk_token'))
DOCKER_LOGIN = strip_spaces(creds.get('docker_login'))
DOCKER_TOKEN = strip_spaces(creds.get('docker_token'))
TF_CLOUD_TOKEN = strip_spaces(creds.get('tf_cloud_token'))
TF_CLOUD_ORG_EMAIL = strip_spaces(creds.get('tf_cloud_org_email'))
TF_CLOUD_ORG_NAME = strip_spaces(creds.get('tf_cloud_org_name'))
TF_CLOUD_ORGANIZATION = TF_CLOUD_ORG_NAME + CIRCLECI_VCS_USER   # Create a unique Org Name for TF Cloud
TF_CLOUD_WORKSPACE = strip_spaces(creds.get('tf_cloud_workspace'))
DIGITALOCEAN_TOKEN = strip_spaces(creds.get('digitalocean_token'))

REQUEST_HEADER = {
    'content-type': "application/json",
    'Circle-Token': CIRCLE_TOKEN
  }

def get_circleci_api_request(endpoint, payload_dict):
  try:
    resp = requests.get(CIRCLECI_BASE_URL + endpoint, headers=REQUEST_HEADER)
    resp.raise_for_status()
    return resp.json()   
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
  except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)

def post_circleci_api_request(endpoint, payload_dict):
  try:
    resp = requests.post(CIRCLECI_BASE_URL + endpoint, headers=REQUEST_HEADER,json=payload_dict)
    resp.raise_for_status()
    return resp.json()
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
  except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)

def put_circleci_api_request(endpoint, payload_dict):
  try:
    resp = requests.put(CIRCLECI_BASE_URL + endpoint, headers=REQUEST_HEADER,json=payload_dict)
    resp.raise_for_status()
    return resp.json()    
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
  except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)

def delete_circleci_api_request(endpoint, context_id):
  try:
    resp = requests.delete(CIRCLECI_BASE_URL + endpoint + context_id, headers=REQUEST_HEADER)
    resp.raise_for_status()
    return resp.json()   
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
  except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
  except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)

def add_circle_token_to_context_with_name(context_name, env_var_name, env_var_value):
    context_id = find_or_create_context_by_name(context_name)
    add_circle_token_to_context(context_id=context_id, env_var_name=env_var_name, env_var_value=env_var_value)
    
    #Mask the secret values 
    masked_env_value = env_var_value[-4:] if len(env_var_value) > 4 else "***********"
    context = {
                'Context Name':CIRCLECI_CONTEXT_NAME_PREFIX + context_name,
                'Environment Variable': env_var_name, 
                'Environment Value' : f'****{masked_env_value}'
              }
    return context

def add_circle_token_to_context(context_id, env_var_name, env_var_value):
  resp = put_circleci_api_request(f'context/{context_id}/environment-variable/{env_var_name}', { "value": env_var_value })
  return resp

# Get the context id to which we'll store env vars
def find_or_create_context_by_name(context_name):   # context name - CICD_WORKSHOP_docker etc...
  full_context_name = CIRCLECI_CONTEXT_NAME_PREFIX + context_name
  contexts = get_circleci_api_request(f'context?owner-id={CIRCLECI_ORG_ID}&owner-type=organization', None).get('items')
  context = next((ctx for ctx in contexts if ctx.get('name') == full_context_name), None)
  # print(f'Full Context Name: {context}')
  if context == None:
  # Context doesn't exist so we create it   
    context_payload = {
      "name": full_context_name,
        "owner": {
          "id": CIRCLECI_ORG_ID,
          "type": "organization"
        }
    }
    context = post_circleci_api_request('context', context_payload) 
  circleci_context_id = context.get('id')
  return circleci_context_id

# Add Env vars to context
print(add_circle_token_to_context_with_name('SNYK', 'SNYK_TOKEN', SNYK_TOKEN))
print(add_circle_token_to_context_with_name('DOCKER', 'DOCKER_LOGIN', DOCKER_LOGIN))
print(add_circle_token_to_context_with_name('DIGITAL_OCEAN', 'DIGITALOCEAN_TOKEN', DIGITALOCEAN_TOKEN))
print(add_circle_token_to_context_with_name('DOCKER', 'DOCKER_PASSWORD', DOCKER_TOKEN))
print(add_circle_token_to_context_with_name('TERRAFORM_CLOUD', 'TF_CLOUD_TOKEN', TF_CLOUD_TOKEN))
print(add_circle_token_to_context_with_name('TERRAFORM_CLOUD', 'TF_CLOUD_ORG_EMAIL', TF_CLOUD_ORG_EMAIL))
print(add_circle_token_to_context_with_name('TERRAFORM_CLOUD', 'TF_CLOUD_ORGANIZATION', TF_CLOUD_ORGANIZATION)
print(add_circle_token_to_context_with_name('TERRAFORM_CLOUD', 'TF_CLOUD_WORKSPACE', TF_CLOUD_WORKSPACE))


# # Warning uncommenting the code block below will delete all the contexts created above
# # To delete the values from CircleCI contexts uncomment the lines below
#
# def delete_contexts():
#   context_ids = get_circleci_api_request(F'context?owner-id={CIRCLECI_ORG_ID}&owner-type=organization', None).get('items')
#   for ctx in context_ids:
#     if ctx == None:
#       #Do nothing
#       print('-----\n')
#     else:
#       #delete the context
#       message = delete_circleci_api_request(f'context/', ctx.get('id')).get('message')
#       print(f"Context ID: {ctx.get('id')} Name: {ctx.get('name')} {message}") 
#
# # execute the delete context call
# delete_contexts()
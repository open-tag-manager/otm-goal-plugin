from chalice import Blueprint, Response
from botocore.errorfactory import ClientError
from chalicelib import authorizer, s3, s3_client, has_role, get_config_data, get_container_data
import os
import json
import uuid

plugin_app = Blueprint(__name__)


@plugin_app.route('/', methods=['GET'], cors=True, authorizer=authorizer)
def get_container_goals(org, name):
    app = plugin_app._current_app

    if not has_role(app, org, 'read'):
        return Response(body={'error': 'permission error'}, status_code=401)

    config = get_config_data(org)
    (data, container) = get_container_data(org, name, config)

    if data is None:
        return Response(body={'error': 'not found'}, status_code=404)

    bucket = os.environ.get('OTM_STATS_BUCKET')
    file = (os.environ.get('OTM_STATS_PREFIX') or '') + 'goals.json'
    object = s3.Object(bucket, file)
    try:
        response = object.get()
        data = json.loads(response['Body'].read())
        result = list(filter(lambda x: x['org'] == org and x['container'] == name, data))

        for r in result:
            prefix = (os.environ.get('OTM_STATS_PREFIX') or '')
            org = r['org']
            if not org == 'root':
                prefix += org + '/'

            r['result_url'] = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket, 'Key': prefix + r['container'] + '_' + r['id'] + '_goal_result.json'},
                ExpiresIn=3600,
                HttpMethod='GET'
            )

        return result
    except ClientError:
        return Response(body=[], status_code=200)


@plugin_app.route('/', methods=['POST'], cors=True, authorizer=authorizer)
def create_container_goals(org, name):
    app = plugin_app._current_app

    if not has_role(app, org, 'read'):
        return Response(body={'error': 'permission error'}, status_code=401)

    config = get_config_data(org)
    (data, container) = get_container_data(org, name, config)

    if data is None:
        return Response(body={'error': 'not found'}, status_code=404)

    bucket = os.environ.get('OTM_STATS_BUCKET')
    file = (os.environ.get('OTM_STATS_PREFIX') or '') + 'goals.json'
    object = s3.Object(bucket, file)

    request = app.current_request
    body = request.json_body
    if not 'name' in body or not 'target' in body:
        return Response(body={'error': 'name or target is required'}, status_code=400)

    try:
        response = object.get()
        data = json.loads(response['Body'].read())
    except ClientError:
        data = []

    target_match = 'eq'
    if 'target_match' in body:
        target_match = body['target_match']

    path = None
    if 'path' in body:
        path = body['path']

    path_match = 'eq'
    if 'path_match' in body:
        path_match = body['path_match']

    goal = {
        'id': str(uuid.uuid4()),
        'name': body['name'],
        'org': org,
        'container': name,
        'target': body['target'],
        'target_match': target_match,
        'path': path,
        'path_match': path_match
    }
    data.append(goal)

    s3.Object(bucket, file).put(Body=json.dumps(data), ContentType='application/json')

    return goal


@plugin_app.route('/{goal}', methods=['DELETE'], cors=True, authorizer=authorizer)
def delete_container_goals(org, name, goal):
    app = plugin_app._current_app

    if not has_role(app, org, 'write'):
        return Response(body={'error': 'permission error'}, status_code=401)

    config = get_config_data(org)
    (data, container) = get_container_data(org, name, config)

    if data is None:
        return Response(body={'error': 'not found'}, status_code=404)

    o_prefix = ''
    if org != 'root':
        o_prefix = org + '/'

    bucket = os.environ.get('OTM_STATS_BUCKET')
    file = (os.environ.get('OTM_STATS_PREFIX') or '') + 'goals.json'
    object = s3.Object(bucket, file)
    try:
        response = object.get()
        data = json.loads(response['Body'].read())
        c = list(filter(lambda x: x['id'] == goal and x['org'] == org and x['container'] == name, data))
        if len(c) > 0:
            data.remove(c[0])
            s3.Object(bucket, file).put(Body=json.dumps(data), ContentType='application/json')
            return Response(body='', status_code=204)
        else:
            return Response(body={'error': 'not found'}, status_code=404)
    except ClientError:
        return Response(body={'error': 'not found'}, status_code=404)

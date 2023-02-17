import boto3
import json
from botocore.exceptions import ClientError

def get_ec2_list(ec2_client):
    
    #check how to get all instances in all regions
    instance_iterator = ec2_client.instances.all()
    running_ec2_list = []
    for inst in instance_iterator:
            print (inst.id + ', ' + inst.state['Name'])
            if inst.state['Name'] == 'running':
                running_ec2_list.append(inst.id)
    return running_ec2_list

def terminate_ec2_instance(ec2_client, ec2_list):
        response = ec2_client.terminate_instances(InstanceIds=ec2_list)
        print(response)
    

def delete_nat_gateways(nat_gateways, region):
    
    client = boto3.client('ec2', region_name=region)
    for nat_gw in nat_gateways: 
        try:
            response = client.delete_nat_gateway(NatGatewayId=nat_gw['NatGatewayId'])
            for allocation in nat_gw['NatGatewayAddresses']:
                a_id = allocation['AllocationId']
                client.release_address(AllocationId=a_id)
                print(f'AllocationId: {a_id} was released successfully in region {region}.')
        except ClientError as ex:
            print(ex)
            print('Could not delete the NAT Gateway.')
            raise
        else:
            nat_gw_id = nat_gw['NatGatewayId']
            print(f'NAT Gateway {nat_gw_id} is deleted successfully in region {region}.')


def describe_nat_gateways(max_items, region):
    client = boto3.client('ec2', region_name=region)
    try:
        # creating paginator object for describe_nat_gateways() method
        paginator = client.get_paginator('describe_nat_gateways')
        # creating a PageIterator from the paginator
        response_iterator = paginator.paginate(
            PaginationConfig={'MaxItems': max_items})
        full_result = response_iterator.build_full_result()
        
        nat_gateways_list = []
        for page in full_result['NatGateways']:
            nat_gateways_list.append(page)
    except ClientError:
        print('Could not describe NAT Gateways.')
        raise
    else:
        if len(nat_gateways_list) > 0:
            return nat_gateways_list
        else:
            print(f'there are no NAT Gateways defined in region {region}')


####
regions = [r['RegionName'] for r in boto3.client('ec2').describe_regions()['Regions']]


for region in regions:
    ec2_client = boto3.resource('ec2', region_name=region)
    ec2_list = get_ec2_list(ec2_client) 
    if len(ec2_list) > 0:
        print('Running EC2 Machines in region {region}:')
        print(ec2_list)
        terminate_ec2_instance(ec2_client, ec2_list)
    else:
        print (f'No EC2 instances are running in region {region}')

MAX_ITEMS = 100
for region in regions:
    nat_gateways = describe_nat_gateways(MAX_ITEMS, region)
    if nat_gateways is not None and len(nat_gateways) > 0:
            delete_nat_gateways(nat_gateways, region)

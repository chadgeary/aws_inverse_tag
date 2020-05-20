import boto3
from botocore.config import Config

# Attempts
config = Config(
  retries = dict(
    max_attempts = 3
  )
)

# Tag(s)
my_tags = [
  {
    "Key": "backup",
    "Value": "true"
  }
]

# Owner ID Filter
owner_id = 'SOME_OWNER_ID'

def lambda_handler(event, context):

  # Connection
  ec2 = boto3.client("ec2", config=config)

  # Instances
  def tag_instances():
    # All Reservations [instances] (tagged or untagged)
    all_reservations = ec2.describe_instances(Filters = [{'Name': 'owner-id', 'Values':[owner_id]}])

    # Append each InstanceId in all_reservations to all_instances
    all_instances = []
    for all_reservation in all_reservations['Reservations']:
      for all_instance in all_reservation['Instances']:
        all_instances.append(all_instance['InstanceId'])

    # Append each InstanceId with backup:true to tagged_instances
    tagged_reservations = ec2.describe_instances(Filters = [{'Name': 'owner-id', 'Values':[owner_id]},{'Name': 'tag:backup', 'Values':['true','false']}])
    tagged_instances = []
    for tagged_reservation in tagged_reservations['Reservations']:
      for tagged_instance in tagged_reservation['Instances']:
        tagged_instances.append(tagged_instance['InstanceId'])

    # Append each InstanceId in all_instances and not in tagged_instances to untagged_instances
    untagged_instances = [all_instance for all_instance in all_instances if all_instance not in tagged_instances]

    # Print untagged InstanceId
    print("untagged_instanceids:",untagged_instances)

    # Tag untagged instances
    if untagged_instances:
      ec2.create_tags(
        Resources = untagged_instances,
        Tags = my_tags
      )

  # Perform tagging
  try:
    tag_instances()
  except botocore.exceptions.ClientError:
    print("Something went wrong.")

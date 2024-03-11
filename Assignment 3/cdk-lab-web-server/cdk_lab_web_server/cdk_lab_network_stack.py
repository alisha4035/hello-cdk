import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
    # aws_sqs as sqs,
)

from constructs import Construct

class CdkLabNetworkStack(Stack):

    @property
    def vpc(self):
        return self.cdk_lab_vpc
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        publicSubnet1 = ec2.SubnetConfiguration(name="PublicSubnet01",subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24)
        privateSubnet1 = ec2.SubnetConfiguration(name="PrivateSubnet01",subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, cidr_mask=28)

        publicSubnet2 = ec2.SubnetConfiguration(name="PublicSubnet02",subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24)
        privateSubnet2 = ec2.SubnetConfiguration(name="PrivateSubnet02",subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, cidr_mask=28)


        # Create a VPC. CDK by default creates and attaches internet gateway for VPC
        # The VPC CIDR will be evenly divided between 2 public and 2 private subnet per AZ.
        self.cdk_lab_vpc = ec2.Vpc(self, "cdk_lab_vpc", 
                            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                            max_azs=2,
                            subnet_configuration=[publicSubnet1, publicSubnet2, privateSubnet1, privateSubnet2]
        )
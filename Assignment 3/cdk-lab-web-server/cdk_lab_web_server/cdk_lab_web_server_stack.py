import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
    aws_sqs as sqs,
)

from constructs import Construct

dirname = os.path.dirname(__file__)
        
class CdkLabWebServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cdk_lab_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        

        # The code that defines your stack goes here

        # Instance Role and SSM Managed Policy
        InstanceRole = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        InstanceRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
       
        
        # Web Server Security Group
        
        cdk_lab_web_server_sg = ec2.SecurityGroup(self, "Web_Server_SG",
                                                  vpc=cdk_lab_vpc,
                                                  allow_all_outbound=True,
                                                  description="Allow inbound HTTP traffic")
                                                 
            
        #Allow inbound HTTP traffic on port 80 to the Web Server Security Group
        
        cdk_lab_web_server_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(),
                                              connection = ec2.Port.tcp(80), 
                                              description="Allow inbound HTTP traffic")
        
        # RDS instances security group
        
        rds_lab_web_server_sg = ec2.SecurityGroup(self, "RDS_SG",
                                                 vpc=cdk_lab_vpc,
                                                 allow_all_outbound=True,
                                                 description="Allow inbound mySQL traffic from webservers")

        # Allow inbound traffic on port 3306 from the Web server security group to the RDS security group
        rds_lab_web_server_sg.add_ingress_rule(peer=cdk_lab_web_server_sg, 
                                              connection=ec2.Port.tcp(3306),
                                              description = "Allow inbound mySQL traffic from webservers")
                                              
                                              
    
        #A subnet group for RDS using all private subnets
        rds_subnet_group = rds.SubnetGroup(self, "RdsSubnetGroup",
                                          vpc = cdk_lab_vpc,
                                          description="Subnet group for RDS",
                                          vpc_subnets=cdk_lab_vpc.select_subnets(ec2.SubnetType.PRIVATE_WITH_EGRESS))
                                            
                                            
        # Web instances
        cdk_lab_web_instance1 = ec2.Instance(self, "cdk_lab_web_instance1", vpc=cdk_lab_vpc,
                                            instance_type=ec2.InstanceType("t2.micro"),
                                            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                            role=InstanceRole,
                                            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                            security_group=cdk_lab_web_server_sg)

        cdk_lab_web_instance2 = ec2.Instance(self, "cdk_lab_web_instance2", vpc=cdk_lab_vpc,
                                            instance_type=ec2.InstanceType("t2.micro"),
                                            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
                                            role=InstanceRole,
                                            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                                            security_group=cdk_lab_web_server_sg)                                     
                                            
                                            
        #A RDS instance with MySQL engine with all private subnets as its subnet group
        
        cdk_lab_rds_instance = rds.DatabaseInstance(self, "RdsInstance",
                                                    engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_23),
                                                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,ec2.InstanceSize.MICRO),
                                                    vpc=cdk_lab_vpc,
                                                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                                                    subnet_groups=rds_subnet_group,
                                                    security_groups=[rds_lab_web_server_sg],
                                                    removal_policy=cdk_lab_vpc.RemovalPolicy.DESTROY)
                                                    
        
        # Script in S3 as Asset
        for cdk_lab_web_instance in [cdk_lab_web_instance1, cdk_lab_web_instance2]:
            webinitscriptasset = S3asset(self, "Asset", path=os.path.join(dirname, "configure.sh"))
            asset_path = cdk_lab_web_instance.user_data.add_s3_download_command(
                bucket=webinitscriptasset.bucket,
                bucket_key=webinitscriptasset.s3_object_key
            )
    
            # Userdata executes script from S3
            cdk_lab_web_instance.user_data.add_execute_file_command(
                file_path=asset_path
                )
            webinitscriptasset.grant_read(cdk_lab_web_instance.role)
            
          


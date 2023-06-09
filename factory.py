from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from cdktf_cdktf_provider_aws.provider import AwsProvider




from cdktf_cdktf_provider_aws.subnet import Subnet
from cdktf_cdktf_provider_aws.vpc import Vpc


from cdktf_cdktf_provider_aws.internet_gateway import InternetGateway
from cdktf_cdktf_provider_aws.route import Route



from cdktf_cdktf_provider_aws.nat_gateway import NatGateway
from cdktf_cdktf_provider_aws.eip import Eip


from cdktf_cdktf_provider_aws.route_table import RouteTable

from cdktf_cdktf_provider_aws.route_table_association import RouteTableAssociation



# from cdktf_cdktf_provider_aws.eks_cluster import EksCluster
# from cdktf_cdktf_provider_aws.eks_node_group import EksNodeGroup

class ResourceFactory:
    def __init__(self, stack: TerraformStack, provider: AwsProvider):
        self.stack = stack
        self.provider = provider

    def create_resource(self, aws_resource, resource_name, **resource_data):
        resource = aws_resource(self.stack, resource_name, provider=self.provider, **resource_data)
        return resource

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Define resources here
        provider = AwsProvider(self, "AWS", region="ap-northeast-2")
        resource_factory = ResourceFactory(self, provider)

        vpc_data = {
            "cidr_block": "10.0.0.0/16"
        }
        vpc = resource_factory.create_resource(Vpc, "my-vpc", **vpc_data)
        
        
        # print( "vpc:", vpc)
        # print( "vpc_id:", vpc.id)
        
        
        
        #  1. 
        #  2. tag 작업 
        
        private_subnet_data = [
            {
                "vpc_id": vpc.id,                
                "cidr_block": "10.0.1.0/24",
                "availability_zone": "ap-northeast-2a",
            },
            {
                "vpc_id": vpc.id,                
                "cidr_block": "10.0.2.0/24",
                "availability_zone": "ap-northeast-2b"
            },
            
        ]
        
        public_subnet_data = [
            {
                "vpc_id": vpc.id,                
                "cidr_block": "10.0.10.0/24",
                "availability_zone": "ap-northeast-2a",
                
            },
            {
                "vpc_id": vpc.id,                
                "cidr_block": "10.0.20.0/24",
                "availability_zone": "ap-northeast-2b"
                
            },
            
        ]
        
        
        i = 0
        private_subnets = []
        for data in private_subnet_data:
            i = i + 1
            private_subnet = resource_factory.create_resource(Subnet, f"my-private-subnet-{i}", **data)
            private_subnets.append(private_subnet)
            
        public_subnets = []
        for data in public_subnet_data:
            i = i + 1
            public_subnet = resource_factory.create_resource(Subnet, f"my-public-subnet-{i}", **data)
            public_subnets.append(public_subnet)
        
        ######################################### subnet end ############################################
        
        
                    
        
        
        vpc_config = {
                "endpoint_private_access"   :  True,
                "endpoint_public_access"    :  False,
                "subnet_ids"                : [subnet.id for subnet in private_subnets],
                "public_access_cidrs"       : [subnet.cidr_block for subnet in public_subnets] , 
                "public_access_cidrs"       : [subnet.cidr_block for subnet in private_subnets] , 
                #"security_group_ids"        : 
                
                #"vpcId": vpc.vpc_id,
                
        }
        
        
        ##################################### 1-1. internet_gateway make         
   
        
        internet_gateway = resource_factory.create_resource(InternetGateway, "my-internet-gateway", vpc_id=vpc.id)  
        
        
        
        ##################################### 1-2. public route table make
        public_routeTable_data = {
            "vpc_id" : vpc.id,
            "tags" : {
                    "Name" : f"my-public-routetable-",
                }            
        }       
        public_route_table = resource_factory.create_resource(RouteTable, "my-public-route-table", **public_routeTable_data)
        
        ##################################### 1-3. public routing table igw association make 
        
        route_igw_data = {                
                "route_table_id"        : public_route_table.id,
                "destination_cidr_block" : "0.0.0.0/0",
                "gateway_id"            : internet_gateway.id
                    
        }
        public_route_table_igw_associate = resource_factory.create_resource(
                                            Route, 
                                            f"route-igw-association-{i}", 
                                            **route_igw_data)            
            
        #print("routeing table id:", public_route_table.id)
        #print("routing table id:", TerraformOutput(self, "RoutingTableId", value=public_route_table.id))      
        
        
        
        ##################################### 4.public routing table association make 
        # public_route_table_associate = []
        # for subnet in public_subnets:
        #     i = i + 1
        #     routeTable_data = {
        #         "route_table_id" : public_route_table.id,                
        #         "subnet_id"     : subnet.id
                
        #     }
        #     print ("routeTable-data:", routeTable_data)
        #     public_route_table_associate = resource_factory.create_resource(
        #                                     RouteTableAssociation, 
        #                                     f"routingtable-association-{i}", 
        #                                     **routeTable_data)
            
        #####################################  2-1 natgateway eip make
        # Create EIP (Elastic IP)
#        eip = resource_factory.create_resource(Eip, "my-eip")
   
        #####################################  2-1 natgateway make
        
        # private_natgateways = []
        # for subnet in private_subnets:
        
        #     nat_gateway_data = {
        #         "subnet_id":    subnet.id,
        #         "allocation_id": 
        #         "tags" : {
        #             "Name" : f"my-nat-gateway-{subnet.availability_zone}"
        #         }
                
        #     }
        #     nat_gateway = resource_factory.create_resource(NatGateway, f"my-nat-gateway-{subnet.availability_zone}", **nat_gateway_data)
        #     private_natgateways.append(nat_gateway)
        
        # ##################################### 2-2 private route table make
        # private_routeTable_data = {
        #     "vpc_id" : vpc.id,
        #     "tags" : {
        #             "Name" : f"my-private-routetable",
        #         }            
        # }     
        
        # private_route_table = resource_factory.create_resource(RouteTable, "my-private-route-table", **private_routeTable_data)

        # ##################################### 2-3 private route table make
        
        
        # route_natgateway_data = {                
        #         "route_table_id"         : public_route_table.id,
        #         "destination_cidr_block" : "0.0.0.0/0",
        #         "nat_gateway_id"         : nat_gateway.id
                    
        # }
        # public_route_table_natgateway_associate = resource_factory.create_resource(
        #                                     Route, 
        #                                     f"route-natgateway-association-{i}", 
        #                                     **route_natgateway_data)    
        
        # ##################################### 2-4 private route table make
        # private_route_table_associate = []
        # for subnet in private_subnets:
        #     i = i + 1
        #     routeTable_data = {
        #         "route_table_id" : private_route_table.id,                
        #         "subnet_id"     : subnet.id
                
        #     }
        #     print ("routeTable-data:", routeTable_data)
        #     private_route_table_associate = resource_factory.create_resource(
        #                                     RouteTableAssociation, 
        #                                     f"routingtable-association-{i}", 
        #                                     **routeTable_data)
            
        
        # # # Create Route  private Table  private
        # route_table = resource_factory.create_resource(RouteTable, "my-public-route-table", vpc_id=vpc.id)
        

        # # Create Route for Internet Gateway
        # route_data = {
        #     "route_table_id": route_table.id,
        #     "destination_cidr_block": "0.0.0.0/0",
        #     "gateway_id": internet_gateway.id,
        # }
        # route = resource_factory.create_resource(Route, "my-route", **route_data)
        




       
       
        
        
# resource "aws_eks_cluster" "example" {
#   name     = "example-cluster"
#   role_arn = aws_iam_role.example.arn

#   vpc_config {
#     endpoint_private_access = true
#     endpoint_public_access  = false
#     # ... other configuration ...
#   }

#   outpost_config {
#     control_plane_instance_type = "m5d.large"
#     outpost_arns                = [data.aws_outposts_outpost.example.arn]
#   }
# }
        
#     #      @jsii.member(jsii_name="putVpcConfig")
    # def put_vpc_config(
    #     self,
    #     *,
    #     subnet_ids: typing.Sequence[builtins.str],
    #     endpoint_private_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    #     endpoint_public_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    #     public_access_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    #     security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    # ) -> None:
        
        # connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        # count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        # depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        # for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        # lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        # provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        # provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        # assign_generated_ipv6_cidr_block: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # cidr_block: typing.Optional[builtins.str] = None,
        # enable_classiclink: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # enable_classiclink_dns_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # enable_dns_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # enable_dns_support: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # enable_network_address_usage_metrics: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        # id: typing.Optional[builtins.str] = None,
        # instance_tenancy: typing.Optional[builtins.str] = None,
        # ipv4_ipam_pool_id: typing.Optional[builtins.str] = None,
        # ipv4_netmask_length: typing.Optional[jsii.Number] = None,
        # ipv6_cidr_block: typing.Optional[builtins.str] = None,
        # ipv6_cidr_block_network_border_group: typing.Optional[builtins.str] = None,
        # ipv6_ipam_pool_id: typing.Optional[builtins.str] = None,
        # ipv6_netmask_length: typing.Optional[jsii.Number] = None,
        # tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        # tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
      
            
            
        # # /home/skycloud/.local/share/virtualenvs/ec2-instance-coWcOciz/lib/python3.11/site-packages/cdktf_cdktf_provider_aws/eks_cluster/__init__.py
        # eks_cluster_data = {
        #     "name" : "my-eks-clsters",
        #     "role_arn" : "arn:aws:iam::557269744548:role/My-EKS-Cluster-cluster-role", 
                          
            
        #     "version": "1.24",
        #     "vpc_config" : vpc_config
        #     #  config = EksClusterConfig(
        #     # enabled_cluster_log_types=enabled_cluster_log_types,
        #     # encryption_config=encryption_config,
        #     #   name=name,
        #     # role_arn=role_arn,
        #     # vpc_config=vpc_config,
        #     # enabled_cluster_log_types=enabled_cluster_log_types,
        #     # encryption_config=encryption_config,
        #     # id=id,
        #     # kubernetes_network_config=kubernetes_network_config,
        #     # outpost_config=outpost_config,
        #     # tags=tags,
        #     # tags_all=tags_all,
        #     # timeouts=timeouts,
        #     # version=version,
        #     # connection=connection,
        #     # count=count,
        #     # depends_on=depends_on,
        #     # for_each=for_each,
        #     # lifecycle=lifecycle,
        #     # provider=provider,
        #     # provisioners=provisioners
        # }
        # #eks_cluster = resource_factory.create_resource(EksCluster, "my-eks-cluster", **eks_cluster_data)
        
        
           
        # eks_node_group_data = {
        #     "cluster_name": eks_cluster.cluster_name,
        #     "instance_types": ["t3.medium"],
        #     "desired_capacity": 3
        # }
        # eks_node_group = resource_factory.create_resource(EksNodeGroup, "my-eks-node-group", **eks_node_group_data)
        
         # Uncomment the following code to create an EKS cluster and node group
"""
        # Create EKS Cluster
        eks_cluster = resource_factory.create_resource(EksCluster, "my-eks-cluster",
                                                      name="my-eks-cluster",
                                                      role_arn="<EKS-CLUSTER-ROLE-ARN>",
                                                      version="1.21")
        
        # Create EKS Node Group
        eks_node_group = resource_factory.create_resource(EksNodeGroup, "my-eks-node-group",
                                                         cluster_name=eks_cluster.name,
                                                         node_group_name="my-eks-node-group",
                                                         node_group_desired_size=2,
                                                         node_group_instance_types=["t3.medium"],
                                                         node_group_remote_access=[{
                                                             "cidr_blocks": ["0.0.0.0/0"],
                                                             "security_group_ids": ["<SECURITY-GROUP-ID>"],
                                                             "ec2_ssh_key": "<SSH-KEY-NAME>"
                                                         }],
                                                         node_group_subnet_ids=[private_subnets[0].id])
"""

app = App()
MyStack(app, "factory")

app.synth()

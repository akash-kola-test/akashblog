---
title: AWS ECS - Assignment 1
date: 2024-12-09
draft: false
tags:
  - aws-training-tasks
  - ecs
---
1. Let's create the IAM role for our EC2 instances to talk with the cluster, to make template more dynamic I'm using mappings

```yml
Mappings:
  PolicyConfigs:
    DocumentVersions:
      CurrentVersion: "2012-10-17"
    AWSManagedPolicyArns:
      AmazonECSFullAccessPolicy: "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
      TaskExecutionRolePolicy: "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
```

```yml
ECSAgentAndTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: ECSAgentAndTaskRole
      AssumeRolePolicyDocument:
        Version: !FindInMap [ PolicyConfigs, DocumentVersions, CurrentVersion ]
        Statement:
        - Effect: Allow
          Action: sts:AssumeRole
          Principal:
            Service:
            - "ec2.amazonaws.com"
            - "ecs-tasks.amazonaws.com"
      ManagedPolicyArns:
      - !FindInMap [ PolicyConfigs, AWSManagedPolicyArns, AmazonECSFullAccessPolicy ]
      - !FindInMap [ PolicyConfigs, AWSManagedPolicyArns, TaskExecutionRolePolicy ]
```

2. Now let's create the IAM instance profile to attach the above role to our EC2 instances

```yml
  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
        InstanceProfileName: ECSEC2IamInstanceProfile
        Roles:
          - !Ref EC2IamRole 
```

3. Configure security group and ingress traffic for our EC2 Host and tasks

```yml
EC2AndTaskSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: "Security group for tasks and EC2 host"
      VpcId: !FindInMap [ VpcConfigs, DefaultVpc, Id ]

  EC2AndTaskSecurityGroupIngressWeb1:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 8080
      ToPort: 8080
      IpProtocol: tcp

  EC2AndTaskSecurityGroupIngressWeb2:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 80
      ToPort: 80
      IpProtocol: tcp

  EC2AndTaskSecurityGroupIngressSSH:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 22
      ToPort: 22
      IpProtocol: tcp

```

4. Let's create launch template for our Auto scaling group

```yml
EC2LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: ECSAgentLaunchTemplate
      LaunchTemplateData:
        IamInstanceProfile:
          Arn: !GetAtt EC2InstanceProfile.Arn
        ImageId: "ami-0453ec754f44f9a4a"
        InstanceType: "t2.micro"
        KeyName: RegularSshPemKey
        SecurityGroupIds:
        - !GetAtt EC2AndTaskSecurityGroup.GroupId
        UserData:
          Fn::Base64: |
            #!/bin/bash
            # install docker
            yum update -y
            yum install -y docker
            usermod -a -G docker ec2-user
            systemctl enable --now --no-block docker.service

            # install ecs agent
            curl -O https://s3.us-east-1.amazonaws.com/amazon-ecs-agent-us-east-1/amazon-ecs-init-latest.x86_64.rpm
            yum localinstall -y amazon-ecs-init-latest.x86_64.rpm
            echo "ECS_CLUSTER=MyCluster" >> /etc/ecs/ecs.config
            systemctl enable --now --no-block ecs.service

```

5. Let's create the auto scaling group now

```yml
ECSASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: ECSASG
      AvailabilityZones:
      # !GetAZs AWS::Region
      - !FindInMap [ RegionConfigs, UsEast1, Az1 ]
      - !FindInMap [ RegionConfigs, UsEast1, Az2 ]
      - !FindInMap [ RegionConfigs, UsEast1, Az3 ]
      LaunchTemplate:
        LaunchTemplateId: !Ref EC2LaunchTemplate
        Version: !GetAtt EC2LaunchTemplate.LatestVersionNumber
      MaxSize: 2
      MinSize: 0
      NewInstancesProtectedFromScaleIn: true

```

6. Let's create ECS cluster, EC2 capacity provider and let's attach capacity provider to ECS cluster

```yml
TaskECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: MyCluster

  TaskECSClusterEC2CapacityProvider:
    Type: AWS::ECS::CapacityProvider
    Properties:
      Name: EC2Group
      AutoScalingGroupProvider:
        AutoScalingGroupArn: !Ref ECSASG
        ManagedScaling:
          Status: ENABLED
        ManagedDraining: ENABLED
        ManagedTerminationProtection: ENABLED

  TaskECSCapacityProviderAssociation:
    Type: AWS::ECS::ClusterCapacityProviderAssociations
    Properties:
      CapacityProviders:
      - !Ref TaskECSClusterEC2CapacityProvider
      - "FARGATE"
      - "FARGATE_SPOT"
      Cluster: !Ref TaskECSCluster
      DefaultCapacityProviderStrategy:
      - Base: 1
        CapacityProvider: !Ref TaskECSClusterEC2CapacityProvider
        Weight: 1

```

7. Let's create task 1 which will use our EC2 capacity provider

```yml
TaskDefinition1:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
      - Name: Container1
        Image: "180294179946.dkr.ecr.us-east-1.amazonaws.com/akash/task1-image:latest"
        PortMappings:
        - ContainerPort: 80
          HostPort: 8080
        LogConfiguration:
          LogDriver: awslogs
          Options:
            mode: non-blocking
            max-buffer-size: 25m
            awslogs-group: LogGroup
            awslogs-region: us-east-1
            awslogs-create-group: "true"
            awslogs-stream-prefix: efs-task-service-1
      Cpu: "256"
      ExecutionRoleArn: !GetAtt ECSAgentAndTaskRole.Arn
      Family: TaskDefinition1
      Memory: "512"
      NetworkMode: bridge
      TaskRoleArn: !GetAtt ECSAgentAndTaskRole.Arn

```

8. Let's now create the task definition 2 which will FARGATE as capacity provider

```yml
TaskDefinition2:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
      - Name: Container1
        Image: "180294179946.dkr.ecr.us-east-1.amazonaws.com/akash/task2-image:latest"
        LogConfiguration:
          LogDriver: awslogs
          Options:
            mode: non-blocking
            max-buffer-size: 25m
            awslogs-group: LogGroup
            awslogs-region: us-east-1
            awslogs-create-group: "true"
            awslogs-stream-prefix: efs-task-service-1
        PortMappings:
        - ContainerPort: 80
      Cpu: "256"
      ExecutionRoleArn: !GetAtt ECSAgentAndTaskRole.Arn
      Family: TaskDefinition2
      Memory: "512"
      NetworkMode: awsvpc
      TaskRoleArn: !GetAtt ECSAgentAndTaskRole.Arn

```

9. Let's create services for those tasks

```yml
Service1:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !GetAtt TaskECSCluster.Arn
      DesiredCount: 1
      ServiceName: Service1
      TaskDefinition: TaskDefinition1
      CapacityProviderStrategy:
      - CapacityProvider: EC2Group
        Base: 1
        Weight: 1
    DependsOn:
      - TaskDefinition1

  Service2:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !GetAtt TaskECSCluster.Arn
      DesiredCount: 1
      ServiceName: Service2
      TaskDefinition: TaskDefinition2
      CapacityProviderStrategy:
      - CapacityProvider: FARGATE
        Base: 1
        Weight: 1
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          SecurityGroups:
          - !GetAtt EC2AndTaskSecurityGroup.GroupId
          Subnets:
          - "subnet-02f6cc9a140bac4f2"
          - "subnet-07d33940df964784d"
          - "subnet-068bb65beb221f69b"
    DependsOn:
      - TaskDefinition2

```

10. Now let's create the cloud formation stack with this configuration template

```sh
aws cloudformation create-stack --stack-name ecs --template-body file://ecs-template.cfn.yml --capabilities CAPABILITY_NAMED_IAM
```

```yml
Mappings:
  PolicyConfigs:
    DocumentVersions:
      CurrentVersion: "2012-10-17"
    AWSManagedPolicyArns:
      AmazonECSFullAccessPolicy: "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
      TaskExecutionRolePolicy: "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

  VpcConfigs:
    DefaultVpc:
      Id: "vpc-0549574e741f7f99f"

  RegionConfigs:
    UsEast1:
      Az1: "us-east-1a"
      Az2: "us-east-1b"
      Az3: "us-east-1c"

Resources:
  ECSAgentAndTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: ECSAgentAndTaskRole
      AssumeRolePolicyDocument:
        Version: !FindInMap [ PolicyConfigs, DocumentVersions, CurrentVersion ]
        Statement:
        - Effect: Allow
          Action: sts:AssumeRole
          Principal:
            Service:
            - "ec2.amazonaws.com"
            - "ecs-tasks.amazonaws.com"
      ManagedPolicyArns:
      - !FindInMap [ PolicyConfigs, AWSManagedPolicyArns, AmazonECSFullAccessPolicy ]
      - !FindInMap [ PolicyConfigs, AWSManagedPolicyArns, TaskExecutionRolePolicy ]

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: ECSEC2IamInstanceProfile
      Roles:
      - !Ref ECSAgentAndTaskRole

  EC2AndTaskSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: "Security group for tasks and EC2 host"
      VpcId: !FindInMap [ VpcConfigs, DefaultVpc, Id ]

  EC2AndTaskSecurityGroupIngressWeb1:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 8080
      ToPort: 8080
      IpProtocol: tcp

  EC2AndTaskSecurityGroupIngressWeb2:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 80
      ToPort: 80
      IpProtocol: tcp

  EC2AndTaskSecurityGroupIngressSSH:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 22
      ToPort: 22
      IpProtocol: tcp

  EC2LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: ECSAgentLaunchTemplate
      LaunchTemplateData:
        IamInstanceProfile:
          Arn: !GetAtt EC2InstanceProfile.Arn
        ImageId: "ami-0453ec754f44f9a4a"
        InstanceType: "t2.micro"
        KeyName: RegularSshPemKey
        SecurityGroupIds:
        - !GetAtt EC2AndTaskSecurityGroup.GroupId
        UserData:
          Fn::Base64: |
            #!/bin/bash
            # install docker
            yum update -y
            yum install -y docker
            usermod -a -G docker ec2-user
            systemctl enable --now --no-block docker.service

            # install ecs agent
            curl -O https://s3.us-east-1.amazonaws.com/amazon-ecs-agent-us-east-1/amazon-ecs-init-latest.x86_64.rpm
            yum localinstall -y amazon-ecs-init-latest.x86_64.rpm
            echo "ECS_CLUSTER=MyCluster" >> /etc/ecs/ecs.config
            systemctl enable --now --no-block ecs.service

  ECSASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: ECSASG
      AvailabilityZones:
      # !GetAZs AWS::Region
      - !FindInMap [ RegionConfigs, UsEast1, Az1 ]
      - !FindInMap [ RegionConfigs, UsEast1, Az2 ]
      - !FindInMap [ RegionConfigs, UsEast1, Az3 ]
      LaunchTemplate:
        LaunchTemplateId: !Ref EC2LaunchTemplate
        Version: !GetAtt EC2LaunchTemplate.LatestVersionNumber
      MaxSize: 2
      MinSize: 0
      NewInstancesProtectedFromScaleIn: true

  TaskECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: MyCluster

  TaskECSClusterEC2CapacityProvider:
    Type: AWS::ECS::CapacityProvider
    Properties:
      Name: EC2Group
      AutoScalingGroupProvider:
        AutoScalingGroupArn: !Ref ECSASG
        ManagedScaling:
          Status: ENABLED
        ManagedDraining: ENABLED
        ManagedTerminationProtection: ENABLED

  TaskECSCapacityProviderAssociation:
    Type: AWS::ECS::ClusterCapacityProviderAssociations
    Properties:
      CapacityProviders:
      - !Ref TaskECSClusterEC2CapacityProvider
      - "FARGATE"
      - "FARGATE_SPOT"
      Cluster: !Ref TaskECSCluster
      DefaultCapacityProviderStrategy:
      - Base: 1
        CapacityProvider: !Ref TaskECSClusterEC2CapacityProvider
        Weight: 1

  TaskDefinition1:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
      - Name: Container1
        Image: "180294179946.dkr.ecr.us-east-1.amazonaws.com/akash/task1-image:latest"
        PortMappings:
        - ContainerPort: 80
          HostPort: 8080
        LogConfiguration:
          LogDriver: awslogs
          Options:
            mode: non-blocking
            max-buffer-size: 25m
            awslogs-group: LogGroup
            awslogs-region: us-east-1
            awslogs-create-group: "true"
            awslogs-stream-prefix: efs-task-service-1
      Cpu: "256"
      ExecutionRoleArn: !GetAtt ECSAgentAndTaskRole.Arn
      Family: TaskDefinition1
      Memory: "512"
      NetworkMode: bridge
      TaskRoleArn: !GetAtt ECSAgentAndTaskRole.Arn

  TaskDefinition2:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
      - Name: Container1
        Image: "180294179946.dkr.ecr.us-east-1.amazonaws.com/akash/task2-image:latest"
        LogConfiguration:
          LogDriver: awslogs
          Options:
            mode: non-blocking
            max-buffer-size: 25m
            awslogs-group: LogGroup
            awslogs-region: us-east-1
            awslogs-create-group: "true"
            awslogs-stream-prefix: efs-task-service-1
        PortMappings:
        - ContainerPort: 80
      Cpu: "256"
      ExecutionRoleArn: !GetAtt ECSAgentAndTaskRole.Arn
      Family: TaskDefinition2
      Memory: "512"
      NetworkMode: awsvpc
      TaskRoleArn: !GetAtt ECSAgentAndTaskRole.Arn

  Service1:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !GetAtt TaskECSCluster.Arn
      DesiredCount: 1
      ServiceName: Service1
      TaskDefinition: TaskDefinition1
      CapacityProviderStrategy:
      - CapacityProvider: EC2Group
        Base: 1
        Weight: 1
    DependsOn:
      - TaskDefinition1

  Service2:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !GetAtt TaskECSCluster.Arn
      DesiredCount: 1
      ServiceName: Service2
      TaskDefinition: TaskDefinition2
      CapacityProviderStrategy:
      - CapacityProvider: FARGATE
        Base: 1
        Weight: 1
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          SecurityGroups:
          - !GetAtt EC2AndTaskSecurityGroup.GroupId
          Subnets:
          - "subnet-02f6cc9a140bac4f2"
          - "subnet-07d33940df964784d"
          - "subnet-068bb65beb221f69b"
    DependsOn:
      - TaskDefinition2

```

![ECS cloud formation stack creation](images/ECS%20cloud%20formation%20stack%20creation.png)

![ECS CF stack creation in progress](images/ECS%20CF%20stack%20creation%20in%20progress.png)

11. Let's wait for it to complete and access our websites from both tasks

![ECS cluster creation successfull](images/ECS%20cluster%20creation%20successfull.png)

12. Let's open our task 1 website

![Task 1 Public IP](images/Task%201%20Public%20IP.png)

![Task 1 website](images/Task%201%20website.png)

13. Now let's open our task 2 website

![Task 2 IP address](images/Task%202%20IP%20address.png)

![Task 2 Website](images/Task%202%20Website.png)


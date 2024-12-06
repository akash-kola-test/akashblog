---
title: AWS ECS - Assignment 1
date: 2024-12-03
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
      AmazonECSFullAccess: "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
```

```yml
EC2IamRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: ECSEC2IamRole
      AssumeRolePolicyDocument:
        Version: !FindInMap [ PolicyConfigs, DocumentVersions, CurrentVersion ]
        Statement:
          - Effect: Allow
            Action: sts:AssumeRole
            Principal:
              Service: "ec2.amazaonaws.com"
      ManagedPolicyArns:
        - !FindInMap [ PolicyConfigs, AWSManagedPolicyArns, AmazonECSFullAccess ]
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

  EC2AndTaskSecurityGroupIngress:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      CidrIp: "0.0.0.0/0"
      GroupId: !GetAtt EC2AndTaskSecurityGroup.GroupId
      FromPort: 80
      ToPort: 81
      IpProtocol: tcp
```


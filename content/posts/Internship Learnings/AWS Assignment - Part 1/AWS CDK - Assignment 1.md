---
title: AWS CDK - Assignment 1
date: 2024-12-16
draft: false
tags:
  - aws-training-tasks
  - "#cdk"
---
1. After creating the project replace the existing resources with the following code inside stack file

```ts
    const kms_key = new Key(this, "KmsKey");

    new Bucket(this, "S3Bucket", {
      bucketName: "",
      versioned: true,
      encryption: BucketEncryption.KMS,
      encryptionKey: kms_key,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
```

- First we created the KMS key and later we used that key to encrypt our bucket objects

2. Let's add KMS key created test

```ts
test("Kms key is created", () => {
  const app = new App();
  const stack = new Assignment1Stack(app, "teststack");

  const template = Template.fromStack(stack);

  template.resourceCountIs("AWS::KMS::Key", 1);

});
```

3. Let's add another test for if KMS encryption is enabled for the bucket or not

```ts
test("SSE KMS encryption is enabled for the bucket", () => {
  const app = new App();
  const stack = new Assignment1Stack(app, "teststack");

  const template = Template.fromStack(stack);

  const expectedBucketProperties = {
    BucketEncryption: {
      ServerSideEncryptionConfiguration: [
        {
          ServerSideEncryptionByDefault: {
            SSEAlgorithm: "aws:kms",
          },
        },
      ],
    },
  };

  template.hasResourceProperties("AWS::S3::Bucket", expectedBucketProperties);
});
```

4. Let's add another test to check if the created key only is being used for objects encryption

```ts
test("Created KMS key is being utilized by bucket for encryption", () => {
  const app = new App();
  const stack = new Assignment1Stack(app, "teststack");

  const template = Template.fromStack(stack);

  const expectedBucketProperties = {
    BucketEncryption: {
      ServerSideEncryptionConfiguration: [
        {
          ServerSideEncryptionByDefault: {
            KMSMasterKeyID: {
              "Fn::GetAtt": ["KmsKey46693ADD", "Arn"],
            },
          },
        },
      ],
    },
  };

  template.hasResourceProperties("AWS::S3::Bucket", expectedBucketProperties);
});
```

5. Let's execute the tests, and we can see that all passed

![AWS CDK - Assignment 1 - Tests passed](images/AWS%20CDK%20-%20Assignment%201%20-%20Tests%20passed.png)

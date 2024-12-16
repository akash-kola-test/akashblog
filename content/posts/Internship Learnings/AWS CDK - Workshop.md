---
draft: true
title: AWS CDK - Workshop
date: 2024-12-10
tags:
  - aws-training-tasks
  - "#cdk"
---
### Prerequisites
- AWS CLI
- AWS Account and User configured with AWS CLI
- Node JS > 18
- AWS CDK Toolkit

### Sample application

1. Initializing a project with the init command

```sh
cdk init sample-app --language typescript
```

![AWS CDK - Workshop - CDK Init Example](images/AWS%20CDK%20-%20Workshop%20-%20CDK%20Init%20Example.png)

2. Generating Cloud formation template for the CDK project, output should show something like below as our project is already containing a sample app with Queue and SNS integration.

```sh
cdk synth
```

![AWS CDK - Workshop - Synth Output](images/AWS%20CDK%20-%20Workshop%20-%20Synth%20Output.png)

![AWS CDK - Workshop - Sample app code](images/AWS%20CDK%20-%20Workshop%20-%20Sample%20app%20code.png)

3. Before we deploy our project, we need to bootstrap the CDK so that it will create necessary recourses to store it's assets and other things

```sh
cdk bootstrap
```

4. Now we can deploy this sample app using CDK's deploy command

```sh
cdk deploy
```

![AWS CDK - Workshop - CF Stack](images/AWS%20CDK%20-%20Workshop%20-%20CF%20Stack.png)

![AWS CDK - Workshop - Deploy output](images/AWS%20CDK%20-%20Workshop%20-%20Deploy%20output.png)


### Custom constructs - Hit Counter

We can also create our own constructs to increase re usability of the resources. Let's create something like below

![AWS CDK - Workshop - Custom Construct Architecture](images/AWS%20CDK%20-%20Workshop%20-%20Custom%20Construct%20Architecture.png)

1. Create a new file under lib called **hitcounter.ts** with the following content:

```ts
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export interface HitCounterProps {
  /** the function for which we want to count url hits **/
  downstream: IFunction;
}

export class HitCounter extends Construct {
  constructor(scope: Construct, id: string, props: HitCounterProps) {
    super(scope, id);

    // TODO
  }
}
```

  
- We declared a new construct class called `HitCounter`.
- As usual, constructor arguments are `scope`, `id` and `props`, and we propagate them to the `cdk.Construct` base class.
- The `props` argument is of type `HitCounterProps` which includes a single property `downstream` of type `lambda.IFunction`. This is where we are going to "plug in" the Lambda function we created in the previous chapter so it can be hit-counted.

2. Now let's write the Lambda handler code for our hit counter, create the file **lambda/hitcounter.js**

```ts
const { DynamoDB } = require("@aws-sdk/client-dynamodb");
const { Lambda, InvokeCommand } = require("@aws-sdk/client-lambda");

exports.handler = async function (event) {
  console.log("request:", JSON.stringify(event, undefined, 2));

  // create AWS SDK clients
  const dynamo = new DynamoDB();
  const lambda = new Lambda();

  // update dynamo entry for "path" with hits++
  await dynamo.updateItem({
    TableName: process.env.HITS_TABLE_NAME,
    Key: { path: { S: event.path } },
    UpdateExpression: "ADD hits :incr",
    ExpressionAttributeValues: { ":incr": { N: "1" } },
  });

  // call downstream function and capture response
  const command = new InvokeCommand({
    FunctionName: process.env.DOWNSTREAM_FUNCTION_NAME,
    Payload: JSON.stringify(event),
  });

  const { Payload } = await lambda.send(command);
  const result = Buffer.from(Payload).toString();

  console.log("downstream response:", JSON.stringify(result, undefined, 2));

  // return response back to upstream caller
  return JSON.parse(result);
};
```

- `HITS_TABLE_NAME` is the name of the DynamoDB table to use for storage.
- `DOWNSTREAM_FUNCTION_NAME` is the name of the downstream AWS Lambda function.

3.  Now, let's define the AWS Lambda function and the DynamoDB table in our `HitCounter` construct. Go back to `lib/hitcounter.ts` and add the following code:

```ts
import { AttributeType, Table } from "aws-cdk-lib/aws-dynamodb";
import { Code, Function, IFunction, Runtime } from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export interface HitCounterProps {
  /** the function for which we want to count url hits **/
  downstream: IFunction;
}

export class HitCounter extends Construct {
  /** allows accessing the counter function */
  public readonly handler: Function;

  constructor(scope: Construct, id: string, props: HitCounterProps) {
    super(scope, id);

    const table = new Table(this, "Hits", {
      partitionKey: { name: "path", type: AttributeType.STRING },
    });

    this.handler = new Function(this, "HitCounterHandler", {
      runtime: Runtime.NODEJS_18_X,
      handler: "hitcounter.handler",
      code: Code.fromAsset("lambda"),
      environment: {
        DOWNSTREAM_FUNCTION_NAME: props.downstream.functionName,
        HITS_TABLE_NAME: table.tableName,
      },
    });
  }
}
```

- We defined a DynamoDB table with `path` as the partition key.
- We defined a Lambda function which is bound to the `lambda/hitcounter.handler` code.
- We **wired** the Lambda's environment variables to the `functionName` and `tableName` of our resources.

4. Our hit counter is ready. Let's use it in our app. Open `lib/cdk-workshop-stack.ts` and modify your stack to look like this, also created hello.js file as mentioned below

```ts
/ defines an AWS Lambda resource
    const hello = new Function(this, "HelloHandler", {
      runtime: Runtime.NODEJS_18_X, // execution environment
      code: Code.fromAsset("lambda"), // code loaded from "lambda" directory
      handler: "hello.handler", // file is "hello", function is "handler"
    });

    const helloWithCounter = new HitCounter(this, "HelloHitCounter", {
      downstream: hello,
    });

    // defines an API Gateway REST API resource backed by our "hello" function.
    const gateway = new LambdaRestApi(this, "Endpoint", {
      handler: helloWithCounter.handler,
    });
```

```ts
// lambda/hello.js
exports.handler = async function (event) {
  console.log("request:", JSON.stringify(event, undefined, 2));
  return {
    statusCode: 200,
    headers: { "Content-Type": "text/plain" },
    body: `Good Night, CDK! You've hit ${event.path}\n`,
  };
};
```

5. As everything we configured, we can now deploy this and test it and we can see something went wrong. Let's check what's wrong with cloud watch logs

![AWS CDK - Workshop - Hitcounter Deploy output](images/AWS%20CDK%20-%20Workshop%20-%20Hitcounter%20Deploy%20output.png)

![AWS CDK - Workshop - First time Error](images/AWS%20CDK%20-%20Workshop%20-%20First%20time%20Error.png)

![AWS CDK - Workshop - Db permission issue](images/AWS%20CDK%20-%20Workshop%20-%20Db%20permission%20issue.png)

6. We can now see our Lambda function can't write to our DynamoDB table, let's give our Lambda's execution role permissions to read/write from our table in `lib/hitcounter.ts`.

```ts
table.grantReadWriteData(this.handler);
```

![AWS CDK - Workshop - Db Grant Permission](images/AWS%20CDK%20-%20Workshop%20-%20Db%20Grant%20Permission.png)

7. Let's deploy and test again, still getting this 5xx error! Let's look at our CloudWatch logs again. 

![AWS CDK - Workshop - Invoke Function Issue](images/AWS%20CDK%20-%20Workshop%20-%20Invoke%20Function%20Issue.png)

![AWS CDK - Workshop - Invoke Issue Logs](images/AWS%20CDK%20-%20Workshop%20-%20Invoke%20Issue%20Logs.png)

8. Our hit counter doesn't have permissions to invoke the downstream lambda function. So, let's add the lines to `lib/hitcounter.ts` as shown:

```ts
 props.downstream.grantInvoke(this.handler);
```

9. Now let's deploy and test it again. This time it works

![AWS CDK - Workshop - Final output](images/AWS%20CDK%20-%20Workshop%20-%20Final%20output.png)
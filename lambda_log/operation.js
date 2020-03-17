const { sleepPromise } = require('./util');


async function isS3BucketExists(bucketName, s3Instance) {
  try {
    const bucketsObject = await s3Instance.listBuckets({}).promise();
    return bucketsObject.Buckets.find(
      (bucket) => bucket.Name === bucketName
    );
  } catch (err) {
    console.error(err);
  }
}


async function waitForExportTaskToComplete(taskId, cloudwatchLogsInstance, waitErrorCount) {
  try {
    const taskDetails = await cloudwatchLogsInstance.describeExportTasks({ taskId: taskId }).promise();
    const task = taskDetails.exportTasks[0];
    const taskStatus = task.status.code;
    
    if (taskStatus === 'RUNNING' || taskStatus.indexOf('PENDING') !== -1) {
      console.log(`Task is running for ${task.logGroupName} with stats ${task.status}.`);
      await sleepPromise(1000);
      return await waitForExportTaskToComplete(taskId);
    }
    return true;
  } catch (error) {
    waitErrorCount++;
    if (waitErrorCount < 3) {
      return await waitForExportTaskToComplete(taskId, cloudwatchLogsInstance, waitErrorCount);
    }
    throw error;
  }
}


exports.createS3BucketAndPutPolicy = async function (bucketName, region, s3Instance) {
  try {
    const existFlag = await isS3BucketExists(bucketName);
    
    if (existFlag) {console.log('s3 bucket exists.');}
    else {
      await s3Instance.createBucket({ Bucket: bucketName }).promise();
      console.log(`s3 bucket ${bucketName} is created.`);

      await s3Instance.putBucketPolicy({
        Bucket: bucketName,
        Policy: "{\"Version\": \"2012-10-17\",\"Statement\": [{\"Effect\": \"Allow\",\
              \"Principal\": {\
                \"Service\": \"logs."+ region + ".amazonaws.com\"\
              },\
              \"Action\": \"s3:GetBucketAcl\",\
              \"Resource\": \"arn:aws:s3:::"+ bucketName + "\"\
            },\
            {\
              \"Effect\": \"Allow\",\
              \"Principal\": {\
                \"Service\": \"logs."+ region + ".amazonaws.com\"\
              },\
              \"Action\": \"s3:PutObject\",\
              \"Resource\": \"arn:aws:s3:::"+ bucketName + "/*\",\
              \"Condition\": {\
                \"StringEquals\": {\
                  \"s3:x-amz-acl\": \"bucket-owner-full-control\"\
                }\
              }\
            }\
          ]\
        }"
      }).promise();
      console.log('s3 bucket policy is added.');
    }
  } catch (err) {
    console.error(err);
  }
};


exports.getCloudWatchLogGroups = function(nextToken, limit, cloudwatchLogsInstance) {
  /*
  https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DescribeLogGroups.html#API_DescribeLogGroups_ResponseSyntax
  */
  const params = {
    nextToken: nextToken,
    limit: limit
  };
  return cloudwatchLogsInstance.describeLogGroups(params).promise();
};


exports.exportToS3Task = async function(s3BucketName, logGroupName, targetPath, cloudwatchLogsInstance) {
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  
  const params = {
    destination: s3BucketName,
    destinationPrefix: targetPath,
    from: yesterday.getTime(),
    logGroupName: logGroupName,
    to: today.getTime()
  };

  const response = await cloudwatchLogsInstance.createExportTask(params).promise();
  await waitForExportTaskToComplete(response.taskId, cloudwatchLogsInstance, 0);
};
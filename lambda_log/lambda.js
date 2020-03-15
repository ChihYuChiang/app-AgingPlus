const AWS = require('aws-sdk');
const __region = 'us-east-1';
let cloudwatchLogsInstance = new AWS.CloudWatchLogs({ region: __region });
let s3Instance = new AWS.S3({ region: __region });
const s3BucketName = 'AgingPlusLog';
const logFolderName = '';


// TODO: Move to util
async function isS3BucketExists(bucketName) {
  try {
    const bucketsObject = await s3Instance.listBuckets({}).promise();
    return bucketsObject.Buckets.find(
      (bucket) => bucket.Name === bucketName
    );
  } catch (err) {
    console.error(err);
  }
}


// TODO: Move to util
async function createS3BucketAndPutPolicy(bucketName) {
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
                \"Service\": \"logs."+ __region + ".amazonaws.com\"\
              },\
              \"Action\": \"s3:GetBucketAcl\",\
              \"Resource\": \"arn:aws:s3:::"+ bucketName + "\"\
            },\
            {\
              \"Effect\": \"Allow\",\
              \"Principal\": {\
                \"Service\": \"logs."+ __region + ".amazonaws.com\"\
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
}


function getDatePath(dateObj) {
  const year = dateObj.getFullYear();
  const month = dateObj.getMonth() + 1;
  const date = dateObj.getDate();
  return `${year}/${month}/${date}`;
}


function getLogGroupPath(logGroupName) {
  if (logGroupName.startsWith('/')) {
    logGroupName = logGroupName.slice(1);
  }
  return logGroupName.replace(/\//g, '-');
}


// TODO: Move to util
function wait(timeout) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve()
    }, timeout)
  });
}


let waitErrorCount = 0;
async function waitForExportTaskToComplete(taskId) {
  try {
    const taskDetails = await cloudwatchLogsInstance.describeExportTasks({ taskId: taskId }).promise();
    const task = taskDetails.exportTasks[0];
    const taskStatus = task.status.code;
    
    if (taskStatus === 'RUNNING' || taskStatus.indexOf('PENDING') !== -1) {
      console.log(`Task is running for ${task.logGroupName} with stats ${task.status}.`);
      await wait(1000);
      return await waitForExportTaskToComplete(taskId);
    }
    return true;
  } catch (error) {
    waitErrorCount++;
    if (waitErrorCount < 3) {
      return await waitForExportTaskToComplete(taskId);
    }
    throw error;
  }
}


async function exportToS3Task(s3BucketName, logGroupName, logFolderName) {
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  
  const params = {
    destination: s3BucketName,
    destinationPrefix: `${logFolderName}/${getLogGroupPath(logGroupName)}/${getDatePath(today)}`,
    from: yesterday.getTime(),
    logGroupName: logGroupName,
    to: today.getTime()
  };

  const response = await cloudwatchLogsInstance.createExportTask(params).promise();
  await waitForExportTaskToComplete(response.taskId);
}


// TODO: Move to util
function getCloudWatchLogGroups(nextToken, limit) {
  const params = {
    nextToken: nextToken,
    limit: limit
  };
  return cloudwatchLogsInstance.describeLogGroups(params).promise();
}


exports.handler = async (event) => {
  const nextToken = event.nextToken;
  const logGroupFilter = event.logGroupFilter;
  try {
    await createS3BucketAndPutPolicy(s3BucketName);
    let cloudWatchLogGroups = await getCloudWatchLogGroups(nextToken, 1);
    event.nextToken = cloudWatchLogGroups.nextToken;
    event.continue = cloudWatchLogGroups.nextToken !== undefined;
    if (cloudWatchLogGroups.logGroups.length < 1) {
      return event;
    }
    const logGroupName = cloudWatchLogGroups.logGroups[0].logGroupName;
    if (logGroupFilter && logGroupName.toLowerCase().indexOf(logGroupFilter) < 0) {
      // Ignore log group
      return event;
    }
    await exportToS3Task(s3BucketName, logGroupName, logFolderName);
    console.log("Successfully created export task for ", logGroupName);
    return event;
  } catch (error) {
    console.error(error);
    throw error;
  }
};
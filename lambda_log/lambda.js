const AWS = require('aws-sdk');
const {
  createS3BucketAndPutPolicy,
  getCloudWatchLogGroups,
  exportToS3Task
} = require('./operation');

const region = 'us-east-1';
const s3BucketName = 'AgingPlusLog';
const cloudwatchLogsInstance = new AWS.CloudWatchLogs({ region: region });
const s3Instance = new AWS.S3({ region: region });
const logGroupFilter = ['LineBot'];  // Preserve only LineBot logs


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


exports.handler = async (event) => {
  try {
    // Inspect the exsitance of the bucket; create one if needed
    await createS3BucketAndPutPolicy(s3BucketName, region, s3Instance);

    // Have to deal with next token if the return item number > limit (50)
    let cloudWatchLogGroups = await getCloudWatchLogGroups(50, cloudwatchLogsInstance);

    // Filter log groups
    const targetLogGroups = cloudWatchLogGroups.logGroups.filter(
      (g) => g.logGroupName.indexOf(logGroupFilter) > -1
    );

    // Exit when no return or all filtered out
    if (
      (cloudWatchLogGroups.logGroups.length < 1) ||
      (logGroupFilter && targetLogGroups.length < 1)
    ) {return;}
    
    // Log group export can't be paralleled
    for (let logGroup in targetLogGroups) {
      await exportToS3Task(
        s3BucketName, logGroup.logGroupName,
        `${getLogGroupPath(logGroup.logGroupName)}/${getDatePath(new Date())}`,  // Today
        cloudwatchLogsInstance
      );
      console.log("Successfully created export task for ", logGroup.logGroupName);
    }
  } catch (error) {
    console.error(error);
    throw error;
  }
};
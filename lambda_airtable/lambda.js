const Airtable = require("airtable");
const moment = require('moment-timezone');
const has = require('lodash/has');
const { retrieve, retrieveReduce, create, find } = require('./operation.js');
const { retrieveMemberIdByLineId } = require('./operation-sp.js');
const { filterUndefined } = require('./util');

const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow',
  REMINDER: 'reminder',
  NEXT_CLASS: 'next_class',
  HOMEWORK: 'homework'
};


//-- Handler middlewares
async function handle_follow(event) {
  if(event.eventType !== AIR_EVENT_TYPES.FOLLOW) { return; }

  const { lineUserId, lineDisplayName, lineProfilePic } = event;
  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    entries: [{
      "fields": {
        "LineUserId": lineUserId,
        "LineDisplayName": lineDisplayName,
        "LineProfilePicture": lineProfilePic
      }
    }]
  };

  // TODO: handle reject error
  await create(params);
  return { Status: 'handle_follow: OK' };
};

async function handle_reminder(event) {
  if(event.eventType !== AIR_EVENT_TYPES.REMINDER) { return; }

  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    processRecord: (record) => ({
      "id": record.id,
      "lineUserId": record.fields.LineUserId,
      "lineDisplayName": record.fields.LineDisplayName,
      "messageTime": moment(record.fields.MessageTime),
      "messageContent": record.fields.MessageContent    
    }),
    // If the scheduled message time is tomorrow
    filterRecord: (record) => moment().add(1, 'days').isSame(record.messageTime, 'day')
  };
  const targets = await retrieve(params);
  
  return { Status: 'handle_reminder: OK', Data: targets };
};

// TODO: Deal with no class found
async function handle_nextClass(event) {
  if(event.eventType !== AIR_EVENT_TYPES.NEXT_CLASS) { return; }

  // Use Line ID to get aging member id
  const params_1 = {
    base: base,
    sheet: 'LINE-MEMBER',
    processRecord: (record) => ({
      "lineUserId": record.fields.LineUserId,
      "lineDisplayName": record.fields.LineDisplayName,
      "memberId": record.fields.學員[0]
    }),
    filterRecord: (record) => record.lineUserId === event.lineUserId
  };
  const target = (await retrieve(params_1))[0]; //Retrieve returns an array

  // Use aging member id get next class: time > (current time - 0.5hr) && earliest
  const params_2 = {
    base: base,
    sheet: '課程',
    processRecord: (record) => ({
      "memberId": record.fields.學員[0],
      "classId": record.fields.編號,
      "classTime": moment(record.fields.日期時間),
      "classLocation": record.fields.地點,
      "classTrainer": record.fields.教練1[0] //TODO: deal with no content yet
    }),
    filterRecord: (record) => record.memberId === target.memberId,
    reduceRecord: (acc, record) => 
      record.classTime.isAfter(moment().subtract(0.5, 'hours')) && record.classTime.isBefore(acc.classTime) ?
      record : acc,
    reduceDefault: { "classTime": moment().add(100, 'years') }
  };
  // When no entry matches, retrieveReduce returned `reduceDefault`
  let nextClass = await retrieveReduce(params_2);

  // Post processing
  if (has(nextClass, 'memberId') && nextClass.classTime.isAfter(moment().subtract(0.5, 'hours'))) {
    //Return time in local format
    nextClass.classTime = nextClass.classTime.tz('Asia/Taipei').format();

    // Get trainer info
    const params_3 = {
      base: base,
      sheet: '教練',
      recordId: nextClass.classTrainer
    };
    nextClass.classTrainer = (await find(params_3)).fields.稱呼;
  } else {
    // Replace `nextClass` with null when no match
    nextClass = null;
  }

  console.log(nextClass);
  return { Status: 'handle_nextClass: OK', Data: nextClass };
};

async function handle_homework(event) {
  if(event.eventType !== AIR_EVENT_TYPES.HOMEWORK) { return; }
  const memberId = await retrieveMemberIdByLineId(base, event.lineUserId);
  
  // TODO: Get only today's record
  const params_1 = {
    base: base,
    sheet: '回家作業',
    processRecord: (record) => ({
      "hwId": record.fields.編號,
      "memberId": record.fields.學員[0],
      "hwDate": record.fields.日期,
      "baseMoveId": record.fields.課程記錄_基本菜單[0],
      "noOfSet": record.fields.幾組,
      "personalTip": record.fields.課程記錄_個人化提醒 && record.fields.課程記錄_個人化提醒[0],
      "image": record.fields.課程記錄_圖片 && record.fields.課程記錄_圖片[0].thumbnails.large.url,
      "video": record.fields.課程記錄_影片 && record.fields.課程記錄_影片[0],
      "isFinished": record.fields.完成 ? true : false
    }),
    filterRecord: (record) => record.memberId === memberId
  };
  let homeworks = await retrieve(params_1);

  // Replace memberId and baseMoveId by member and baseMove names
  let promises = homeworks.map(async (homework) => {
    const params_2 = {
      base: base,
      sheet: '學員',
      recordId: homework.memberId
    };
    homework.member = (await find(params_2)).fields.稱呼;

    const params_3 = {
      base: base,
      sheet: '基本菜單',
      recordId: homework.baseMoveId
    };
    homework.baseMove = (await find(params_3)).fields.名稱;

    // Removing ids for saving bandwidth
    delete homework.memberId;
    delete homework.baseMoveId;

    return homework;
  });
  homeworks = await Promise.all(promises);

  console.log(homeworks);
  return { Status: 'handle_homework: OK', Data: homeworks };
}


//-- Main handler
// TODO: remove the awkward list results
function handlerBuilder(...funcs) {
  return async (event, context) => {
    // Concurrent fire all handlers
    let promises = funcs.map((func) => func(event));
    let results = filterUndefined(await Promise.all(promises));

    // Res with an array with all activated handlers
    console.log(results)
    return results;
  };
}

exports.handler = handlerBuilder(
  handle_follow,
  handle_reminder,
  handle_nextClass,
  handle_homework
);
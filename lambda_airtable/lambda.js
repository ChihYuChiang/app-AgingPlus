const Airtable = require("airtable");
const moment = require('moment-timezone');
const has = require('lodash/has');
const { retrieve, retrieveReduce, create, find, update } = require('./operation.js');
const { retrieveMemberIidByLineId, isLineAdmin } = require('./operation-sp.js');
const { filterUndefined } = require('./util');


// -- Setup
const base = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
const AIR_EVENT_TYPES = {
  FOLLOW: 'follow',
  REMINDER: 'reminder',
  NEXT_CLASS: 'next_class',
  HOMEWORK: 'homework',
  FINISH_HOMEWORK: 'finish_homework',
  CLASS_HISTORY: 'class_history',
  CLASS_RECORD: 'class_record',
  EMPTY: 'empty'
};


// -- Handler middlewares
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

  await create(params);
  return { Status: 'handle_follow: OK' };
}


async function handle_reminder(event) {
  // Only Line admin can send reminder
  if(event.eventType !== AIR_EVENT_TYPES.REMINDER ||
    !(await isLineAdmin(base, event.lineUserId))) { return; }

  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    processRecord: (record) => ({
      "iid": record.id,  // Iid, internal id used by Airtable
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
}


// TODO: Identify the required fields in Air
async function handle_nextClass(event) {
  if(event.eventType !== AIR_EVENT_TYPES.NEXT_CLASS) { return; }
  const memberIid = await retrieveMemberIidByLineId(base, event.lineUserId);

  // Use aging member iid get next class: time > (current time - 0.5hr) && earliest
  const params_1 = {
    base: base,
    sheet: '課程',
    processRecord: (record) => ({
      "memberIid": record.fields.學員[0],
      "classId": record.fields.編號,
      "classTime": moment(record.fields.日期時間),
      "classLocation": record.fields.地點,
      "classTrainerIid": record.fields.教練1 && record.fields.教練1[0]
    }),
    filterRecord: (record) => record.memberIid === memberIid,
    reduceRecord: (acc, record) => 
      record.classTime.isAfter(moment().subtract(0.5, 'hours')) && record.classTime.isBefore(acc.classTime) ?
      record : acc,
    reduceDefault: { "classTime": moment().add(100, 'years') }
  };
  // `reduceDefault` prevents error when no entry returned
  let nextClass = await retrieveReduce(params_1);

  // Post processing
  if (has(nextClass, 'memberIid') && nextClass.classTime.isAfter(moment().subtract(0.5, 'hours'))) {
    // Return time in local format
    nextClass.classTime = nextClass.classTime.tz('Asia/Taipei').format('MMDD HH:mm');

    // Get trainer info
    const params_2 = {
      base: base,
      sheet: '教練',
      recordId: nextClass.classTrainerIid
    };
    nextClass.classTrainer = (await find(params_2)).fields.稱呼;

    // Removing ids for saving bandwidth
    delete nextClass.classTrainerIid;

  } else {
    // Replace `nextClass` with null when no match
    nextClass = null;
  }

  console.log(nextClass);
  return { Status: 'handle_nextClass: OK', Data: nextClass };
}


async function handle_homework(event) {
  if(event.eventType !== AIR_EVENT_TYPES.HOMEWORK) { return; }
  const memberIid = await retrieveMemberIidByLineId(base, event.lineUserId);
  
  const params_1 = {
    base: base,
    sheet: '回家作業',
    processRecord: (record) => ({
      "hwIid": record.id,
      "memberIid": record.fields.學員[0],
      "hwDate": record.fields.日期,
      "baseMoveIid": record.fields.課程記錄_基本菜單[0],
      "noOfSet": record.fields.幾組,
      "personalTip": record.fields.課程記錄_個人化提醒 && record.fields.課程記錄_個人化提醒[0],
      "image": record.fields.課程記錄_圖片 && record.fields.課程記錄_圖片[0].thumbnails.large.url,
      "video": record.fields.課程記錄_影片 && record.fields.課程記錄_影片[0],
      "isFinished": record.fields.完成 ? true : false
    }),
    filterRecord: (record) => (
      record.memberIid === memberIid &&
      moment(record.hwDate).isSame(moment(), 'day')  // Is today's hw
    )
  };
  let homeworks = await retrieve(params_1);

  // Replace memberIid and baseMoveIid by member and baseMove names
  let promises = homeworks.map(async (homework) => {
    const params_2 = {
      base: base,
      sheet: '學員',
      recordId: homework.memberIid
    };
    homework.member = (await find(params_2)).fields.稱呼;

    const params_3 = {
      base: base,
      sheet: '基本菜單',
      recordId: homework.baseMoveIid
    };
    homework.baseMove = (await find(params_3)).fields.名稱;

    // Removing ids for saving bandwidth
    delete homework.memberIid;
    delete homework.baseMoveIid;
    delete homework.hwDate;

    return homework;
  });
  homeworks = await Promise.all(promises);

  console.log(homeworks);
  return { Status: 'handle_homework: OK', Data: homeworks };
}


async function handle_finishHomework(event) {
  if(event.eventType !== AIR_EVENT_TYPES.FINISH_HOMEWORK) { return; }
  
  const params = {
    base: base,
    sheet: '回家作業',
    entries: [{
      "id": event.hwIid,
      "fields": {
        "完成": true,
      }
    }]
  };

  await update(params);
  return { Status: 'handle_finishHomework: OK' };
}


async function handle_classHistory(event) {
  if(event.eventType !== AIR_EVENT_TYPES.CLASS_HISTORY) { return; }
  const memberIid = await retrieveMemberIidByLineId(base, event.lineUserId);

  // Use aging member iid get passed classes: max 5 by time && 完成 && < now - 1hr
  const params_1 = {
    base: base,
    sheet: '課程',
    processRecord: (record) => ({
      "memberIid": record.fields.學員[0],
      "classIid": record.id,
      "classTime": moment(record.fields.日期時間),
      "classLocation": record.fields.地點,
      "classTrainerIid": record.fields.教練1 && record.fields.教練1[0],
      "attendance": record.fields.出席狀態
    }),
    filterRecord: (record) =>
      record.memberIid === memberIid &&
      record.attendance === "完成",
    reduceRecord: (acc, record) => {
      if (record.classTime.isBefore(moment().subtract(1, 'hours')) &&
      record.classTime.isAfter(acc.slice(-1)[0].classTime)) {  // If more recent than the min
        acc.pop();  // Remove the last
        acc.push(record);

        // Sort from the most recent (0) to the most distant past (-1)
        return acc.sort((a, b) => a.classTime.isAfter(b.classTime) ? -1 : 1);
      } else {
        return acc;
      }
    },
    reduceDefault: Array(5).fill({ "classTime": moment().subtract(100, 'years') })
  };
  const lastFewClasses = await retrieveReduce(params_1);


  // Post processing
  let classHistory_promises = lastFewClasses.map(async (pastClass) => {
    if (has(pastClass, 'memberIid')) {
      // Return time in local format
      const classDateTime = pastClass.classTime.tz('Asia/Taipei');
      pastClass.classTime = classDateTime.format("HHmm");
      pastClass.classDate = classDateTime.format("YYYYMMDD");

      // Get trainer info
      const params_2 = {
        base: base,
        sheet: '教練',
        recordId: pastClass.classTrainerIid
      };
      pastClass.classTrainer = (await find(params_2)).fields.稱呼;
  
      // Removing unnecessary for saving bandwidth
      delete pastClass.memberIid;
      delete pastClass.classTrainerIid;
      delete pastClass.attendance;

      return pastClass;
  
    } else {
      // Replace with null when not satisfy
      return null;
    }
  });
  let classHistory = filterUndefined(await Promise.all(classHistory_promises));

  console.log(classHistory);
  return { Status: 'handle_classHistory: OK', Data: classHistory };
}


async function handle_classRecord(event) {
  if(event.eventType !== AIR_EVENT_TYPES.CLASS_RECORD) { return; }
  
  // Use class iid get target class records
  const params_1 = {
    base: base,
    sheet: '課程記錄',
    filterRecordByFormula: "NOT({課程} = '')",
    processRecord: (record) => ({
      "classIid": record.fields.課程 && record.fields.課程[0],
      "baseMoveIid": record.fields.基本菜單 && record.fields.基本菜單[0],
      "performanceRec": record.fields.實做記錄,
      "image": record.fields.圖片 && record.fields.圖片[0].thumbnails.large.url,
      "video": record.fields.影片,
    }),
    filterRecord: (record) => record.classIid === event.classIid
  };
  const rawRecords = await retrieve(params_1);

  // Post processing
  let classRecords_promises = rawRecords.map(async (record) => {
    // Get baseMove info
    const params_2 = {
      base: base,
      sheet: '基本菜單',
      recordId: record.baseMoveIid
    };
    record.baseMove = (await find(params_2)).fields.名稱;

    // Removing unnecessary for saving bandwidth
    delete record.classIid;
    delete record.baseMoveIid;

    return record;
  });
  let classRecords = filterUndefined(await Promise.all(classRecords_promises));

  console.log(classRecords);
  return { Status: 'handle_classRecord: OK', Data: classRecords };
}


// -- Main handler
function handlerBuilder(...funcs) {
  return async (event, context) => {
    // Concurrent fire all handlers; make it sequential when needed
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
  handle_homework,
  handle_finishHomework,
  handle_classHistory,
  handle_classRecord
);
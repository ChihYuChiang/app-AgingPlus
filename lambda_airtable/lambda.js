const moment = require('moment-timezone');
const has = require('lodash/has');
const { retrieve, retrieveReduce, create, find, update } = require('./operation.js');
const { retrieveMemberIidByLineId, isLineAdmin } = require('./operation-sp.js');
const { filterUndefined, AIR_SHEETS } = require('./util');


// -- Setup
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
  if (event.eventType !== AIR_EVENT_TYPES.FOLLOW) { return; }

  const { lineUserId, lineDisplayName, lineProfilePic } = event;
  const FIELD_NAMES = AIR_SHEETS.LINE_MEMBER.FIELD_NAMES;
  const params = {
    sheet: AIR_SHEETS.LINE_MEMBER.NAME,
    entries: [{
      "fields": {
        [FIELD_NAMES.LINE_USER_ID]: lineUserId,
        [FIELD_NAMES.LINE_DISPLAY_NAME]: lineDisplayName,
        [FIELD_NAMES.LINE_PROFILE_PIC]: lineProfilePic
      }
    }]
  };

  await create(params);
  return { Status: 'handle_follow: OK' };
}


async function handle_reminder(event) {
  // Only Line admin can send reminder
  if (event.eventType !== AIR_EVENT_TYPES.REMINDER ||
    !(await isLineAdmin(event.lineUserId))) { return; }

  const FIELD_NAMES = AIR_SHEETS.LINE_MEMBER.FIELD_NAMES;
  const params = {
    sheet: AIR_SHEETS.LINE_MEMBER.NAME,
    processRecord: (record) => ({
      "iid": record.id,  // Iid, internal id used by Airtable
      "lineUserId": record.fields[FIELD_NAMES.LINE_USER_ID],
      "lineDisplayName": record.fields[FIELD_NAMES.LINE_DISPLAY_NAME],
      "messageTime": moment(record.fields[FIELD_NAMES.MSG_TIME]),
      "messageContent": record.fields[FIELD_NAMES.MSG_CONTENT]
    }),
    // If the scheduled message time is tomorrow
    filterRecord: (record) => moment().add(1, 'days').isSame(record.messageTime, 'day')
  };
  const targets = await retrieve(params);
  
  return { Status: 'handle_reminder: OK', Data: targets };
}


// TODO: Identify the required fields in Air
async function handle_nextClass(event) {
  if (event.eventType !== AIR_EVENT_TYPES.NEXT_CLASS) { return; }

  const memberIid = await retrieveMemberIidByLineId(event.lineUserId);
  const FIELD_NAMES = AIR_SHEETS.CLASS.FIELD_NAMES;
  
  // Use aging member iid get next class: time > (current time - 0.5hr) && earliest
  const params_1 = {
    sheet: AIR_SHEETS.CLASS.NAME,
    processRecord: (record) => ({
      "memberIid": record.fields[FIELD_NAMES.MEMBER_IID][0],
      "classId": record.fields[FIELD_NAMES.CLASS_ID],
      "classTime": moment(record.field[FIELD_NAMES.CLASS_TIME]),
      "classLocation": record.fields[FIELD_NAMES.CLASS_LOCATION],
      "classTrainerIid": record.fields[FIELD_NAMES.CLASS_TRAINER_IID] && record.fields[FIELD_NAMES.CLASS_TRAINER_IID][0]
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
      sheet: AIR_SHEETS.TRAINER.NAME,
      recordId: nextClass.classTrainerIid
    };
    nextClass.classTrainer = (await find(params_2)).fields[AIR_SHEETS.TRAINER.FIELD_NAMES.NICKNAME];

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
  if (event.eventType !== AIR_EVENT_TYPES.HOMEWORK) { return; }

  const memberIid = await retrieveMemberIidByLineId(event.lineUserId);
  const FIELD_NAMES = AIR_SHEETS.HOMEWORK.FIELD_NAMES;

  const params_1 = {
    sheet: AIR_SHEETS.HOMEWORK.NAME,
    processRecord: (record) => ({
      "hwIid": record.id,
      "memberIid": record.fields[FIELD_NAMES.MEMBER_IID][0],
      "hwDate": record.fields[FIELD_NAMES.HW_DATE],
      "baseMoveIid": record.fields[FIELD_NAMES.BASE_MOVE_IID][0],
      "noOfSet": record.fields[FIELD_NAMES.NO_OF_SET],
      "personalTip": record.fields[FIELD_NAMES.PERSONAL_TIP] && record.fields[FIELD_NAMES.PERSONAL_TIP][0],
      "image": record.fields[FIELD_NAMES.IMAGE] && record.fields[FIELD_NAMES.IMAGE][0].thumbnails.large.url,
      "video": record.fields[FIELD_NAMES.VIDEO] && record.fields[FIELD_NAMES.VIDEO][0],
      "isFinished": record.fields[FIELD_NAMES.IS_FINISHED] ? true : false
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
      sheet: AIR_SHEETS.MEMBER.NAME,
      recordId: homework.memberIid
    };
    homework.member = (await find(params_2)).fields[AIR_SHEETS.MEMBER.FIELD_NAMES.NICKNAME];

    const params_3 = {
      sheet: AIR_SHEETS.BASE_MOVE.NAME,
      recordId: homework.baseMoveIid
    };
    homework.baseMove = (await find(params_3)).fields[AIR_SHEETS.BASE_MOVE.FIELD_NAMES.NAME];

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
  if (event.eventType !== AIR_EVENT_TYPES.FINISH_HOMEWORK) { return; }
  
  const FIELD_NAMES = AIR_SHEETS.HOMEWORK.FIELD_NAMES;
  const params = {
    sheet: AIR_SHEETS.HOMEWORK.NAME,
    entries: [{
      "id": event.hwIid,
      "fields": {
        [FIELD_NAMES.IS_FINISHED]: true,
      }
    }]
  };

  await update(params);
  return { Status: 'handle_finishHomework: OK' };
}


async function handle_classHistory(event) {
  if (event.eventType !== AIR_EVENT_TYPES.CLASS_HISTORY) { return; }

  const memberIid = await retrieveMemberIidByLineId(event.lineUserId);
  const FIELD_NAMES = AIR_SHEETS.CLASS.FIELD_NAMES;

  // Use aging member iid get passed classes: max 5 by time && 完成 && < now - 1hr
  const params_1 = {
    sheet: AIR_SHEETS.CLASS.NAME,
    processRecord: (record) => ({
      "memberIid": record.fields[FIELD_NAMES.MEMBER_IID][0],
      "classIid": record.id,
      "classTime": moment(record.fields[FIELD_NAMES.CLASS_TIME]),
      "classLocation": record.fields[FIELD_NAMES.CLASS_LOCATION],
      "classTrainerIid": record.fields[FIELD_NAMES.CLASS_TRAINER_IID] && record.fields[FIELD_NAMES.CLASS_TRAINER_IID][0],
      "attendance": record.fields[FIELD_NAMES.ATTENDANCE]
    }),
    filterRecord: (record) =>
      record.memberIid === memberIid &&
      record.attendance === AIR_SHEETS.CLASS.OPTIONS.ATTENDANCE.COMPLETED,
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
        sheet: AIR_SHEETS.TRAINER.NAME,
        recordId: pastClass.classTrainerIid
      };
      pastClass.classTrainer = (await find(params_2)).fields[AIR_SHEETS.TRAINER.FIELD_NAMES.NICKNAME];
  
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
  if (event.eventType !== AIR_EVENT_TYPES.CLASS_RECORD) { return; }

  const FIELD_NAMES = AIR_SHEETS.CLASS_RECORD.FIELD_NAMES;
  
  // Use class iid get target class records
  const params_1 = {
    sheet: AIR_SHEETS.CLASS_RECORD.NAME,
    filterRecordByFormula: `NOT({${FIELD_NAMES.CLASS_IID}} = '')`,
    processRecord: (record) => ({
      "classIid": record.fields[FIELD_NAMES.CLASS_IID] && record.fields[FIELD_NAMES.CLASS_IID][0],
      "baseMoveIid": record.fields[FIELD_NAMES.BASE_MOVE_IID] && record.fields[FIELD_NAMES.BASE_MOVE_IID][0],
      "performanceRec": record.fields[FIELD_NAMES.PERFORMANCE_REC],
      "image": record.fields[FIELD_NAMES.IMAGE] && record.fields[FIELD_NAMES.IMAGE][0].thumbnails.large.url,
      "video": record.fields[FIELD_NAMES.VIDEO],
    }),
    filterRecord: (record) => record.classIid === event.classIid
  };
  const rawRecords = await retrieve(params_1);

  // Post processing
  let classRecords_promises = rawRecords.map(async (record) => {
    // Get baseMove info
    const params_2 = {
      sheet: AIR_SHEETS.BASE_MOVE.NAME,
      recordId: record.baseMoveIid
    };
    record.baseMove = (await find(params_2)).fields[AIR_SHEETS.BASE_MOVE.FIELD_NAMES.NAME];

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
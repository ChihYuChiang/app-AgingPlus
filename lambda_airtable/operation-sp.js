const { retrieve } = require('./operation.js');
const { Base, AIR_SHEETS } = require('./util');
let base = Base.getInstance();


// Get aging member iid by Line id
exports.retrieveMemberIidByLineId = async function(lineUserId) {
  const SHEET_NAME = AIR_SHEETS.LINE_MEMBER.NAME;
  const FIELD_NAMES = AIR_SHEETS.LINE_MEMBER.FIELD_NAMES;
  const params = {
    base: base,
    sheet: SHEET_NAME,
    processRecord: (record) => {
    return ({
      "lineUserId": record.fields[FIELD_NAMES.LINE_USER_ID],
      "lineDisplayName": record.fields[FIELD_NAMES.LINE_DISPLAY_NAME],
      "memberIid": record.fields[FIELD_NAMES.MEMBER_IID] && record.fields[FIELD_NAMES.MEMBER_IID][0]  // Get [0] if not null
    })},
    filterRecord: (record) => record.lineUserId === lineUserId
  };

  const memberIid = (await retrieve(params))[0].memberIid;  // Retrieve returns an array of records
  return memberIid;
};


// Check if is Line administrator
exports.isLineAdmin = async function(lineUserId) {
  const SHEET_NAME = AIR_SHEETS.LINE_MEMBER.NAME;
  const FIELD_NAMES = AIR_SHEETS.LINE_MEMBER.FIELD_NAMES;
  const params = {
    base: base,
    sheet: SHEET_NAME,
    processRecord: (record) => {
    return ({
      "lineUserId": record.fields[FIELD_NAMES.LINE_USER_ID],
      "isAdmin": record.fields[FIELD_NAMES.IS_ADMIN]
    })},
    filterRecord: (record) => record.lineUserId === lineUserId
  };

  const isAdmin = (await retrieve(params))[0].isAdmin;
  return isAdmin;
};
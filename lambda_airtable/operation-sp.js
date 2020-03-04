const { retrieve } = require('./operation.js');


// Get aging member iid by Line id
exports.retrieveMemberIidByLineId = async function(base, lineUserId) {
  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    processRecord: (record) => {
    return ({
      "lineUserId": record.fields.LineUserId,
      "lineDisplayName": record.fields.LineDisplayName,
      "memberIid": record.fields.學員 && record.fields.學員[0]  // Get [0] if not null
    })},
    filterRecord: (record) => record.lineUserId === lineUserId
  };

  const memberIid = (await retrieve(params))[0].memberIid;  // Retrieve returns an array of records
  return memberIid;
};
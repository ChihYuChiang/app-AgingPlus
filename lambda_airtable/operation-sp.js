const { retrieve } = require('./operation.js');


// Get aging member id by Line id
exports.retrieveMemberIdByLineId = async function(base, lineUserId) {
  const params = {
    base: base,
    sheet: 'LINE-MEMBER',
    processRecord: (record) => {
    return ({
      "lineUserId": record.fields.LineUserId,
      "lineDisplayName": record.fields.LineDisplayName,
      "memberId": record.fields.學員 && record.fields.學員[0]  // Get [0] if not null
    })},
    filterRecord: (record) => record.lineUserId === lineUserId
  };

  const memberId = (await retrieve(params))[0].memberId;  // Retrieve returns an array of records
  return memberId;
};
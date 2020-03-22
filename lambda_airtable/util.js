const Airtable = require("airtable");


class Sheet {
  constructor(_name, _fieldNames={}, _options={}) {
    this._name = _name;
    this._fieldNames = _fieldNames;
    this._options = _options;

    Object.freeze(this);
  }

  get NAME() {return this._name;}
  get FIELD_NAMES() {return this._fieldNames;}
  get OPTIONS() {return this._options;}
}


// Singleton
exports.Base = class {
  createInstance() {
    this._instance = new Airtable({ apiKey: process.env.AIRTABLE_APIKEY }).base(process.env.BASE_ID);
  }

  getInstance() {
    if (!this._instance) {
      this._instance = this.createInstance();
    }
    return this._instance;
  }
};


exports.AIR_SHEETS = {
  LINE_MEMBER: new Sheet('LINE-MEMBER', {
    LINE_USER_ID: 'LineUserId',
    LINE_DISPLAY_NAME: 'LineDisplayName',
    LINE_PROFILE_PIC: 'lineProfilePic',
    MSG_TIME: 'MessageTime',
    MSG_CONTENT: 'MessageContent',
    MEMBER_IID: '學員',
    IS_ADMIN: '管理員'
  }),

  MEMBER: new Sheet('學員', {
    NICKNAME: '稱呼'
  }),

  TRAINER: new Sheet('教練', {
    NICKNAME: '稱呼'
  }),

  BASE_MOVE: new Sheet('基本菜單', {
    NAME: '名稱'
  }),
  
  CLASS: new Sheet('課程', {
    MEMBER_IID: '學員',
    CLASS_ID: '編號',
    CLASS_TIME: '日期時間',
    CLASS_LOCATION: '地點',
    CLASS_TRAINER_IID: '教練1',
    ATTENDANCE: '出席狀態'
  }, {
    ATTENDANCE: {
      COMPLETED: '完成'
    }
  }),

  CLASS_RECORD: new Sheet('課程記錄', {
    CLASS_IID: '課程',
    BASE_MOVE_IID: '基本菜單',
    PERFORMANCE_REC: '實做記錄',
    IMAGE: '圖片',
    VIDEO: '影片'
  }),

  HOMEWORK: new Sheet('回家作業', {
    MEMBER_IID: '學員',
    HW_DATE: '日期',
    BASE_MOVE_IID: '課程記錄_基本菜單',
    NO_OF_SET: '幾組',
    PERSONAL_TIP: '課程記錄_個人化提醒',
    IMAGE: '課程記錄_圖片',
    VIDEO: '課程記錄_影片',
    IS_FINISHED: '完成'
  })
};


exports.sleepPromise = function(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
};


// Return obj removed `undefined` array elements or object attributes
exports.filterUndefined = function(obj) {
  if(Array.isArray(obj)) {
    return obj.filter((item) => typeof item !== 'undefined');
  }
  else {
    Object.keys(obj).forEach((key) => obj[key] === undefined && delete obj[key]);
  }
};

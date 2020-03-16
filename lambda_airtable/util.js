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
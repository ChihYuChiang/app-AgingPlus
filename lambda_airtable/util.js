exports.sleepPromise = function(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

exports.filterUndefined = function(ar) {
  return ar.filter((item) => typeof item !== 'undefined');
};
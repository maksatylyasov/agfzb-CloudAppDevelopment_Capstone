/**
 * Get all dealerships
 */
//create app custom part
var express = require("express");
var app = express();

const { CloudantV1 } = require("@ibm-cloud/cloudant");
const { IamAuthenticator } = require("ibm-cloud-sdk-core");

function main(params) {
  const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY });
  const cloudant = CloudantV1.newInstance({
    authenticator: authenticator,
  });
  cloudant.setServiceUrl(params.COUCH_URL);

  let dbListPromise = getDbs(cloudant);
  return dbListPromise;
}

function getDbs(cloudant) {
  return new Promise((resolve, reject) => {
    cloudant
      .getAllDbs()
      .then((body) => {
        resolve({ dbs: body.result });
      })
      .catch((err) => {
        console.log(err);
        reject({ err: err });
      });
  });
}

/*
 Sample implementation to get the records in a db based on a selector. If selector is empty, it returns all records. 
 eg: selector = {state:"Texas"} - Will return all records which has value 'Texas' in the column 'State'
 */
function getMatchingRecords(cloudant, dbname, selector) {
  return new Promise((resolve, reject) => {
    cloudant
      .postFind({ db: dbname, selector: selector })
      .then((result) => {
        resolve({ result: result.result.docs });
      })
      .catch((err) => {
        console.log(err);
        reject({ err: err });
      });
  });
}

/*
 Sample implementation to get all the records in a db.
 */
function getAllRecords(cloudant, dbname) {
  return new Promise((resolve, reject) => {
    cloudant
      .postAllDocs({ db: dbname, includeDocs: true, limit: 10 })
      .then((result) => {
        resolve({ result: result.result.rows });
      })
      .catch((err) => {
        console.log(err);
        reject({ err: err });
      });
  });
}

// Creating the endpoints

// 1. Get all the dealerships
app.get("/api/dealership", function (request, response) {
  // get all the cloudant data and display the result

  //prepare the data variables
  const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY });
  const cloudant = CloudantV1.newInstance({
    authenticator: authenticator,
  });
  cloudant.setServiceUrl(params.COUCH_URL);

  //get dealership data
  let db_dealers = getAllRecords(cloudant, "dealerships");

  return response.send(db_dealers);
});

app.post("/api/dealership/:state", function (request, response) {
  // get all the dealerships per state
  //prepare the data variables
  const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY });
  const cloudant = CloudantV1.newInstance({
    authenticator: authenticator,
  });
  cloudant.setServiceUrl(params.COUCH_URL);
  //get dealership data
  let matched_dealers = getMatchingRecords(cloudant, "dealerships", {
    state: "Texas",
  });
  response.render(matched_dealers);
});

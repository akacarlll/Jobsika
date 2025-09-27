// Google Apps Script code to manage a job application tracker spreadsheet.
// Disclaimer: The production scripts is currently still on Google Apps Script platform.
// This will be used by modifying the CI/CD pipeline.

function getOrCreateSpreadsheet(spreadsheetName) {
  let spreadsheet = null;

  try {
    // Check if a file with the given name exists in the root folder.
    const files = DriveApp.getFilesByName(spreadsheetName);
    if (files.hasNext()) {
      // If a file with the name exists, get its ID and open it.
      const file = files.next();
      spreadsheet = SpreadsheetApp.openById(file.getId());
    } else {

      spreadsheet = SpreadsheetApp.create(spreadsheetName);
    }
  } catch (e) {
    console.error("Error in getOrCreate function: " + e.toString());
  }

  return spreadsheet;
}


function getOrCreateSheet(spreadsheet, sheetName, rollingWindowSize) { 
  console.log("entering get or create sheet");
  let sheet = spreadsheet.getSheetByName(sheetName);

  // Static headers + Status
  const baseHeaders = [
    "Job Title",
    "Company",
    "Location",
    "URL",
    "Date Applied",
    "Salary",
    "Skills Required",
    "Contact Information",
    "Job Description",
    "Notes",
    "Status",
    "Number of Interview"
  ];

  // Add rolling window columns dynamically
  const rollingHeaders = [];
  if (rollingWindowSize && rollingWindowSize > 0) {
    for (let i = 1; i <= rollingWindowSize; i++) {
      rollingHeaders.push("Day -" + i);
    }
  }

  const headers = baseHeaders.concat(rollingHeaders);

  if (sheet === null) {
    // If the sheet doesn't exist, create it
    sheet = spreadsheet.insertSheet(sheetName);
    sheet.appendRow(headers);
    console.log("Sheet created with name: " + sheetName);

    // --- Add Data Validation for Status + Number of Interview ---
    const statusValues = [
      "Applied",
      "In Progress",
      "Interviewing",
      "Offer Received",
      "Accepted",
      "Rejected",
      "Withdrawn",
      "Paused",
      "Ignored",
      "Other"
    ];
    const numberInterviewsValues = [0,1,2,3,4,5,6,7,8,9,10];

    const statusRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(statusValues)
      .setAllowInvalid(false)
      .build();

    const numberInterviewsRule = SpreadsheetApp.newDataValidation()
      .requireValueInList(numberInterviewsValues)
      .setAllowInvalid(false)
      .build();

    // Apply validation to Status column
    const statusCol = baseHeaders.indexOf("Status") + 1; // 1-based index
    sheet.getRange(2, statusCol, sheet.getMaxRows() - 1).setDataValidation(statusRule);

    // Apply validation to Number of Interview column
    const interviewsCol = baseHeaders.indexOf("Number of Interview") + 1; // 1-based index
    sheet.getRange(2, interviewsCol, sheet.getMaxRows() - 1).setDataValidation(numberInterviewsRule);

  } else {
    console.log("Sheet found with name: " + sheetName);
  }

  return sheet;
}


function doPost(e) {
  console.log("Post request obtained")
  let mySpreadsheet = getOrCreateSpreadsheet("JobsikaTracker");
  console.log("Spreasheet got or created");
  const sheet = getOrCreateSheet(mySpreadsheet, "TestApplication");
  console.log("Sheets accessed");
  if (e){
    console.log(e)
    let data = JSON.parse(e.postData.contents);
    const rowData = [
      data.job_title || "",         // Job Title
      data.company_name || "",      // Company
      data.location || "",          // Location
      data.url || "",               // URL
      data.application_date || "",  // Date Applied
      data.salary || "",            // Salary
      data.required_skills || "",   // Skills Required
      data.contact_information || "", 
      data.job_description_summary || "", // Notes
      data.notes || "",
      "Applied",
      "0"
    ];
    console.log(rowData)
    sheet.appendRow(rowData);
  }


}
  
function doGet(e) {
  const files = DriveApp.getFilesByName("JobsikaTracker");
    if (files.hasNext()) {
      // If a file with the name exists, get its ID and open it.
      const file = files.next();
      spreadsheet = SpreadsheetApp.openById(file.getId());
    }
  var sheet = spreadsheet.getSheetByName("TestApplication");
  var data = sheet.getDataRange().getValues();

  // Example: convert to JSON
  var headers = data.shift();
  var jsonArray = data.map(function(row) {
    var obj = {};
    headers.forEach(function(header, i) {
      obj[header] = row[i];
    });
    return obj;
  });

  return ContentService.createTextOutput(
    JSON.stringify(jsonArray)
  ).setMimeType(ContentService.MimeType.JSON);
}

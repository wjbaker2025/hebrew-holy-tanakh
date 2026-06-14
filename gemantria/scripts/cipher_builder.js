var allCiphers = [];
var charArr = [];
capArr = [];
calcArr = [];
var ignArr = ["'", "`", "*"];
numArr = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
var defaultOrder = [];
backGemArr = [];
const baseArr = ["Ordinal", "Reverse", "Reduction", "Reverse Reduction"];
var shortArr = ["s;", "o;", "m;", "b;", "p;", "r;", "c;", "t;", "d;"];

function Load_Ciphers(impLanguage = calcLanguage) {
  //Queries the SQL database for Cipher data
  let resArr, tArr;
  let xhttp = new XMLHttpRequest();
  if (customOnly == true) {
    impLanguage = "custom";
  }

  xhttp.open(
    "GET",
    "tools/calculator-advanced/php/cipherdetails.php?lang=" + impLanguage,
  );
  xhttp.send();
  xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      //Split the returned text into smaller items in an array
      resArr = xhttp.responseText.split("|");
      charArr = Make_Numeric(resArr[0].split("_"));
      if (resArr[1] !== "") {
        capArr = Make_Numeric(resArr[1].split("_"));
      } else {
        capArr = [];
      }
      langCount = parseInt(resArr[2]);
      for (x = 3; x < resArr.length; x++) {
        //Split each item in the array into a smaller array and create a new cipher object, adding it to allCiphers
        tArr = resArr[x].split("-");
        allCiphers[allCiphers.length] = new cipher(
          tArr[0],
          tArr[1],
          tArr[2],
          tArr[3],
          tArr[4],
          tArr[5],
          tArr[6],
          tArr[7],
          tArr[8],
          tArr[9],
        );
        defaultOrder.push(tArr[0].replaceAll("_", " "));
      }
      Load_History();
    }
  };
}
class cipher {
  constructor(
    impName,
    impCat,
    impOn,
    impVals,
    capVals,
    impR,
    impG,
    impB,
    impShort,
    impChart,
  ) {
    //Sets default values based on the imported variables
    let x;

    this.Nickname = impName.replaceAll("_", " ");
    this.Category = impCat;
    this.RGB = [impR, impG, impB];
    this.vArr = impVals.split("_");
    if (capVals !== "") {
      this.vArr.push(...capVals.split("_"));
    }
    if (impOn == "1" || impOn == 1) {
      this.isOn = true;
    } else {
      this.isOn = false;
    }
    this.Shortcut = impShort;
    this.ChartAction = impChart;

    //If "Alphanumeric" is in the cipher name, set the cipher type as such
    if (this.Nickname.search("Alphanumeric") > -1) {
      this.cipherType = "alphanumeric";
    } else {
      this.cipherType = "reduction";
      for (x = 0; x < this.vArr.length; x++) {
        if (this.vArr[x] > 10 && ReduceNum(this.vArr[x], true, true) == false) {
          this.cipherType = "normal";
          break;
        }
      }
    }
    this.lastGem = 0;
    this.numSum = 0;
    this.gemTotal = 0;
  }
  //Returns the gematria in this cipher for an imported array of characters
  CalcGematria(impArr = calcArr, impSum) {
    let thisChar;
    this.lastGem = 0;
    this.numSum = 0;
    this.gemTotal = 0;

    //Cycle through each item in the imported array and increase the gematria total for each
    for (let x = 0; x < impArr.length; x++) {
      for (let y = 0; y < impArr[x].length; y++) {
        thisChar = impArr[x][y];
        if (String(thisChar).substring(0, 1) !== "#") {
          this.lastGem += parseInt(this.vArr[thisChar]);
        }
      }
    }

    //Add the numbers from the imported phrase to the gematria total
    this.numSum = impSum;
    this.gemTotal = this.lastGem + this.numSum;
    return this.gemTotal;
  }
  //Returns the values of each character in the imported array in another array. Two-dimensional arrays for multiple words
  GetBreakdown(impArr = calcArr) {
    let tempArr = [],
      expArr = [];
    let thisChar;

    for (let x = 0; x < impArr.length; x++) {
      for (let y = 0; y < impArr[x].length; y++) {
        thisChar = impArr[x][y];

        if (String(thisChar).substring(0, 1) == "#") {
          if (this.cipherType !== "alphanumeric") {
            tempArr.push(thisChar.substring(1));
          } else {
            for (let z = 1; z < thisChar.length; z++) {
              tempArr.push(thisChar.substring(z, z + 1));
            }
          }
        } else {
          tempArr.push(this.vArr[thisChar]);
        }
      }

      expArr.push(tempArr);
      tempArr = [];
    }

    return expArr;
  }
  //Returns a string formatted in the cipher's color
  GemString(
    impVal = this.gemTotal,
    impReduce = false,
    impHeaders = true,
    impLink = true,
  ) {
    let rStr =
      '<font style="color: RGB(' +
      this.RGB.join(", ") +
      ');"><div class="NumberClass">';
    let thisSpot = CipherSpot(this);

    if (impLink == false) {
      rStr += impVal + "</div>";
    } else if (impHeaders == true || thisSpot == breakCipher) {
      rStr +=
        '<b id="finalBreakNum" class="justnumber" onclick="javascript:Open_Properties(' +
        impVal +
        ')">' +
        impVal +
        "</b></div>";
    } else {
      rStr +=
        '<b class="justnumber" onclick="javascript:Change_Cipher(' +
        thisSpot +
        ', event)">' +
        impVal +
        "</b></div>";
    }

    if (impReduce == true) {
      rStr +=
        '<br><font style="font-size: 0.5em; font-weight:600;">' +
        ReduceNum(impVal) +
        "</font>";
    }
    rStr += "</font>";
    return rStr;
  }
  //Retrieve the stored RGB values
  RGB() {
    return this.RGB;
  }
  //Return the name of the cipher using the stored RGB values
  NameString(impParentheses = false) {
    let tStr;
    tStr = '<font style="color: RGB(' + this.RGB.join(", ") + ')">';
    if (impParentheses == true) {
      tStr += "(";
    }
    tStr += this.Nickname;
    if (impParentheses == true) {
      tStr += ")";
    }
    tStr += "</font>";
    return tStr;
  }
  //Returns the name of the cipher with a link to make it the highlighted one
  NameLink(impNum = CipherSpot(this), impClass) {
    let tStr;
    tStr =
      '<div class="' +
      impClass +
      '" onclick="javascript:MoveCipherClick(' +
      impNum +
      ', event)">';
    tStr +=
      '<font style="color: RGB(' +
      this.RGB.join(", ") +
      ')">' +
      this.Nickname +
      "</font></div>";
    return tStr;
  }
  //Returns HTML for a table containing a chart with the letters from impArr and the values from this.vArr
  GetChart() {
    let iText, tPass, rowLen, chartVersion;
    let add1, add2;
    let tempArr = [];

    //Cycle through each item in charArr and find the associated value in this.vArr
    for (let z = 0; z < langCount; z++) {
      add1 = String.fromCharCode(charArr[z]);
      add2 = Number(this.vArr[z]);
      tempArr.push({ add1, add2 });
    }

    chartVersion = this.cipherType;

    //If it's a capital letter cipher, continue the array for capital values
    if (Is_CapitalCipher(this.vArr)) {
      for (let q = 0; q < langCount; q++) {
        add1 = String.fromCharCode(capArr[q]);
        add2 = Number(this.vArr[q + charArr.length]);
        tempArr.push({ add1, add2 });
      }
      chartVersion = "normal";
    }

    if (this.ChartAction == "sort") {
      tempArr.sort(chartSorter);
    } else if (this.ChartAction == "reverse") {
      tempArr.reverse();
    }

    //If the cipher is a Reduction method, then simply display one row of letters and one of numbers
    iText = "<table><tr>";
    tPass = 1;
    switch (chartVersion) {
      case "reduction":
        do {
          if (tPass > 1) {
            iText += "</tr><tr>";
          }
          for (let x = 0; x < langCount; x++) {
            switch (tPass) {
              case 1:
                iText +=
                  '<td class="chartChar">' + tempArr[x]["add1"] + "</td>";
                break;
              case 2:
                iText += '<td class="chartVal">' + tempArr[x]["add2"] + "</td>";
                break;
            }
          }
          tPass++;
        } while (tPass < 3);

        rowLen = langCount;
        break;

      //If the cipher is normal, create a two-tiered table split in half
      case "normal":

      case "alphanumeric":
        //Add 0-9 to the displayed table if it is an alphanumeric cipher
        if (this.cipherType == "alphanumeric") {
          for (let q = 9; q > -1; q--) {
            add1 = q;
            add2 = q;
            tempArr.unshift({ add1, add2 });
          }
        }

        rowLen = Math.ceil(tempArr.length / 2);

        do {
          iText += "</tr><tr>";
          for (let x = 0; x < rowLen; x++) {
            switch (tPass) {
              case 1:
                iText +=
                  '<td class="chartChar">' + tempArr[x]["add1"] + "</td>";
                break;
              case 2:
                iText += '<td class="chartVal">' + tempArr[x]["add2"] + "</td>";
                break;
              case 3:
                if (x + rowLen < tempArr.length) {
                  iText +=
                    '<td class="chartChar">' +
                    tempArr[x + rowLen]["add1"] +
                    "</td>";
                }
                break;
              case 4:
                if (x + rowLen < tempArr.length) {
                  iText +=
                    '<td class="chartVal">' +
                    tempArr[x + rowLen]["add2"] +
                    "</td>";
                }
                break;
            }
          }
          tPass++;
        } while (tPass < 5);
        break;
    }

    iText +=
      '</tr><tr><td id="cipherChartTitle" colspan="' +
      rowLen +
      '"><span id="moveCipherUp" class="moveCipher" onclick="javascript:MoveCipher(undefined, 1)"><i class="fas fa-chevron-circle-up"></i></span>' +
      this.NameString() +
      ' <span id="moveCipherDown" class="moveCipher" onclick="javascript:MoveCipher(undefined, 2)"><i class="fas fa-chevron-circle-down"></i></span></td>';
    iText += "</tr></table>";
    return iText;
  }
}
function Calc_AllGem(impVal) {
  //impVal is the phrase being calculated
  let thisChar, charSpot, numToAdd, shortSpot;
  let tempArr = [];
  let numStr = "",
    realVal = "";
  calcArr = [];

  //Reverse impVal if Hebrew
  if (calcLanguage == "hebrew") {
    newVal = "";
    for (let z = impVal.length - 1; z > -1; z--) {
      thisChar = impVal.substring(z, z + 1);
      newVal += String(thisChar);
    }
    impVal = newVal;
  }

  if (impVal.length > 1) {
    shortSpot = shortArr.indexOf(impVal.substring(0, 2));
  } else {
    shortSpot = -1;
  }
  let didShortRun = false;

  //Check the first two characters to see if a keyboard shortcut is being used
  if (optArr.Shortcuts == true && shortSpot > -1) {
    let optText = impVal.substring(2, impVal.length);
    didShortRun = Run_Shortcut(optText, shortSpot);
    if (didShortRun == true) {
      impVal = EntryValue();
    } else {
      impVal = "";
    }
  }

  //Remove Diacritics if the option is on
  if (optArr.RemoveDiacritics) {
    impVal = impVal.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  //Cycle through each letter in the phrase
  for (let g = 0; g < impVal.length; g++) {
    thisChar = impVal.substring(g, g + 1);

    //If the character is a number, either add it to the temp array or create a number string based on options
    if (numArr.indexOf(thisChar) > -1) {
      switch (optArr.NumCalc) {
        case "Reduced":
          tempArr.push("#" + String(thisChar));
          break;
        case "Full":
        case "Smart":
          if (numStr == "") {
            numStr = String(thisChar);
          } else {
            numStr += String(thisChar);
          }
          break;
      }
    } else {
      //If not a number, add any running number strings to tempArr based on options
      if (numStr !== "") {
        if (optArr.NumCalc == "Full" || numStr.length < 4) {
          tempArr.push("#" + numStr);
        } else if (optArr.NumCalc == "Smart") {
          for (let q = 0; q < numStr.length; q++) {
            tempArr.push("#" + numStr.substring(q, q + 1));
          }
        }
        numStr = "";
      }

      thisChar = thisChar.charCodeAt(0);
      if (thisChar > 1450 && thisChar < 1488) {
        continue;
      }
      thisCharSpot = charArr.indexOf(thisChar);

      //If the character is being calculated, push it to the array
      if (thisCharSpot > -1) {
        tempArr.push(thisCharSpot);
      } else if (capArr.indexOf(thisChar) > -1) {
        tempArr.push(capArr.indexOf(thisChar) + charArr.length);
        //If the character is not in the array of Ignored items, treat it as a space
      } else if (ignArr.indexOf(String.fromCharCode(thisChar)) == -1) {
        if (tempArr.length > 0) {
          calcArr.push(tempArr);
          tempArr = [];
        }
      }
    }
  }

  //Once the loop is done, handle any remaining number strings. Code snipped from block above.
  if (numStr !== "") {
    if (tempArr.length > 0) {
      if (optArr.NumCalc == "Full" || numStr.length < 4) {
        tempArr.push("#" + numStr);
      } else if (optArr.NumCalc == "Smart") {
        for (let q = 0; q < numStr.length; q++) {
          tempArr.push("#" + numStr.substring(q, q + 1));
        }
      }
    } else {
      if (optArr.NumCalc == "Full" || numStr.length < 4) {
        calcArr.push(["#" + numStr]);
      } else if (optArr.NumCalc == "Smart") {
        for (let q = 0; q < numStr.length; q++) {
          tempArr.push("#" + numStr.substring(q, q + 1));
        }
      }
    }
    numStr = "";
  }
  //If there are items in tempArr, add it as the final word
  if (tempArr.length > 0) {
    calcArr.push(tempArr);
  }

  //SumCalcArr figures out the sum of the numbers in the phrase based on the user's options and/or cipher type
  let numArray = SumCalcArr();
  //Cycle through each cipher and calculate the gematria using calcArr
  for (let x = 0; x < allCiphers.length; x++) {
    if (
      optArr.NumCalc == "Reduced" ||
      allCiphers[x].cipherType == "alphanumeric"
    ) {
      numToAdd = numArray[0];
    } else if (optArr.NumCalc == "Full") {
      numToAdd = numArray[1];
    } else if (optArr.NumCalc == "Smart") {
      numToAdd = numArray[2];
    } else if (optArr.NumCalc == "Off") {
      numToAdd = 0;
    }

    //Run the gematria in each individual cipher
    allCiphers[x].CalcGematria(calcArr, numToAdd);
  }

  if (shortSpot == 1 && didShortRun == true) {
    return true;
  } else {
    return false;
  }
}
function HasDiacritic(impChar) {
  normChar = impChar.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  if (impChar === normChar) {
    return false;
  } else {
    return true;
  }
}
function SumCalcArr(impType, impArr = calcArr) {
  //This function takes all of the numbers in the entry field and adds them based on the user's options
  let nSum = 0;
  let redSum = 0,
    fullSum = 0,
    smartSum = 0;
  let redTotal = 0,
    fullTotal = 0,
    smartTotal = 0;

  for (let x = 0; x < impArr.length; x++) {
    for (let y = 0; y < impArr[x].length; y++) {
      thisChar = impArr[x][y];
      if (String(thisChar).substring(0, 1) == "#") {
        redSum = 0;
        fullSum = 0;
        smartSum = 0;

        for (let z = 1; z < thisChar.length; z++) {
          redSum += Number(thisChar.substring(z, z + 1));
        }
        fullSum += Number(thisChar.substring(1));

        if (thisChar.length > 4) {
          smartTotal += redSum;
        } else {
          smartTotal += fullSum;
        }
        redTotal += redSum;
        fullTotal += fullSum;
      }
    }
  }
  return [redTotal, fullTotal, smartTotal];
}
function CipherCount(impNum = 1) {
  //impNum 1 will return the total count of ciphers, impNum 2 will return the number of ciphers that are on
  let x;
  let onCount = 0;
  if (impNum == 1) {
    return allCiphers.length;
  } else if (impNum == 2) {
    for (x = 0; x < allCiphers.length; x++) {
      if (allCiphers[x].isOn == true) {
        onCount++;
      }
    }
    return onCount;
  }
}
function RestoreCipherSettings(impVal = 0) {
  if (calcLanguage !== "english") {
    return;
  }
  if (!optArr.CipherOrder) {
    return;
  }

  if (optArr.CipherOrder.length == 0 || optArr.CipherOrder[0] == "") {
    optArr.CipherOrder[0] = [
      "Ordinal",
      "Reduction",
      "Reverse",
      "Reverse Reduction",
    ];
    optArr.CipherSelection[0] = [1, 1, 1, 1];
  }

  let orderArr = optArr.CipherOrder[impVal];
  let onArr = optArr.CipherSelection[impVal];

  //Sorts allCiphers to match the order from impArr, which contains an array of cipher names
  let tempArr = [];

  for (let x = 0; x < orderArr.length; x++) {
    for (let y = 0; y < allCiphers.length; y++) {
      if (allCiphers[y].Nickname == orderArr[x]) {
        tempArr.push(allCiphers[y]);
        allCiphers.splice(y, 1);
        y--;
        break;
      }
    }
  }

  //Add any ciphers that weren't in the user's list to the end of the array
  for (let q = 0; q < allCiphers.length; q++) {
    tempArr.push(allCiphers[q]);
  }
  allCiphers = [];
  allCiphers = tempArr;

  //Cycle through each cipher
  for (let z = 0; z < allCiphers.length; z++) {
    if (z >= onArr.length) {
      allCiphers.isOn = false;
      //Set the cipher as "on" based on the imported array
    } else if (onArr[z] == 1) {
      allCiphers[z].isOn = true;
    } else {
      allCiphers[z].isOn = false;
    }
  }
  NewBreakCipher();
}
function ReduceNum(impNum, impBool = true, boolReturn = false) {
  //This function reduces impNum and returns it. impBool determines if Master Numbers are acceptable as Reduced numbers.
  //If boolReturn is true, then this function only returns true/false based on whether or not the number is already reduced.
  //Otherwise it will return the Reduced number
  let x, s;
  let cn = 0;
  let tempNum = impNum;
  while (tempNum > 9) {
    if (impBool == true) {
      if (impNum == 11 || impNum == 22 || impNum == 33) {
        return tempNum;
      }
    }
    cn = 0;
    for (x = 0; x < String(tempNum).length; x++) {
      s = Number(String(tempNum).slice(x, x + 1));
      cn += s;
    }
    tempNum = cn;
  }
  if (boolReturn == true) {
    if (tempNum == impNum) {
      return true;
    } else {
      return false;
    }
  } else {
    return tempNum;
  }
}
function chartSorter(a, b) {
  //Special sort function for the cipher's chart
  if (a["add2"] === b["add2"]) {
    return 0;
  } else {
    return a["add2"] < b["add2"] ? -1 : 1;
  }
}
function AllGemArr(impBool = false) {
  //Creates an array of all the values each cipher last calculated
  let x, addNum;
  let expArr = [];
  for (x = 0; x < allCiphers.length; x++) {
    addNum = parseInt(allCiphers[x].lastGem + allCiphers[x].numSum);
    if (impBool == true) {
      if (allCiphers[x].isOn == true) {
        expArr.push(addNum);
      } else {
        expArr.push("");
      }
    } else {
      expArr.push(addNum);
    }
  }
  return expArr;
}
function CharSpot(impNum) {
  //Small function for handling small/capital letters
  if (impNum > charArr.length - 1) {
    return capArr[impNum - charArr.length];
  } else {
    return charArr[impNum];
  }
}
function CipherSpot(impCipher, impName = "") {
  //Find the position of a cipher with the allCiphers array using the cipher or its name
  let searchFor;
  if (impName !== "") {
    searchFor = impName;
  } else {
    searchFor = impCipher.Nickname;
  }
  for (let x = 0; x < allCiphers.length; x++) {
    if (allCiphers[x].Nickname == searchFor) {
      return x;
    }
  }
  return -1;
}
function DefaultSpot(impCipher, impName = "") {
  //Find the position of a cipher with the defaultOrder array using the cipher or its name
  let searchFor;
  if (impName !== "") {
    searchFor = impName;
  } else {
    searchFor = impCipher.Nickname;
  }
  for (let x = 0; x < defaultOrder.length; x++) {
    if (defaultOrder[x] == searchFor) {
      return x;
    }
  }
  return -1;
}
function Run_Shortcut(impVal, impSpot) {
  //If a shortcut has been entered, Re-build the Breakdown and Gematria Table so they empty out
  Build_Breakdown();
  Populate_GemTable(false);
  let didCalc = false;

  switch (impSpot) {
    //For "s;" shortcut that toggles ciphers on/off
    case 0:
      if (impVal == "base") {
        Set_BaseCiphers();
        LoadTop();
        didCalc = true;
      } else {
        for (let x = 0; x < allCiphers.length; x++) {
          if (allCiphers[x].Shortcut == impVal) {
            Toggle_Cipher(x);
            LoadTop();
            didCalc = true;
          }
        }
      }
      break;
    //For "o;" shortcut that turns all cipher but one off
    case 1:
      for (let x = 0; x < allCiphers.length; x++) {
        if (allCiphers[x].Shortcut == impVal) {
          Only_Cipher(x);
          LoadTop();
          didCalc = true;
        }
      }
      break;
    //For "m;" shortcut that moves a cipher up or down in the table
    case 2:
      if (impVal.toLowerCase() == "u") {
        MoveCipher(breakCipher, 1);
        LoadTop();
        didCalc = true;
      } else if (impVal.toLowerCase() == "d") {
        MoveCipher(breakCipher, 2);
        LoadTop();
        didCalc = true;
      }
      break;
    //For "b;" shortcut that restores the previous ciphers
    case 3:
      if (CipherCount(2) == 1 && backGemArr.length > 0) {
        Back_Ciphers();
        LoadTop();
        didCalc = true;
      }
      break;
    //For "p;" shortcut that restores a user's Preset
    case 4:
      if (isNaN(impVal) == false && impVal > 0 && impVal < 5) {
        Load_Preset(impVal);
        LoadTop();
        didCalc = true;
      } else if (impVal == "d") {
        Load_Preset(0);
        LoadTop();
        didCalc = true;
      }
      break;
    //For "r;" shortcut, change the number of ciphers per row
    case 5:
      if (isNaN(impVal) == false && impVal > 1 && impVal < 9) {
        optArr.PerRow = impVal;
        Build_GemTable();
        LoadTop();
        didCalc = true;
      }
      break;
    //For "c;" shortcut, change the active cipher
    case 6:
      for (let x = 0; x < allCiphers.length; x++) {
        if (allCiphers[x].Shortcut == impVal) {
          if (allCiphers[x].isOn == true) {
            Change_Cipher(x);
            LoadTop();
            didCalc = true;
          } else {
            Toggle_Cipher(x);
            LoadTop();
            didCalc = true;
          }
        }
      }
      break;
    //For "t;" shortcut, change the active history table
    case 7:
      if (TablesEnabled == true && impVal > 0 && impVal <= userHistory.length) {
        Change_History(impVal - 1);
        LoadTop();
        didCalc = true;
      } else if (HistoryEnabled == true && impVal == "h") {
        Change_History(userHistory.length - 2);
        LoadTop();
        didCalc = true;
      } else if (impVal == "s") {
        Change_History(userHistory.length - 1);
        LoadTop();
        didCalc = true;
      }
      break;
    //For "d;" shortcut, change Display options
    case 8:
      if (impVal == "b") {
        ToggleBreakdown();
        LoadTop();
        didCalc = true;
      } else if (impVal == "base") {
        Set_BaseCiphers();
        LoadTop();
        didCalc = true;
      } else if (impVal == "c") {
        ToggleGemChart();
        LoadTop();
        didCalc = true;
      } else if (impVal == "n") {
        if (optArr.Headers) {
          optArr.Headers = false;
        } else {
          optArr.Headers = true;
        }
        Build_GemTable();
        LoadTop();
        didCalc = true;
      } else if (impVal == "s") {
        if (optArr.ShowSimple) {
          optArr.ShowSimple = false;
        } else {
          optArr.ShowSimple = true;
        }
        Build_Breakdown();
        LoadTop();
        didCalc = true;
      } else if (impVal == "r") {
        if (optArr.Reduce) {
          optArr.Reduce = false;
        } else {
          optArr.Reduce = true;
        }
        Build_GemTable();
        LoadTop();
        didCalc = true;
      } else if (impVal == "l" || impVal == "w") {
        if (optArr.LetterCount) {
          optArr.LetterCount = false;
        } else {
          optArr.LetterCount = true;
        }
        Build_Breakdown();
        LoadTop();
        didCalc = true;
      }
      break;
  }
  return didCalc;
}
function Change_Cipher(impNum) {
  //Set the Breakdown Cipher and rebuild the Gematria Table and Chart
  if (breakCipher == impNum) {
    return;
  }
  breakCipher = impNum;
  Populate_GemTable();
  Build_Breakdown(true);
  Build_GemChart(breakCipher);
}
function MoveCipher(impNum = breakCipher, impType) {
  //impNum is the position of the cipher being moved, impType 1 to move up and 2 to move down
  let x, y;
  let wasSuccess = false;
  let saveCipher = allCiphers[impNum];

  allCiphers.splice(impNum, 1);

  switch (impType) {
    case 1:
      for (x = impNum - 1; x > -1; x--) {
        if (allCiphers[x].isOn == true) {
          allCiphers.splice(x, 0, saveCipher);
          breakCipher = x;
          UpdateOnArr();
          wasSuccess = true;
          break;
        }
      }
      if (wasSuccess == false) {
        allCiphers.splice(impNum, 0, saveCipher);
        breakCipher = impNum;
      }
      break;
    case 2:
      for (x = impNum; x < allCiphers.length; x++) {
        if (allCiphers[x].isOn == true) {
          allCiphers.splice(x + 1, 0, saveCipher);
          breakCipher = x + 1;
          UpdateOnArr();
          wasSuccess = true;
          break;
        }
      }
      if (wasSuccess == false) {
        allCiphers.splice(impNum, 0, saveCipher);
        breakCipher = impNum;
      }
      break;
    case 3:
      y = impNum;
      for (x = impNum - 1; x > -1; x--) {
        if (allCiphers[x].isOn == true) {
          y = x;
        }
      }
      allCiphers.splice(y, 0, saveCipher);
      breakCipher = y;
      break;
    case 4:
      y = impNum;
      for (x = impNum; x < allCiphers.length; x++) {
        if (allCiphers[x].isOn == true) {
          y = x + 1;
        }
      }
      if (y > allCiphers.length - 1) {
        y--;
      }
      allCiphers.splice(y, 0, saveCipher);
      breakCipher = y;
      break;
  }

  Build_GemTable();
}
function MoveCipherClick(impNum = breakCipher, impEvent) {
  if (impEvent.ctrlKey) {
    if (impEvent.altKey) {
      Toggle_Cipher(impNum);
    } else if (impEvent.shiftKey) {
      MoveCipher(impNum, 3);
    } else {
      MoveCipher(impNum, 1);
    }
  } else if (impEvent.altKey) {
    if (impEvent.shiftKey) {
      MoveCipher(impNum, 4);
    } else {
      MoveCipher(impNum, 2);
    }
  } else {
    Change_Cipher(impNum);
  }
}
function Toggle_Cipher(impNum) {
  //Toggles a cipher on or off
  let x;
  let newFound = false;

  if (allCiphers[impNum].isOn == true) {
    allCiphers[impNum].isOn = false;
    Build_GemTable();
    NewBreakCipher(impNum);
  } else {
    allCiphers[impNum].isOn = true;
    Build_GemTable();
    Change_Cipher(impNum);
  }
}
function Set_BaseCiphers() {
  for (let x = 0; x < allCiphers.length; x++) {
    if (baseArr.includes(allCiphers[x].Nickname)) {
      allCiphers[x].isOn = true;
      if (baseArr.indexOf(allCiphers[x].Nickname) == 0) {
        outBreak = x;
      }
    } else {
      allCiphers[x].isOn = false;
    }
  }
  NewBreakCipher();
  Build_GemTable();
  return outBreak;
}
function Only_Cipher(impNum) {
  //Turn all ciphers off, except for the one imported via impNum
  let cCount = CipherCount(2);
  if (cCount > 1) {
    backGemArr = [];
  }

  for (let x = 0; x < allCiphers.length; x++) {
    if (cCount > 1 && allCiphers[x].isOn == true) {
      backGemArr.push(x);
    }
    if (x == impNum) {
      allCiphers[x].isOn = true;
    } else {
      allCiphers[x].isOn = false;
    }
  }
  //Rebuild the Gematria Table and Change the selected cipher
  Build_GemTable();
  Change_Cipher(impNum);
}
function Back_Ciphers() {
  //This function restores the Gematria table back to its original state from prior to running the "only" shortcut
  for (let x = 0; x < allCiphers.length; x++) {
    if (backGemArr.indexOf(x) > -1) {
      allCiphers[x].isOn = true;
    } else {
      allCiphers[x].isOn = false;
    }
  }
  //Empty the saved array and select a new cipher if the highlighted one wasn't originally there
  backGemArr = [];
  if (allCiphers[breakCipher].isOn == false) {
    NewBreakCipher(1);
  }
  //Rebuild the gematria table
  Build_GemTable();
}
function NewBreakCipher(impNum = breakCipher) {
  //This function figures out which cipher to highlight for the Breakdown if the active one is closed
  let x;
  let newFound = false;

  //Cycle through the ciphers before the old one and highlight the first one that's on
  for (x = impNum; x > -1; x--) {
    if (allCiphers[x].isOn == true) {
      Change_Cipher(x);
      newFound = true;
      break;
    }
  }
  //If none of those were on, cycle through the ones after it and find the first one that is
  if (newFound == false) {
    for (x = impNum + 1; x < allCiphers.length; x++) {
      if (allCiphers[x].isOn == true) {
        Change_Cipher(x);
        newFound = true;
        break;
      }
    }
  }
}
//This is a special function that figures out if cipher matches are relevant to the strength or not
function isMatchOK(impCipher1, impCipher2, impPhrase1, impPhrase2) {
  switch (impCipher1.Nickname) {
    case "Sumerian":
      switch (impCipher2.Nickname) {
        case "Sumerian":
          if (allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true) {
            return false;
          }
          break;
        case "Reverse Sumerian":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Reverse Sumerian":
      switch (impCipher2.Nickname) {
        case "Reverse Sumerian":
          if (allCiphers[CipherSpot(undefined, "Reverse")].isOn == true) {
            return false;
          }
          break;
        case "Sumerian":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Capitals Added":
      switch (impCipher2.Nickname) {
        case "Capitals Added":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Reverse Caps Added":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Capitals Mixed":
      switch (impCipher2.Nickname) {
        case "Capitals Mixed":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Reverse Caps Mixed":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Reverse Caps Added":
      switch (impCipher2.Nickname) {
        case "Reverse Caps Added":
          if (
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Capitals Added":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Reverse Caps Mixed":
      switch (impCipher2.Nickname) {
        case "Reverse Caps Mixed":
          if (
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Capitals Mixed":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Satanic":
      switch (impCipher2.Nickname) {
        case "Satanic":
          if (
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Reverse Satanic":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
    case "Reverse Satanic":
      switch (impCipher2.Nickname) {
        case "Reverse Satanic":
          if (
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
        case "Satanic":
          if (
            allCiphers[CipherSpot(undefined, "Ordinal")].isOn == true &&
            allCiphers[CipherSpot(undefined, "Reverse")].isOn == true &&
            SameCharCount(impPhrase1, impPhrase2) == true
          ) {
            return false;
          }
          break;
      }
      break;
  }
  return true;
}
function SameCharCount(impVal1, impVal2) {
  //Cycles through both imported arrays and returns true/false based on whether or not they have the same number of letters/
  //Used in accordance with isMatchOK function
  let thisChar;
  let cCount = 0,
    cCount2 = 0;
  for (let x = 0; x < impVal1.length; x++) {
    let thisChar = impVal1.substring(x, x + 1);
    if (charArr.indexOf(thisChar) || capArr.indexOf(thisChar)) {
      cCount++;
    }
  }
  for (let y = 0; y < impVal2.length; y++) {
    thisChar = impVal2.substring(y, y + 1);
    if (charArr.indexOf(thisChar) > -1 || capArr.indexOf(thisChar) > -1) {
      cCount2++;
    }
  }
  if (cCount == cCount2) {
    return true;
  } else {
    return false;
  }
}
function Is_CapitalCipher(impArr) {
  let z = 0;
  if (capArr.length == 0) {
    return false;
  }

  for (let x = charArr.length; z < langCount; x++) {
    if (impArr[x] !== impArr[z]) {
      return true;
    } else {
      z++;
    }
  }

  return false;
}

function Get_CipherOrder(impBool = false) {
  //Returns a text string of cipher names in the order the user has them stored.
  //If impBool is true, only return the ciphers that are on
  let expArr = [],
    ciphText = "";

  if (impBool == false) {
    for (let x = 0; x < optArr.CipherOrder.length; x++) {
      ciphText = "";
      thisOrder = optArr.CipherOrder[x];

      for (let y = 0; y < thisOrder.length; y++) {
        if (y > 0) {
          ciphText += "|";
        }
        ciphText += thisOrder[y];
      }

      expArr.push(ciphText);
    }
  } else {
    for (let x = 0; x < allCiphers.length; x++) {
      thisCipher = allCiphers[x];

      if (thisCipher.isOn == true) {
        expArr.push(thisCipher.Nickname);
      }
    }
  }

  return expArr.join("%%%");
}

function Get_CiphersOn() {
  //Returns a text string of 1's and 0's based on whether or not the cipher is turned on
  let expArr = [],
    selText = "";

  for (let x = 0; x < optArr.CipherSelection.length; x++) {
    selText = "";
    thisSel = optArr.CipherSelection[x];

    for (let y = 0; y < thisSel.length; y++) {
      if (y > 0) {
        selText += "|";
      }
      selText += thisSel[y];
    }

    expArr.push(selText);
  }

  return expArr.join("%%%");
}
function MatchCipherOrder() {
  let cNames = [];
  cOn = [];

  for (let x = 0; x < allCiphers.length; x++) {
    cNames.push(allCiphers[x].Nickname);
    if (allCiphers[x].isOn) {
      cOn.push("1");
    } else {
      cOn.push("0");
    }
  }

  for (let y = 0; y < optArr.CipherSelection.length; y++) {
    if (
      cNames.join("|") == optArr.CipherOrder[y].join("|") &&
      cOn.join("|") == optArr.CipherSelection[y].join("|")
    ) {
      return y;
    }
  }

  return -1;
}

function Slide_MatchCipher(impNum, impEvent) {
  //Set local variables
  let thisCipher,
    sendVar = -1;
  thisCipher = historyCiphers[impNum];

  //If Control is pressed...
  if (impEvent.ctrlKey) {
    //If Alt is also pressed, remove the cipher
    if (impEvent.altKey) {
      historyCiphers.splice(impNum, 1);
      sendVar = 0;
    } else {
      //If only Ctrl is pressed, move the cipher up
      if (impNum > 0) {
        historyCiphers.splice(impNum, 1);
        historyCiphers.splice(impNum - 1, 0, thisCipher);
        sendVar = 2;
      }
    }
    //If only Alt is pressed, move the cipher down
  } else if (impEvent.altKey) {
    if (impNum < historyCiphers.length - 1) {
      historyCiphers.splice(impNum, 1);
      historyCiphers.splice(impNum + 1, 0, thisCipher);
      sendVar = 1;
    }
  }

  //Call the next functions if qualified
  if (sendVar == -1) {
    return;
  }
  Update_MatchArrays(impNum, sendVar);
  Build_MatchTable(currPage);
}
function Update_MatchArrays(impNum, impType) {
  let thisHist,
    thisGem,
    thisCiph,
    multiImp = false;

  //Cycle through each Matched item
  for (let x = 0; x < historyMatched.length; x++) {
    thisHist = historyMatched[x];
    thisGem = thisHist.gemArr[impNum];
    thisCiph = thisHist.ciphArr[impNum];

    //Remove the gematria from the array
    thisHist.gemArr.splice(impNum, 1);
    thisHist.ciphArr.splice(impNum, 1);

    //If moving the cipher, slide the value over
    if (impType == 1) {
      thisHist.gemArr.splice(impNum + 1, 0, thisGem);
      thisHist.ciphArr.splice(impNum + 1, 0, thisCiph);
    } else if (impType == 2) {
      thisHist.gemArr.splice(impNum - 1, 0, thisGem);
      thisHist.ciphArr.splice(impNum - 1, 0, thisCiph);
    }
  }

  if (historyNumeric == true) {
    SlimNumMatches();
    return;
  }

  //Do the same thing for the main Matched item
  thisGem = historyMatch.gemArr[impNum];
  thisCiph = historyMatch.ciphArr[impNum];

  historyMatch.gemArr.splice(impNum, 1);
  historyMatch.ciphArr.splice(impNum, 1);

  if (historyMatch.gemArr.indexOf(thisGem) > -1) {
    multiImp = true;
  }

  if (impType == 1) {
    historyMatch.gemArr.splice(impNum + 1, 0, thisGem);
    historyMatch.ciphArr.splice(impNum + 1, 0, thisCiph);
  } else if (impType == 2) {
    historyMatch.gemArr.splice(impNum - 1, 0, thisGem);
    historyMatch.ciphArr.splice(impNum - 1, 0, thisCiph);
  } else if (impType == 0) {
    RerankMatches();
  }
}
function SelBaseCiphers() {
  const numCiphers = CipherCount(1);
  for (let x = 0; x < numCiphers; x++) {
    if (baseArr.includes(allCiphers[x].Nickname)) {
      document.getElementById("Cipher" + x).checked = true;
    } else {
      document.getElementById("Cipher" + x).checked = false;
    }
  }
}
function SelAllCiphers(impBool = false) {
  const numCiphers = CipherCount(1);
  for (let x = 0; x < numCiphers; x++) {
    document.getElementById("Cipher" + x).checked = impBool;
  }
}

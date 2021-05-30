profilefreeze()
function profilefreeze(){
    sendObj = {}
    sendObj.UserId = localStorage.userid; // need to add user id here 
    console.log(sendObj);
    var form = new FormData();
    form.append("file", JSON.stringify(sendObj));
    var settings11 = {
       "async": true,
       "crossDomain": true,
       "url": 'http://127.0.0.1:5001/profile-freeze-request',
       "method": "POST",
       "processData": false,
       "contentType": false,
       "mimeType": "multipart/form-data",
       "data": form
       };
     $.ajax(settings11).done(function (msg) {
       
        msg = JSON.parse(msg);
       console.log(msg);

    //    document.getElementById("firstname").value = 'harnath';
       document.getElementById("firstname").value = msg.FirstName;
       document.getElementById("middlename").value = msg.MiddleName;
       document.getElementById("lastname").value = msg.LastName;
       document.getElementById("dateofbirth").value = msg.DateOfBirth;
       document.getElementById("height").value = msg.Height;
       document.getElementById("weight").value = msg.Weight;
       document.getElementById("sex").value = msg.Sex;
       document.getElementById("address").value = msg.Address;
      //  document.getElementById("email").value = msg.Email;
       document.getElementById("phonenumber").value = msg.PhoneNumber;
       document.getElementById("bmivalue").value = msg.BMIValue;
       document.getElementById("bmicategory").value = msg.BMICategory;
       document.getElementById("usernumber").value = msg.UserId;
       document.getElementById("minweight").value = msg.MinWeight;
       document.getElementById("maxweight").value = msg.MaxWeight;
       document.getElementById("bmrvalue").value = msg.BMRValue;
       document.getElementById("sbmrvalue").value = msg.SuggestedBMRValue;
       document.getElementById("score").innerHTML = msg.Message;
    })
}

// function profilenextbutton(){

// }
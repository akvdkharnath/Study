profilefreeze()
function profilefreeze(){
    sendObj = {}
    sendObj.UserId = localStorage.userid;
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
       document.getElementById("usernumber").value = msg.CreatedBy;
       document.getElementById("firstname").value = msg.FirstName;
       document.getElementById("lastname").value = msg.LastName;
       document.getElementById("glucoselevel").value = msg.GlucoseLevel;
       document.getElementById("heartrate").value = msg.HeartRate;
       document.getElementById("caloriesburnt").value = msg.CaloriesBurnt;
       document.getElementById("timeofexercise").value = msg.TimeOfExercise;
       document.getElementById("comments").value = msg.Comments
    })
}

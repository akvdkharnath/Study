$(document).ready(function(){
    $(".profilecls").click(function(event){
       event.preventDefault();
       var firstname = $('.firstname').val()
       var lastname =  $('.lastname').val()
       var glucoselevel =  $('.glucoselevel').val()
       var heartrate =  $('.heartrate').val()
       var caloriesburnt =  $('.caloriesburnt').val()
       var timeofexercise =  $('.timeofexercise').val()
       var comments =  $('.comments').val()
       profile(firstname,lastname,glucoselevel,heartrate,caloriesburnt,timeofexercise,comments)
     });
 })

 function profile(firstname,lastname,glucoselevel,heartrate,caloriesburnt,timeofexercise,comments){
    sendObj = {};
    sendObj.FirstName = firstname;
    sendObj.LastName = lastname;
    sendObj.GlucoseLevel = glucoselevel;
    sendObj.HeartRate = heartrate;
    sendObj.CaloriesBurnt = caloriesburnt;
    sendObj.TimeOfExercise = timeofexercise;
    sendObj.Comments = comments;
    sendObj.UserId = localStorage.userid;

    console.log(sendObj);
    var form = new FormData();
    form.append("file", JSON.stringify(sendObj));
    var settings11 = {
       "async": true,
       "crossDomain": true,
       "url": 'http://127.0.0.1:5001/profile-create-button',
       "method": "POST",
       "processData": false,
       "contentType": false,
       "mimeType": "multipart/form-data",
       "data": form
       };
     $.ajax(settings11).done(function (msg) {
       msg = JSON.parse(msg);
       console.log(msg);
       if (msg.Status == true){
         alert("Profile Created Successfully");
         window.location.href="profilefreeze-page"
       }
       else{
         alert("Profile not created please try once more");
       } 
    })
 }
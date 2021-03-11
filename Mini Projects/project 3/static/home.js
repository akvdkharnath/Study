
$(document).ready(function(){


// Get the element with id="defaultOpen" and click on it
// create acount ka code //


  $(".createcls").click(function(event){
      event.preventDefault();
    var email= $('.useremail').val();
    var password=  $('.password1').val();
    var conformedpassword = $('.cpassword').val();
    var username = $('.username1').val();
    createaccount(email,password,conformedpassword,username)
    });
 


 // login ka code //


  $(".logincls").click(function(event){
     event.preventDefault();
    var email= $('.username').val();
    var password=  $('.password').val();
    loginaccount(email,password)
   });

  $(".questiontab").click(function(){

  
    sendObj ={}
  var form = new FormData();
  form.append("file", JSON.stringify(sendObj));
  var settings11 = {
     "async": true,
     "crossDomain": true,
     "url": 'http://127.0.0.1:5001/get-answers',
     "method": "POST",
     "processData": false,
     "contentType": false,
     "mimeType": "multipart/form-data",
     "data": form
     };
   $.ajax(settings11).done(function (msg) {
     msg = JSON.parse(msg);
     console.log(msg);

     for (let i = 0; i < msg.length; i++) {
        var add = ''
        add += '<h1 style="color:white;">'+msg[i].question+'</h1>'
        add += '<p style="font-size:160%; color:white;">'+'answered on '+msg[i].answered_date+'</p>'
        add += '<p style="font-size:160%; color:white;">'+msg[i].answer+'</p>'          
        $('.blog').append(add)
     }
   })
   })

// servay ka code //
  $(".surveycls").click(function(event){
     event.preventDefault();
     var first_name = $('.firstname').val();
     var last_name = $('.lastname').val();
     var glucose_level = $('.glucoselevel').val();
     var heart_rate = $('.heartrate').val();
     var calories_brunt = $('.caloriesburnt').val();
     var time = $('.timeofexercise').val();
     var comments = $('.comments').val();
    insertservay(first_name,last_name,glucose_level,heart_rate,calories_brunt,time,comments)
   });





// question ka code //
  $(".questioncls").click(function(event){
     event.preventDefault();
     var question = $('.question').val();
     var user_id = 1
    insertquestion(question,user_id)
   });


  })

function insertquestion(question,user_id){
  sendObj = {};
  sendObj.question = question;
  sendObj.user_id = user_id;
  
  console.log(sendObj);
  var form = new FormData();
  form.append("file", JSON.stringify(sendObj));
  var settings11 = {
     "async": true,
     "crossDomain": true,
     "url": 'http://127.0.0.1:5001/create-question-button',
     "method": "POST",
     "processData": false,
     "contentType": false,
     "mimeType": "multipart/form-data",
     "data": form
     };
   $.ajax(settings11).done(function (msg) {
     msg = JSON.parse(msg);
     console.log(msg);
     if (msg.status == true){
        alert("your question submitted thank you") 
        window.location.href="question-page"
       }
      else{
      alert("some thing went wrong pls try again");
      }
  })
}

function createaccount(email,password,conformedpassword,username){
  sendObj = {};
  sendObj.user_email = email;
  sendObj.password = password;
  sendObj.conformed_password = conformedpassword;
  sendObj.user_name = username;
  
  console.log(sendObj);
  var form = new FormData();
  form.append("file", JSON.stringify(sendObj));
  var settings11 = {
     "async": true,
     "crossDomain": true,
     "url": 'http://127.0.0.1:5001/create-account-button',
     "method": "POST",
     "processData": false,
     "contentType": false,
     "mimeType": "multipart/form-data",
     "data": form
     };
   $.ajax(settings11).done(function (msg) {
     msg = JSON.parse(msg);
     console.log(msg);
     if (msg.status == true){
      alert("Account Created Successfully");
      // window.location.href="login-page"
     }
      else{
      alert("Account not created please check your email and password");
      }
  })
}

function loginaccount(email,password){
  sendObj = {};
  sendObj.user_email = email;
  sendObj.password = password;

  console.log(sendObj);
  var form = new FormData();
  form.append("file", JSON.stringify(sendObj));
  var settings11 = {
     "async": true,
     "crossDomain": true,
     "url": 'http://127.0.0.1:5001/login-button',
     "method": "POST",
     "processData": false,
     "contentType": false,
     "mimeType": "multipart/form-data",
     "data": form
     };
   $.ajax(settings11).done(function (msg) {
     msg = JSON.parse(msg);
     console.log(msg);
     if (msg.status == true){
      localStorage.userid = msg.user_id;
       if (msg.role == "Export"){
        window.location.href="export-page"
       }
       else{
        window.location.href="question-page"
       }
       
     }
      else{
      alert("Incorrect email and password");
      }
  })
}

function insertservay(first_name,last_name,glucose_level,heart_rate,calories_brunt,time,comments){
  sendObj = {};
  sendObj.first_name = first_name;
  sendObj.last_name = last_name;
  sendObj.glucose_level = glucose_level;
  sendObj.heart_rate = heart_rate;
  sendObj.calories_brunt = calories_brunt;
  sendObj.time = time;
  sendObj.comments = comments;
  
  console.log(sendObj);
  var form = new FormData();
  form.append("file", JSON.stringify(sendObj));
  var settings11 = {
     "async": true,
     "crossDomain": true,
     "url": 'http://127.0.0.1:5001/submit-survey-button',
     "method": "POST",
     "processData": false,
     "contentType": false,
     "mimeType": "multipart/form-data",
     "data": form
     };
   $.ajax(settings11).done(function (msg) {
     msg = JSON.parse(msg);
     console.log(msg);
     alert("data subbmitted")

  })
}

document.getElementById("defaultOpen").click();


function openPage(pageName, elmnt, color) {
  // Hide all elements with class="tabcontent" by default */
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove the background color of all tablinks/buttons
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(pageName).style.display = "block";

  // Add the specific color to the button used to open the tab content
  elmnt.style.backgroundColor = color;
}
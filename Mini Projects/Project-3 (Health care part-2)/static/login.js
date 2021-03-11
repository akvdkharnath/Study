$(document).ready(function(){
   $(".logincls").click(function(event){
      event.preventDefault();
     var userName= $('.username').val();
     var password=  $('.password').val();
     login(userName,password)
    });
})

function login(username, password){
   sendObj = {};
   sendObj.UserEmail = username;
   sendObj.Password = password;
   //  sendObj.currentdate = currentdate;
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
      if (msg.ValidLogin == true){
         // window.location.href="../templates/profile.html";
         if (msg.IsProfileCreated == true){
            localStorage.userid = msg.UserId;
            window.location.href="profilefreeze-page"
            }
         else{
            localStorage.userid = msg.UserId;
            window.location.href="profile-page"
         }
      }
      else {
         alert("Invalid username/password");
     }

   })
}
debugger
$(document).ready(function(){
    $(".createcls").click(function(event){
       event.preventDefault();
      var email= $('.username').val();
      var password=  $('.password').val();
      var conformedpassword = $('.cpassword').val();
      createaccount(email,password,conformedpassword)
     });
 })
 function createaccount(email,password,conformedpassword){
    sendObj = {};
    sendObj.UserEmail = email;
    sendObj.Password = password;
    sendObj.ConformedPassword = conformedpassword;
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
       if (msg.Status == true){
        alert("Account Created Successfully");
        window.location.href="login-page"
       }
        else{
        alert("Account not created please check your email and password");
        }
    })
 }
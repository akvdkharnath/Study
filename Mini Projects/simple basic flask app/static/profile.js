$(document).ready(function(){
    $(".profilecls").click(function(event){
       event.preventDefault();
       var firstname = $('.firstname').val()
       var middlename = $('.middlename').val()
       var lastname =  $('.lastname').val()
       var dateofbirth = $('.dateofbirth').val()
       var height = $('.height').val()
       var weight = $('.weight').val()
       var sex = $('.sex').val()
       var address = $('.address').val()
       var email = $('.email').val()
       var phonenumber = $('.phonenumber').val()
    profile(firstname,middlename,lastname,dateofbirth,height,weight,sex,address,email,phonenumber)
     });
 })

 function profile(firstname,middlename,lastname,dateofbirth,height,weight,sex,address,email,phonenumber){
    sendObj = {};
    sendObj.FirstName = firstname;
    sendObj.MiddleName = middlename;
    sendObj.LastName = lastname;
    sendObj.DateOfBirth = dateofbirth;
    sendObj.Height = height;
    sendObj.Weight = weight;
    sendObj.Sex = sex;
    sendObj.Address = address;
    sendObj.Email = email;
    sendObj.PhoneNumber = phonenumber;
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
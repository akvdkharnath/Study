$(document).ready(function(){
    $(".recordcls").click(function(event){
     
        event.preventDefault();
        var selecteddate = $('.selecteddate').val()
        var cin = $('.cintake').val()
        var cout = $('.couttake').val()
        $('input[type="text"]').val('');
        $('input[type="date"]').val('');
  
     result(selecteddate,cin,cout)
    })
 })

function result(selecteddate,cin,cout){
    sendObj = {};
    sendObj.SelectedDate = selecteddate
    sendObj.Cin = cin
    sendObj.Cout = cout
    sendObj.UserId = localStorage.userid;
    console.log(sendObj);
     var form = new FormData();
     form.append("file", JSON.stringify(sendObj));
     var settings11 = {
        "async": true,
        "crossDomain": true,
        "url": 'http://127.0.0.1:5001/record-create-button',
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
         alert("Record Created Successfully");
       }
       else{
         alert("Record not created please try once more");
       }
     })
  }
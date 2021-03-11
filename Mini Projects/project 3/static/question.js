$(document).ready(function(){
    $(".surveycls").click(function(event){
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
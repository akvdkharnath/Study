// Accordian
var speed="500";

pageload()
function pageload(){
    sendObj = {};
    console.log(sendObj);
    var form = new FormData();
    form.append("file", JSON.stringify(sendObj));
    var settings11 = {
       "async": true,
       "crossDomain": true,
       "url": 'http://127.0.0.1:5001/get-questions',
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
       
      var qa = msg[i]
      var add =''
      add += ' <li class="q"><i class="ion-chevron-right"></i>'+qa.question+'</li>'
      add += ' <li class="a"><textarea class="question  questionanswer'+i+'" questionname='+qa.question+'  rows="4" cols="100" placeholder="please processed"></textarea></li>'
      $('.faq').append(add)
    }
        


       
    })
  


}

// Accordian
var action="click";
var speed="500";

$(document).ready(function() {
    // Question handler
    $('body').on('click','li.q',function(){

        // Get next element
        $(this).next()
            .slideToggle(speed)
        // Select all other answers
                .siblings('li.a')
                    .slideUp();
    });


    $('body').on('click','.submit_question',function(){

        newArray =[]
        var count = $('.question')
        for (let i = 0; i < count.length; i++) {
        var question =$('.questionanswer'+i).attr('questionname')
        var answer  =$('.questionanswer'+i).val()
        obj ={}
        obj.Question = question
        obj.Answer = answer
        newArray.push(obj)
    }

    console.log(newArray)
    sendObj = {};
    sendObj.Data = newArray
    console.log(sendObj);
    var form = new FormData();
    form.append("file", JSON.stringify(sendObj));
    var settings11 = {
       "async": true,
       "crossDomain": true,
       "url": 'http://127.0.0.1:5001/submit-answer-button',
       "method": "POST",
       "processData": false,
       "contentType": false,
       "mimeType": "multipart/form-data",
       "data": form
       };
     $.ajax(settings11).done(function (msg) {
       msg = JSON.parse(msg);
       console.log(msg);
       window.location.href="export-page"

     })



    })
});
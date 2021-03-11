var docs = [
    {
        Title: "User 1",
        Date: "01-07-20",
        Info:    "hi i am the first user",
    },
    {
        Title: "User 2",
        Date: "01-07-20",
        Info:    "hi i am the second user",
    },
    {
        Title: "User 3",
        Date: "01-07-20",
        Info:    "hi i am the third user",
    },
]
   

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
       "url": 'http://127.0.0.1:5001/blog-freeze-request',
       "method": "POST",
       "processData": false,
       "contentType": false,
       "mimeType": "multipart/form-data",
       "data": form
       };
     $.ajax(settings11).done(function (msg) {
       
       docs = JSON.parse(msg);
       console.log(docs);
       $.each(docs,function(i,doc){
    
        var add = ''
        add += '<h4>'+doc.question+'</h4>'
        add += '<p>'+''+doc.+'</p>'
        add += '<span>'+doc.Info+'</span>'
          
        $('#contact').append(add)

})
       
       });


    }




    


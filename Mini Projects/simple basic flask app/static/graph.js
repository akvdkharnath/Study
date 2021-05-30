logindata()
function logindata(){
    sendObj = {}
    sendObj.UserId = localStorage.userid; // need to add user id here 
    console.log(sendObj);
    console.log( Date(1992, 0,10));
    var form = new FormData();
    form.append("file", JSON.stringify(sendObj));
    var settings11 = {
       "async": true,
       "crossDomain": true,
       "url": 'http://127.0.0.1:5001/graph-dataset-request',
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

        var chart = new CanvasJS.Chart("chartContainer2",
    {
        animationEnabled: true,
        title: {
            text: "No.Of Calories Workout"
        },
        axisX: {
            interval: 10,
        },
        data: [
        {
            type: "column",
            legendMarkerType: "triangle",
            legendMarkerColor: "green",
            color: "rgba(255,12,32,.3)",
            showInLegend: true,
            legendText: "Day wise Calories Burned",
            dataPoints:msg.loose
        },
        ]
    });
chart.render();
var chart = new CanvasJS.Chart("chartContainer1",
    {
        animationEnabled: true,
        title: {
            text: "No.Of Calories Gained"
        },
        axisX: {
            interval: 10,
        },
        data: [
        {
            type: "column",
            legendMarkerType: "triangle",
            legendMarkerColor: "green",
            color: "rgba(255,12,32,.3)",
            showInLegend: true,
            legendText: "Day wise Calories gained",
            dataPoints:msg.gain
        },
        ]
    });
chart.render();       

var chart = new CanvasJS.Chart("chartContainer3",
    {
        animationEnabled: true,
        title: {
            text: "No.Of Calories Gained/Loosed by end of the Day"
        },
        axisX: {
            interval: 10,
        },
        data: [
        {
            type: "column",
            legendMarkerType: "triangle",
            legendMarkerColor: "green",
            color: "rgba(255,12,32,.3)",
            showInLegend: true,
            legendText: "Sum of gained and burned Calories as per day",
            dataPoints:msg.maintain
        },
        ]
    });
chart.render();
var chart = new CanvasJS.Chart("chartContainer4",
    {
        animationEnabled: true,
        title: {
            text: "Variation in Calories gained/burned as per BMR value"
        },
        axisX: {
            interval: 10,
        },
        data: [
        {
            type: "column",
            legendMarkerType: "triangle",
            legendMarkerColor: "green",
            color: "rgba(255,12,32,.3)",
            showInLegend: true,
            legendText: "Difference of BMR value and final Calories value",
            dataPoints:msg.endoftheday
        },
        ]
    });
chart.render();       












}})}




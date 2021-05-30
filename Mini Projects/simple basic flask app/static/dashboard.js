var dataTable___;
var selectedFiles = [];
pageonloadhit()
function pageonloadhit() {
    obj = {}
    obj.UserId = localStorage.userid;
    // obj.IsDefault = true
    console.log(obj);
    var form = new FormData();
    form.append("file", JSON.stringify(obj));
    var settings11 = {
        "async": true,
        "crossDomain": true,
        "url": 'http://127.0.0.1:5001/dashboard-onscreen-load',
        "method": "POST",
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form
    };
    $.ajax(settings11).done(function (msg) {
        msg = JSON.parse(msg);
        console.log(msg);
        // $(".loading").hide();
        if (msg.Status == false){
            alert("Pls refresh the page we are unable to get the data");}
        else {
            msg1 = msg.Record
            displaytable(msg1);    
        }

    })
}


function displaytable(record) {
    // <col width="13000">
    row = ''
    
    row +='<table class="tablecls" align="center" style="border:1px solid black">'
    row +='<tr>'
    row +='<th> Sno</th>'
    row +='<th>User Id</th>'
    row +='<th>Date Of the Record</th>'
    row +='<th>Ideal BMR Value</th>'
    row +='<th>Calorie Input</th>'
    row +='<th>Calorie Output</th>'
    row +='<th>Final Calorie</th>'
    row +='<th>Variation</th>'
    
    row +='</tr>'
    
    for (var i = 0; i < record.length; i++) {
        block = record[i];
        var PlanScheduleStatus= block['PlanScheduleStatus']
        createschedulealert =block['CreateScheduleAlert']
       allowreplanFromacceleratedFile=block['AllowReplanFromAcceleratedFile']
       scheduleid= block['ScheduleId']
       campaignid=block['CampaignId']
        

        row += '<tr>'
        row += '<td>'+(i+1)+'</td>'
        // row += '<td  style="" class="nr"><a key="'+i+'" style="text-decoration:underline; cursor:pointer;" acceleratorpathbyrpa = "'+block.AcceleratorFilePathByRPA+'" id="camp_idhyperlink_"  plainidattr="'+block.PlanId+'" status="'+block.PlanStatus+'" class="statusCheck">'+block.CampaignId+'</a></td>';
        row += '<td>'+block.UserId+'</td>';
        row += '<td>'+format_date(block.DateCreated)+'</td>';
        row += '<td>'+block.IdealBMRValue+'</td>';
        row += '<td>'+block.CalorieInput+'</td>';
        row += '<td>'+block.CalorieOutput+'</td>';
        row += '<td>'+block.FinalCalorie+'</td>';
        row += '<td>'+block.Variation+'</td>';

        




        // row += '<td  style="width: 121px;">'+block.ClientName+'</td>';
        // row += '<td style="width: 142px;">'+block.BrandName+' </td>';
        // row += '<td style="width: 125px;">'+block.PlannerName+'</td>';
        // row += '<td style="width: 159px;">'+format_date(block.StartDate)+'</td>';
        // row += '<td style="width: 162px;">'+format_date(block.EndDate)+'</td>';
        // if (block.IsPrioritized == false) {
        // row += '<td><div class="replanmodal" Campaignid='+block.CampaignId+' plainidattr='+block.PlanId+' ><img src="assets/images/WhiteIcons/replan.png" style="width:27px;"></div></td>';

        // row += '<td style="text-align:center;"><div class="downloadbtn pointer" campId="'+block.CampaignId+'" plainidattr="'+block.PlanId+'" style=""><img src="assets/images/WhiteIcons/download.png" style="width:27px;"></div></td>';
        row += '</tr>';
       
    }
    row+='</table>'

    $(".dashboard-table").html(row)
    

}




function format_date(date_string) {
    date = new Date(date_string)
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
    weeks_ = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"];
    hours_mian = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"];
    hrs = date.getHours().toString().length < 2 ? '0'+date.getHours() : date.getHours()
    mins = date.getMinutes().toString().length < 2 ? '0'+date.getMinutes() : date.getMinutes()
    return date.getDate()+'-'+months[date.getMonth()]+'-'+date.getFullYear()+' &nbsp&nbsp'+hrs+':'+mins;
}



// })
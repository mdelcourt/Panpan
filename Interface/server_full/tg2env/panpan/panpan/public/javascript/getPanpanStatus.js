function httpGet(theUrl)
{
  var xmlHttp = null;

  xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", theUrl, false );
  xmlHttp.send( null );
  return xmlHttp.responseText;
}
//   document.getElementById('requestStatus').innerHTML="Trying to get process status...";

var relaunch = true;
var nDots = 0;

function refreshStatus()
{
  var refreshing = document.getElementById('refreshingStatus');
  if (relaunch){
    document.getElementById('requestStatus').innerHTML=httpGet("jobStatus?name="+name);
    var refreshingTxt = "Status updating";
    for (var i = 0; i<nDots; i++){
      refreshingTxt+=".";
    }
    nDots+=1;
    if (nDots==5) nDots=1;
  }
  if ( document.getElementById('requestStatus').innerHTML.indexOf('JOBISDONE') > 0 ||document.getElementById('requestStatus').innerHTML.indexOf('Cannot find job status') > -1 ){
  relaunch = false;
  refreshingTxt="";
//   refreshingTxt = "Status not updating.";
  }
  refreshing.innerHTML=refreshingTxt;
}
refreshStatus();
setInterval(refreshStatus,500);

function deletePanpan(){
  var x = confirm("Are you sure you want to delete "+name+"?");
  if (x==true){
   javascript:window.location.href='deletePanpan?name='+name;
  }
}

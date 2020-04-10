$(document).ready(function(){
   var queries = []


$("#results").empty()
var row1 = $("<div class = 'row bottom_row_padding'>")
var col6 = $("<div class = 'col-md-1'>")
var col1 = $("<div class = 'col-md-4'>")
var col2 = $("<div class = 'col-md-2'>")
var col3 = $("<div class = 'col-md-2'>")
var col4 = $("<div class = 'col-md-2'>")
var col5 = $("<div class = 'col-md-1'>")

$(col6).append("<h4 style=\"text-decoration:underline;\">Record Count</h4>")
$(col1).append("<h4 style=\"text-decoration:underline;\">Query Syntax</h4>")
$(col2).append("<h4 style=\"text-decoration:underline;\">Table Name</h4>")
$(col3).append("<h4 style=\"text-decoration:underline;\">Created on</h4>")
$(col4).append("<h4 > </h4>")
$(col5).append("<h4> </h4>")

$(row1).append(col6)
$(row1).append(col1)
$(row1).append(col2)
$(row1).append(col3)
$(row1).append(col4)
$(row1).append(col5)

$("#results").append(row1)

// display some variables (json)

$.each(final_result, function(i, val){
		var row = $("<div class = 'row bottom_row_padding' >")
		var column5 = $("<div class = 'col-md-1'>")
		var column = $("<div class = 'col-md-4 player"+i+"'>")
		var column1 = $("<div id = 'tablename' class = 'col-md-2'>")
		var column2 = $("<div class = 'col-md-2'>")
		var column3 = $("<div class = 'col-md-2'>")
		var column4 = $("<div class = 'col-md-1'>")
	  queries.push(val["tablename"])
    $(column5).append(linesCount[i])
		$(column).append(val["query"])
		$(column1).append(val["tablename"])
		$(column2).append(new Date(val["timestamp"]).toUTCString())
		$(column3).append("<button  type='button' class='btnOK btn  btn-sm btn-primary'>View Result</button>")
		$(column4).append("<button type='button' class='delete btn btn-sm btn-danger'>Delete Record</button>")


		$(row).append(column5)
		$(row).append(column)
		$(row).append(column1)
		$(row).append(column2)
		$(row).append(column3)
		$(row).append(column4)

		$(row).append("<div class = 'demo'>")



		$(row).hover(function(){
		$(this).css("background-color", "#F0FFFF");
		}, function(){
			console.log($(this))
			$(this).css("background-color", "white");
		});
		$("#results").append("<br></br>")
		$("#results").append(row)

})



function closeBigImgAndContainer(evt)
{
	var giddy = evt.currentTarget.myParam
	var data_to_save = {"findvar":evt.currentTarget.myParam}
	$.ajax({
		type : 'POST',
		dataType : "json",
		url : "fetch",
		contentType: 'application/json;charset=UTF-8',
		data : JSON.stringify(data_to_save),
		success: function(result){
			console.log(giddy)

			// console.log(result);
			// console.log(typeof(result))
			// $("body").html(JSON.stringify(result));
			window.location.href = '/display/'+giddy;
		},
		error: function(request, status, error){
			console.log("Error");
			console.log(request)
			console.log(status)
			console.log(error)
		}
	  });

};

var closeIcons=document.getElementsByClassName("btnOK");

for (i = 0; i < closeIcons.length; i++) {

	closeIcons[i].addEventListener("click", closeBigImgAndContainer, false);
	closeIcons[i].myParam = queries[i];
}

function deleteRecords(evt)
{
	var giddy = evt.currentTarget.myParam
	var data_to_save = {"findvar":giddy}
	// $('.row').each(function(i, obj) {
	// 	//delete row if its button is clicked.
	// 	if($('#tablename').text().length > 0) {  // Checking the text inside a div
	// 		// Condition to check the  text match
	// 		console.log($("#tablename:contains("+giddy+")"));
	// 		if($("#tablename:contains(" + giddy + ")")){
	// 			console.log(obj);
	// 			// $('#toremove').remove();
	// 		}
	// 	  }
	// });

	$.ajax({
		type : 'POST',
		dataType : "json",
		url : "delete",
		contentType: 'application/json;charset=UTF-8',
		data : JSON.stringify(data_to_save),
		success: function(result){
			// console.log(result);
			// console.log(typeof(result))
			// $("body").html(JSON.stringify(result));
			window.location.href = "/pastFilter";;
		},
		error: function(request, status, error){
			console.log("Error");
			console.log(request)
			console.log(status)
			console.log(error)
		}
	  });

};

var deleteIcon = document.getElementsByClassName("delete");

for (i = 0; i < deleteIcon.length; i++) {

	deleteIcon[i].addEventListener("click", deleteRecords, false);
	deleteIcon[i].myParam = queries[i];
}

})

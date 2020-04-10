$(document).ready(function(){

filter_object = JSON.parse(json_filters)
console.log(filter_object);

var rules_basic = {
	condition: 'AND',
	rules: [{
	  condition: 'OR',
	  rules: []
	}]
  };


  $('#builder').queryBuilder({
	plugins: ['bt-tooltip-errors'],

	filters: [ {
	  id: 'category',
	  label: 'Category',
	  type: 'integer',
	  input: 'select',
	  values: {
		1: 'Books',
		2: 'Movies',
		3: 'Music',
		4: 'Tools',
		5: 'Goodies',
		6: 'Clothes'
	  },
	  operators: ['equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
	},
	{
		id: 'name',
		label: 'Selectize',
		type: 'string',
		plugin: 'selectize',
		plugin_config: {
		  valueField: 'id',
		  labelField: 'name',
		  searchField: 'name',
		  sortField: 'name',
		  create: true,
		  maxItems: 1,
		  plugins: ['remove_button'],
		  onInitialize: function() {
			var that = this;

			if (localStorage.demoData === undefined) {
			  $.getJSON('http://querybuilder.js.org/assets/demo-data.json', function(data) {
				localStorage.demoData = JSON.stringify(data);
				data.forEach(function(item) {
				  that.addOption(item);
				});
			  });
			}
			else {
			  JSON.parse(localStorage.demoData).forEach(function(item) {
				that.addOption(item);
			  });
			}
		  }
		},
		valueSetter: function(rule, value) {
		  rule.$el.find('.rule-value-container input')[0].selectize.setValue(value);
		}
	}],

  });
  $('#builder').queryBuilder('addFilter', filter_object);

  $('#builder').queryBuilder('removeFilter', 'name');
  $('#builder').queryBuilder('removeFilter', 'category');


  // Fix for Bootstrap Datepicker
$('#builder').on('afterUpdateRuleValue.queryBuilder', function(e, rule) {
	if (rule.filter.plugin === 'datepicker') {
	  rule.$el.find('.rule-value-container input').datepicker('update');
	}
  });


  $('#builder').on('afterCreateRuleInput.queryBuilder', function(e, rule) {
	if (rule.filter.plugin == 'selectize') {
	rule.$el.find('.rule-value-container').css('min-width', '200px')
		.find('.selectize-control').removeClass('form-control');
	}
});




  $('#btn-reset').on('click', function() {
	$('#builder').queryBuilder('reset');
  });

  var delayInMilliseconds = 1000000000000; //1 second




  $('#btn-get').on('click', function() {
	var result = $('#builder').queryBuilder('getSQL');

	if (!$.isEmptyObject(result)) {
	var query = JSON.stringify(result, null, 2)
	 var name = result["sql"];
	 json_var = {'data':name};

	 Swal.fire({
		title: 'Enter Table Name',
		input: 'text',
		inputAttributes: {
		  autocapitalize: 'off'
		},
		showCancelButton: false,
		confirmButtonColor: 'green',
		confirmButtonText: 'Save',
		showLoaderOnConfirm: true,
		allowOutsideClick: () => !Swal.isLoading()
	  }).then((result) => {
		Object.assign(json_var, {'tableName': result.value});
		if (result.value) {
			console.log("Result: " + result.value);
			Object.assign(json_var, {'tableName': result.value});
			Swal.fire({
			  title: 'Save?',
			  text: "Once saved, you won't be able to edit your query",
			  icon: 'warning',
			  showCancelButton: true,
			  confirmButtonColor: 'green',
			  cancelButtonColor: '#d33',
			  confirmButtonText: 'Yes, save it'
			}).then((result) => {
			  if (result.value) {
				  Swal.fire({
					  position: 'top-end',
					  icon: 'success',
					  title: 'Your work has been saved',
					  showConfirmButton: false,
					  timer: 1500
					})
			  }
			})

			$.ajax({
				type : 'POST',
				dataType : "json",
				url : "tableResults",
				contentType: 'application/json;charset=UTF-8',
				data : JSON.stringify(json_var),
				success: function (response) {
					location.href= "/pastFilter";
				}
			  });

		}
	  })



	//   Swal.fire({
	// 	position: 'top-end',
	// 	icon: 'success',
	// 	title: 'Your work has been saved',
	// 	showConfirmButton: false,
	// 	timer: 2500

	}
  });

})

$(".panel").hide();

$(".accordion").on('click', function(){
	var panel = $(this).next();
	if ($(this).hasClass("active"))
		panel.hide();
	else
		panel.show();
	$(this).toggleClass("active");
});
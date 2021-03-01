var pitfall_count = 0;

$("#actions-header").width($("#buttons-div-0").width()); 

$("#pitfalls-div").on("click", ".delete", function(event){
    var row_id = "row-" + $(this).attr('id').split("-").slice(-1)[0];
    $("#" + row_id).remove();
    var max_conditions = -1;
    var rows = $(".row").slice(1);
    if (rows == 0)
        return
    rows.each(function(row){
        conditions = $(rows[row]).find("select").length-1;
        if (conditions > max_conditions)
            max_conditions = conditions;
    });
    var header_conditions = ($("#header").find(".col").length-1);
    if (header_conditions > max_conditions)
        $("#header").find(".col").slice(- header_conditions + max_conditions).remove();
});

$("#pitfalls-div").on("click", ".add-cond", function(event){
    var row_id = "criticality-div-" + $(this).attr('id').split("-").slice(-1)[0];
    var condition_id = $("#" + row_id).parent().prev().find("select").attr('id').split("-").slice(-1)[0];
    condition_id++;
    var new_cond = "<div class='col'>\
        <div class='form-group'>\
            <select class='form-control predicate-select' name='predicate-select-"+pitfall_count+"' id='predicate-select-"+pitfall_count+"-"+condition_id+"'>\
                <option selected>Select predicate...</option>\
                <option>Has attribute</option>\
                <option>Has child</option>\
            </select>\
        </div>\
    </div>\
    <div class='col'>\
        <div class='form-group' id='object-div-"+pitfall_count+"-"+condition_id+"'>\
            <select class='form-control object-select' name='object-select-"+pitfall_count+"' id='object-select-"+pitfall_count+"-"+condition_id+"'>\
                <option selected>Select object...</option>\
                <option>ID</option>\
                <option>Language</option>\
            </select>\
        </div>\
    </div>";
    $("#" + row_id).parent().before(new_cond);
    condition_id++;
    
        
});

$("#pitfalls-div").on("change", ".predicate-select", function(event){
    var class_element = $(this).attr('class').split(" ").slice(-1)[0];
    var id = $(this).attr('id').split("-").slice(-2).join("-");
    var predicate_id = "#predicate-select-" + id;

    var predicate_val = $(predicate_id).val();
    var object_select = "<select class='form-control' name='object-select-"+id.split("-")[0]+"' id='object-select-" + id + "'>";
    console.log(predicate_val);
    var options = [];
    if (predicate_val == "Has child")
        options = ["Label", "Type", "Domain", "Range", "Subclass"];
    else
        options = ["ID", "Language"];
    for (index in options)
        object_select += "<option>" + options[index] + "</option>";
    object_select += "</select>";
    $("#object-div-" + id).html(object_select);
});

$( "#add-pitfall" ).click(function() {
    pitfall_count++;
    $("#pitfalls-div").append("<div class='row' id='row-" + pitfall_count + "'>\
            <div class='col'>\
                <div class='form-group'>\
                    <select class='form-control subject-select' name='subject-select-"+pitfall_count+"' id='subject-select-" + pitfall_count + "'>\
                        <option selected>Select subject...</option>\
                        <option>Classes</option>\
                        <option>Instances</option>\
                        <option>Properties</option>\
                    </select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group'>\
                    <select class='form-control predicate-select' name='predicate-select-"+pitfall_count+"' id='predicate-select-" + pitfall_count + "-0'>\
                        <option selected>Select predicate...</option>\
                        <option>Has attribute</option>\
                        <option>Has child</option>\
                    </select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group' id='object-div-" + pitfall_count + "-0'>\
                    <select class='form-control object-select' name='object-select-"+pitfall_count+"' id='object-select-" + pitfall_count + "-0'>\
                        <option selected>Select object...</option>\
                        <option>ID</option>\
                        <option>Language</option>\
                    </select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group' id='criticality-div-" + pitfall_count + "'>\
                    <select class='form-control criticality-select' name='criticality-select-"+pitfall_count+"' id='criticality-select-" + pitfall_count + "-0'>\
                        <option selected>Select rule priority...</option>\
                        <option>Critical</option>\
                        <option>Intermediate</option>\
                        <option>Minor</option>\
                    </select>\
                </div>\
            </div>\
            <div class='buttons-div' id='buttons-div-" + pitfall_count + "'>\
                <button type='button' class='add-cond btn btn-success' id='add-cond-" + pitfall_count + "'>\
                    <i class='fa fa-plus'></i>&nbsp; Add condition\
                </button>\
                &nbsp;\
                <button type='button' class='delete btn btn-danger' id='delete-" + pitfall_count + "'>\
                    <i class='fa fa-trash'></i>&nbsp; Delete\
                </button>\
            </div>\
        </div>");
});


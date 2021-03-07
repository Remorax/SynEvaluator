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

    var object_values = $.map($('#object-select-0-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    var pred_values = $.map($('#predicate-select-0-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    var new_cond = "<div class='col'>\
        <div class='form-group'>\
            <select class='form-control predicate-select' name='predicate-select-"+pitfall_count+"' id='predicate-select-"+pitfall_count+"-"+condition_id+"'>"
                + pred_values.join("\n") +
            "</select>\
        </div>\
    </div>\
    <div class='col'>\
        <div class='form-group' id='object-div-"+pitfall_count+"-"+condition_id+"'>\
            <select class='form-control object-select' name='object-select-"+pitfall_count+"' id='object-select-"+pitfall_count+"-"+condition_id+"'>"
                + object_values.join("\n") +
            "</select>\
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
    var options = [];
    if (predicate_val == "Has Child Element")
        options = ["License", "Label", "Type", "Domain", "Range", "Annotation", "Subclass", "Is Relation", "Inverse Relation", "Equivalent Property", "Equivalent Class", "Disjoint Class", "Property Chain Axiom"];
    else if (predicate_val == "Has Attribute")
        options = ["ID", "Language", "Defined Namespace", "Used Namespace"];
    else if (predicate_val == "Has File Extension")
        options = ["Ontology(.owl/.rdf/.xml)", "Other"];
    else if (predicate_val == "Maps to Element of Type")
        options = ["Element", "Class", "Property", "Instance"];
    else if (predicate_val == "Uses Comparative Operator")
        options = ["Equality", "Inequality", "Synonymy", "Inverse"];
    else if (predicate_val == "Uses Conjunctive Operator")
        options = ["And", "Or"];
    else if (predicate_val == "Has Logical Property")
        options = ["Text Validity", "ID Consistency", "Text Symmetry", "Uniqueness"];
    else if (predicate_val == "Has Linguistic Property")
        options = ["Contains Polysemes", "Contains Conjunctions", "Contains Misc Items"];
    else
        options = ["License", "Label", "Type", "Domain", "Range", "Annotation", "Relations", "Subclass", "Is Relation", "Inverse Relation", "Equivalent Property", "Equivalent Class", "Disjoint Class", "Property Chain Axiom"];
    for (index in options)
        object_select += "<option>" + options[index] + "</option>";
    object_select += "</select>";
    $("#object-div-" + id).html(object_select);
});

$( "#add-pitfall" ).click(function() {
    var subject_values = $.map($('#subject-select-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    var object_values = $.map($('#object-select-0-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    var pred_values = $.map($('#predicate-select-0-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    var priority_values = $.map($('#criticality-select-0 option') ,function(option) {
        return "<option>" + option.value + "</option>";
    });

    pitfall_count++;
    $("#pitfalls-div").append("<div class='row' id='row-" + pitfall_count + "'>\
            <div class='col'>\
                <div class='form-group'>\
                    <select class='form-control subject-select' name='subject-select-"+pitfall_count+"' id='subject-select-" + pitfall_count + "'>"
                        + subject_values.join("\n") +
                    "</select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group'>\
                    <select class='form-control predicate-select' name='predicate-select-"+pitfall_count+"' id='predicate-select-" + pitfall_count + "-0'>"
                        + pred_values.join("\n") +   
                    "</select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group' id='object-div-" + pitfall_count + "-0'>\
                    <select class='form-control object-select' name='object-select-"+pitfall_count+"' id='object-select-" + pitfall_count + "-0'>"
                        + object_values.join("\n") +
                    "</select>\
                </div>\
            </div>\
            <div class='col'>\
                <div class='form-group' id='criticality-div-" + pitfall_count + "'>\
                    <select class='form-control criticality-select' name='criticality-select-"+pitfall_count+"' id='criticality-select-" + pitfall_count + "-0'>"
                        + priority_values.join("\n") +
                    "</select>\
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


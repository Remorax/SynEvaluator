var pitfall_count = 0;
var subject_values = $.map($('#subject-select-0 option') ,function(option) {
    return "<option>" + option.value + "</option>";
});

var extractive_clauses = {
    "Has Related Element": ["Type", "Domain", "Range", "Subclass", "Is Relation", "Inverse Relation", "Equivalent Property", "Equivalent Class", "Disjoint Class", "Property Chain Axiom"],
    "Has Descriptive Element": ["License", "Annotation", "Label", "Comment"],
    "Has Attribute": ["ID", "Language", "Defined Namespace", "Used Namespace"],
    "Has File Extension": ["Ontology(.owl/.rdf/.xml)", "Other"],
    "Maps to Element of Type": ["Element", "Class", "Property", "Instance"]
};

var functional_clauses = {
    "Has Ontological Property": ["Text Validity", "ID Consistency", "Text Symmetry", "Uniqueness"],
    "Has Linguistic Property": ["Contains Polysemes", "Contains Conjunctions", "Contains Misc Items"]
};

var operator_expressions = {
    "Uses Comparative Operator": ["Equality", "Inequality", "Synonymy", "Dissimilarity", "Inverse"],
    "Uses Logical Operator": ["And", "Or", "Not"]
};

var object_values = ["Select predicate..."].concat(Object.keys(extractive_clauses), Object.keys(functional_clauses), Object.keys(operator_expressions));
var pred_values = ["Select object..."];

object_values = $.map(object_values, function(element) {
    return "<option>" + element + "</option>";
});

pred_values = $.map(pred_values, function(element) {
    return "<option>" + element + "</option>";
});

var priority_values = $.map($('#criticality-select-0 option') ,function(option) {
    return "<option>" + option.value + "</option>";
});
$("#actions-header").width($("#buttons-div-0").width()); 

$("#pitfalls-div").on('click', '.exp-type', function(){
    console.log("here");
    var row_id = $(this).parent().attr('id').split("-").slice(-1)[0];
    var condition_id;
    try {
        condition_id = $("#criticality-div-" + row_id).parent().prev().find("select").attr('id').split("-").slice(-1)[0];
    } 
    catch (err) {
        console.log(err);
        condition_id = -1;
    }
    condition_id++;
    objs = ["Select object..."];
    preds = ["Select predicate..."];
    
    if ($(this).text() == "Extractive Clause")
        preds = preds.concat(Object.keys(extractive_clauses));
    else if ($(this).text() == "Functional Clause")
        preds = preds.concat(Object.keys(functional_clauses));
    else if ($(this).text() == "Operator Expression")
        preds = preds.concat(Object.keys(operator_expressions));
    
    preds = $.map(preds, function(element) {
    return "<option>" + element + "</option>";
    });

    objs = $.map(objs, function(element) {
        return "<option>" + element + "</option>";
    });

    var new_cond = "<div class='col'>\
        <div class='form-group'>\
            <select class='form-control predicate-select' name='predicate-select-"+row_id+"' id='predicate-select-"+row_id+"-"+condition_id+"'>"
                + preds.join("\n") +
            "</select>\
        </div>\
    </div>\
    <div class='col'>\
        <div class='form-group' id='object-div-"+row_id+"-"+condition_id+"'>\
            <select class='form-control object-select' name='object-select-"+row_id+"' id='object-select-"+row_id+"-"+condition_id+"'>"
                + objs.join("\n") +
            "</select>\
        </div>\
    </div>";
    $("#criticality-div-" + row_id).parent().before(new_cond);
    console.log($("#object-select-"+row_id+"-"+condition_id).width());
    console.log($("#predicate-select-"+row_id+"-"+condition_id).width());
    if (condition_id > 1)
        $("#subject-select-" + row_id).css("width", '');
    console.log($("#subject-select-"+row_id).width());
    
});

$("#pitfalls-div").on("click", ".delete", function(event){
    var row_id = $(this).parent().attr('id').split("-").slice(-1)[0];
    if ($(this).text() == "Rule"){
        $("#row-" + row_id).remove();  
        pitfall_count--;
    }
    else if ($(this).text() == "Condition"){
        prev_elem = $("#criticality-div-" + row_id).parent().prev();
        if (!prev_elem.find("select").attr('class').split(/\s+/).includes("subject-select")){
            prev_elem.remove();
            $("#criticality-div-" + row_id).parent().prev().remove();
        }
    }
});

$("#pitfalls-div").on("change", ".predicate-select", function(event){
    var class_element = $(this).attr('class').split(" ").slice(-1)[0];
    var id = $(this).attr('id').split("-").slice(-2).join("-");
    var predicate_id = "#predicate-select-" + id;

    var predicate_val = $(predicate_id).val();
    var object_select = "<select class='form-control' name='object-select-"+id.split("-")[0]+"' id='object-select-" + id + "'>";
    var options = [];
    if (predicate_val in extractive_clauses)
        options = extractive_clauses[predicate_val]
    else if (predicate_val in functional_clauses)
        options = functional_clauses[predicate_val]
    else if (predicate_val in operator_expressions)
        options = operator_expressions[predicate_val]
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
                    <select class='form-control subject-select' style='width: 274.078px' name='subject-select-"+pitfall_count+"' id='subject-select-" + pitfall_count + "'>"
                        + subject_values.join("\n") +
                    "</select>\
                </div>\
            </div>\
            <div class='col' style='max-width: 220px'>\
                <div class='form-group' id='criticality-div-" + pitfall_count + "'>\
                    <select class='form-control criticality-select'  style='width: 190px' name='criticality-select-"+pitfall_count+"' id='criticality-select-" + pitfall_count + "-0'>"
                        + priority_values.join("\n") +
                    "</select>\
                </div>\
            </div>\
            <div class='buttons-div' id='buttons-div-" + pitfall_count + "'>\
                <div class='dropdown' style='display: inline'>\
                    <button class='btn btn-success dropdown-toggle' type='button' data-toggle='dropdown' id='add-cond-" + pitfall_count + "' aria-haspopup='true' aria-expanded='false'>\
                        <i class='fa fa-plus'></i>&nbsp; Add <span class='caret'></span>\
                    </button>\
                    <ul class='dropdown-menu' aria-labelledby='add-cond-" + pitfall_count + "'>\
                        <li id='add-eclause-" + pitfall_count + "'><a class='dropdown-item exp-type' href='#'>Extractive Clause</a></li>\
                        <li id='add-fclause-" + pitfall_count + "'><a class='dropdown-item exp-type' href='#'>Functional Clause</a></li>\
                        <li id='add-operator-" + pitfall_count + "'><a class='dropdown-item exp-type' href='#'>Operator Expression</a></li>\
                    </ul>\
                </div>\
                <div class='dropdown' style='display: inline'>\
                    <button class='btn btn-danger dropdown-toggle' type='button' data-toggle='dropdown' id='delete-" + pitfall_count + "' aria-haspopup='true' aria-expanded='false'>\
                        <i class='fa fa-trash'></i>&nbsp; Delete <span class='caret'></span>\
                    </button>\
                    <ul class='dropdown-menu' aria-labelledby='delete-" + pitfall_count + "'>\
                        <li id='delete-cond-" + pitfall_count + "'><a class='dropdown-item delete' href='#'>Condition</a></li>\
                        <li id='delete-rule-" + pitfall_count + "'><a class='dropdown-item delete' href='#'>Rule</a></li>\
                    </ul>\
                </div>\
            </div>\
        </div>");
});
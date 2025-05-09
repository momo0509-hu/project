$(document).ready(function(){
    // Natural language execute button click event (button in first input-group)
    $(".input-group").first().find("button").click(function(){
        var naturalQuery = $("#nlInput").val().trim();
        if(naturalQuery === ""){
            alert("Please enter a natural language query");
            return;
        }
        $.ajax({
            url: "/nl2sql",
            type: "POST",
            data: JSON.stringify({ query: naturalQuery }),
            contentType: "application/json",
            success: function(response){
                $("#sqlInput").val(response.sql);
            },
            error: function(xhr){
                alert("Natural language conversion failed: " + xhr.responseText);
            }
        });
    });

    // SQL execute button click event
    $("#sqlExecute").click(function(){
        var sqlQuery = $("#sqlInput").val().trim();
        if(sqlQuery === ""){
            alert("SQL cannot be empty");
            return;
        }
        $.ajax({
            url: "/execute-sql",
            type: "POST",
            data: JSON.stringify({ query: sqlQuery }),
            contentType: "application/json",
            success: function(response){
                $("#displayArea").html("<pre>" + JSON.stringify(response, null, 2) + "</pre>");
            },
            error: function(xhr){
                $("#displayArea").html("<pre>Error: " + xhr.responseText + "</pre>");
            }
        });
    });
});

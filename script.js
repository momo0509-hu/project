$(document).ready(function(){
    // Natural language execute button click event
    $("#nlExecute").click(function(){
        var naturalQuery = $("#nlInput").val().trim();
        if(naturalQuery === ""){
            alert("Please enter a natural language query");
            return;
        }
        // Show loading spinner
        $("#nlSpinner").show();
        $.ajax({
            url: "http://10.2.0.4:8888/nl2sql",
            type: "POST",
            data: JSON.stringify({ query: naturalQuery }),
            contentType: "application/json",
            success: function(response){
                $("#sqlInput").val(response.sql);
            },
            error: function(xhr){
                alert("Natural language conversion failed: " + xhr.responseText);
            },
            complete: function(){
                // Hide loading spinner
                $("#nlSpinner").hide();
            }
        });
    });

    // SQL execute button click event
    $("#sqlExecute").click(function(){
        var sqlQuery = $("#sqlInput").val().trim();
        if(sqlQuery === ""){
            alert("SQL query cannot be empty");
            return;
        }
        // Show loading spinner
        $("#sqlSpinner").show();
        $.ajax({
            url: "http://10.2.0.4:8888/execute-sql",
            type: "POST",
            data: JSON.stringify({ query: sqlQuery }),
            contentType: "application/json",
            success: function(response){
                if(response.status === "success") {
                    if(Array.isArray(response.data)) {
                        // If array (query results), display as table
                        var table = '<table class="table table-striped"><thead><tr>';
                        if(response.data.length > 0) {
                            // Add table headers
                            Object.keys(response.data[0]).forEach(function(key) {
                                table += '<th>' + key + '</th>';
                            });
                            table += '</tr></thead><tbody>';
                            // Add data rows
                            response.data.forEach(function(row) {
                                table += '<tr>';
                                Object.values(row).forEach(function(value) {
                                    table += '<td>' + value + '</td>';
                                });
                                table += '</tr>';
                            });
                            table += '</tbody></table>';
                        } else {
                            table = '<div class="alert alert-info">No matching data found</div>';
                        }
                        $("#displayArea").html(table);
                    } else {
                        // If object (like affected rows count), display as JSON
                        $("#displayArea").html("<pre>" + JSON.stringify(response.data, null, 2) + "</pre>");
                    }
                } else {
                    $("#displayArea").html('<div class="alert alert-danger">Execution failed: ' + JSON.stringify(response) + '</div>');
                }
            },
            error: function(xhr){
                $("#displayArea").html('<div class="alert alert-danger">Error: ' + xhr.responseText + '</div>');
            },
            complete: function(){
                // Hide loading spinner
                $("#sqlSpinner").hide();
            }
        });
    });
});

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
            url: "http://10.2.0.4:8888/nl2mongo",
            type: "POST",
            data: JSON.stringify({ query: naturalQuery }),
            contentType: "application/json",
            success: function(response){
                $("#mongoInput").val(response.mongo);
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

    // MongoDB execute button click event
    $("#mongoExecute").click(function(){
        var mongoQuery = $("#mongoInput").val().trim();
        if(mongoQuery === ""){
            alert("MongoDB query cannot be empty");
            return;
        }
        // Show loading spinner
        $("#mongoSpinner").show();
        $.ajax({
            url: "http://10.2.0.4:8888/execute-mongodb",
            type: "POST",
            data: JSON.stringify({ query: mongoQuery }),
            contentType: "application/json",
            success: function(response){
                if(response.status === "success") {
                    $("#displayArea").html("<pre>" + JSON.stringify(response.data, null, 2) + "</pre>");
                } else {
                    $("#displayArea").html('<div class="alert alert-danger">Execution failed: ' + JSON.stringify(response) + '</div>');
                }
            },
            error: function(xhr){
                $("#displayArea").html('<div class="alert alert-danger">Error: ' + xhr.responseText + '</div>');
            },
            complete: function(){
        // Hide loading spinner
                $("#mongoSpinner").hide();
            }
        });
    });
});

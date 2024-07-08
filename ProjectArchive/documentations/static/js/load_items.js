$("#id_faculty").change(function () {
    const url = $("#documentationSearchForm").attr("data-departments-url");
    const facultyName = $(this).val();

    $.ajax({
        url: url,
        data: {
            'faculty_name': facultyName
        },
        success: function (data) {
            $("#id_department").html(data);
            $("#id_programme").html('');

            if ($("#id_department").val() === '') {
                $("#id_programme").html(''); // Clear the value of #id_programme if #id_department is empty
            } else {
                // Only make the AJAX call to update #id_programme if #id_department is not empty
                const next_url = $("#documentationSearchForm").attr("data-programmes-url");
                const departmentName = $("#id_department").val(); // Use the newly updated #id_department value

                $.ajax({
                    url: next_url,
                    data: {
                        'department_name': departmentName
                    },
                    success: function (data) {
                        $("#id_programme").html(data);
                    }
                });
            }
        }
    });
});


$("#id_faculty").change(function () {
    const url = $("#documentationSearchForm").attr("data-supervisors-url");
    const facultyName = $(this).val();

    $.ajax({
        url: url,
        data: {
            'faculty_name': facultyName
        },
        success: function (data) {
            $("#id_supervisor").html(data);
        }
    });
});


$("#id_department").change(function () {
    const next_url = $("#documentationSearchForm").attr("data-programmes-url");
    const departmentName = $("#id_department").val(); // Use the newly updated #id_department value

    $.ajax({
        url: next_url,
        data: {
            'department_name': departmentName
        },
        success: function (data) {
            $("#id_programme").html('');
            $("#id_programme").html(data);
        }
    });
});
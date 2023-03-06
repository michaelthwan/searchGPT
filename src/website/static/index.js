$(document).ready(function () {
    $('#search-btn').click(function (event) {
        event.preventDefault();
        let search_text = $('#form1').val();
        if (search_text.length === 0) {
            alert("Please input any search query. ");
            return
        }
        $.ajax({
            url: '/search',
            type: 'POST',
            data: {
                q: search_text,
                bing_search_subscription_key: $('#bing_search_subscription_key').val(),
                openai_api_key: $('#openai_api_key').val(),
                is_use_source: $('input[name="is_use_source"]').val(),
                llm_service_provider: $('#llm_service_provider').val(),
                llm_model: $('#llm_model').val(),
                semantic_search_provider: $('#semantic_search_provider').val()
            },
            success: function (response) {
                $('#' + response.id).html(response.html)
            },
            error: function (error) {
                console.log(error)
            }
        })
    })
})
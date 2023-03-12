$(document).ready(function () {
    let socket = io.connect();
    socket.on('search-step', function (message) {
        console.log("search-step: " + message)
    });

    $('form').submit(function (event) {
        event.preventDefault();
        let search_text = $('#form1').val();
        $('#search-btn')[0].disabled = true;
        $('#search-result-spinner').addClass('d-flex');
        $('#search-results').hide();
        $('#explain_results').hide();
        $.ajax({
            url: '/search',
            type: 'POST',
            data: {
                q: search_text,
                bing_search_subscription_key: $('#bing_search_subscription_key').val(),
                openai_api_key: $('#openai_api_key').val(),
                is_use_source: $('input[name="is_use_source"]')[0].checked,
                llm_service_provider: $('#llm_service_provider').val(),
                llm_model: $('#llm_model').val()
            },
            success: function (response) {
                $('#' + response.id).html(response.html)
                $('#explain_results').html(response.explain_html)
                $('#search-btn')[0].disabled = false;
                $('#search-result-spinner').removeClass('d-flex');
                $('#search-results').show();
                $('#explain_results').show();
            },
            error: function (error) {
                console.log(error)
                $('#explain_results').html(response.explain_html)
                $('#search-btn')[0].disabled = false;
                $('#search-result-spinner').removeClass('d-flex');
                $('#search-results').show();
                $('#explain_results').show();
            }
        })
    })
})
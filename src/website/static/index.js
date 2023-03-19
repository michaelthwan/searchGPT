$(document).ready(function () {
    let refresh_progress = function () {
        let status = $('#status').val()
        if (status === 'done' || status === 'error') {
            return;
        }
        $.get("/progress",
            {request_id: $('#request_id').val()},
            function (data, status) {
                if (status === 'success') {
                    $('#search-result-step').html(data.html);
                    $('#result-text')[0].innerText = data.openai_stream;
                }
            }
        );
    }

    $('form').submit(function (event) {
        event.preventDefault();

        let socket = io.connect();
        socket.on('search-step', function (message) {
            if (message) {
                console.log("search-step: " + message.msg);
                $('#search-result-step').html(message.html);
            } else {
            }
        });

        socket.on('openai-stream', function (message) {
            $('#result-text')[0].append(message.msg);
        });

        let search_text = $('#form1').val();

        $('#result-text')[0].innerHTML = '';
        $('#ref-links')[0].innerHTML = '';
        $('#search-query')[0].innerHTML = search_text;

        $('#search-btn')[0].disabled = true;
        $('#status').val('processing');
        $('#search-result-spinner').addClass('d-flex');
        $('#search_text')[0].innerText = search_text;
        $('#search_result_sources')[0].innerText = '';
        $('#explain_results').hide();
        $.ajax({
            url: '/search',
            type: 'POST',
            data: {
                q: search_text,
                request_id: $('#request_id').val(),
                bing_search_subscription_key: $('#bing_search_subscription_key').val(),
                openai_api_key: $('#openai_api_key').val(),
                is_use_source: $('input[name="is_use_source"]')[0].checked,
                llm_service_provider: $('#llm_service_provider').val(),
                llm_model: $('#llm_model').val()
            },
            success: function (response) {
                $('#' + response.id).html(response.html)
                $('#explain_results').html(response.explain_html)
                $('#request_id_status_html').html(response.request_id_status_html)
                $('#search-btn')[0].disabled = false;
                $('#search-result-spinner').removeClass('d-flex');
                $('#explain_results').show();

                socket.disconnect();
            },
            error: function (error) {
                console.log(error)
                $('#explain_results').html(response.explain_html)
                $('#request_id_status_html').html(response.request_id_status_html)
                $('#search-btn')[0].disabled = false;
                $('#search-result-spinner').removeClass('d-flex');
                $('#explain_results').show();

                socket.disconnect();
            }
        })

        // call 10 times progress each sec
        CALL_TIMES = 30; // 30 sec
        for (let i = 0; i < CALL_TIMES; i++) {
            setTimeout(refresh_progress, 1000 * i);
        }
    })
})
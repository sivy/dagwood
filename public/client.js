// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

function clickHandler(nodeid, node) {
    var yesNo = confirm("Add dependency for '" + node + "'?");
    if (yesNo) {
        $('#targetMenu').val(nodeid);
        $('#fromMenu').val("");
        $('#nodename').focus();
    }
}

$(function () {
    console.log('check your privilege :o');

    // $.get('/nodes', function (graph) {
    //     console.log(graph)
    //     graph.forEach(function (edge) {

    //         var text = edge[0].title + " -> " + edge[1].title
    //         $('<li></li>').text(text).appendTo('ul#nodes');
    //     });
    // });

    $('form').submit(function (event) {
        event.preventDefault();
        node = $('#nodename').val();
        target = $('#targetMenu').val();
        from = $('#fromMenu').val();
        class_ = $('#classMenu').val();
        console.log(node, target, from, class_)

        if (
            (node == '' && from == '') || target == ''
        ) {
            alert("Something went wrong");
            return
        }

        $.post('/graph?' + $.param({
            'node': node, 'target': target,
            'from': from, 'class': class_
        }), function () {
            $.get('/nodes.json', function (data) {
                console.log(data);
                $('#targetMenu').find('option').remove();

                $.each(data, function (nodeId, nodeData) {
                    $('<option></option>').text(nodeData.title).val(nodeData.id).appendTo('#targetMenu');
                });

                $('#fromMenu').find('option').remove();

                $.each(data, function (nodeId, nodeData) {
                    $('<option></option>').text(nodeData.title).val(nodeData.id).appendTo('#fromMenu');
                });
            });

            d = new Date();
            $("#graph").attr("data", "/graph.svg?" + d.getTime())
            $('input').val('');
            $('input').focus();
            $('#targetMenu').val(node);
            $('#classMenu').val("");
        });
    });

});

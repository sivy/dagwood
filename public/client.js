// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html

$(function () {
    console.log('check your privilege :o');

    $('form').submit(function (event) {
        event.preventDefault();
        node = $('input[name=name').val();
        target = $('select[name=target]').val();
        class_ = $('select[name=class]').val();
        $.post('/nodes?' + $.param({
            'node': node, 'target': target, 'class': class_
        }), function () {
            d = new Date();
            $("#graph").attr("src", "/graph.svg?" + d.getTime())
            $('input').val('');
            $('input').focus();
            $('select[name=target]').val(node);
            $('select[name=class]').val("");
        });
    });

});

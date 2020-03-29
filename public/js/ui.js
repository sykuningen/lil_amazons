$(() => {
    // Set up draggable windows
    let current_z_index = 10;

    interact('.draggable')
        .draggable({
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent',
                    endOnly: false
                })
            ],

            listeners: {
                move: dragMoveListener
            }
        })
        .on('tap', (event) => {
            event.target.style.zIndex = current_z_index;
            current_z_index += 1;
        });

    function dragMoveListener(event) {
        const target = event.target;
        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)';
        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);
    }

    window.dragMoveListener = dragMoveListener;

    // Toggle windows
    $('#navbar').on('click', 'a', (e) => {
        if (e.target.id != 'navbar-home') {
            const target = '#' + e.target.id.replace('navbar', 'window');

            if ($(target).is(':visible')) {
                $(target).hide();
            } else {
                $(target).show();
            }
        }
    });
});

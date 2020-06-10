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
        .resizable({
            edges: { left: true, right: true, bottom: true, top: true },

            listeners: {
                move(e) {
                    let x = (parseFloat(e.target.getAttribute('data-x')) || 0);
                    let y = (parseFloat(e.target.getAttribute('data-y')) || 0);

                    e.target.style.width  = e.rect.width  + 'px';
                    e.target.style.height = e.rect.height + 'px';

                    x += e.deltaRect.left;
                    y += e.deltaRect.top;

                    e.target.style.webkitTransform = e.target.style.transform = 'translate(' + x + 'px,' + y + 'px)';

                    e.target.setAttribute('data-x', x);
                    e.target.setAttribute('data-y', y);

                    e.currentTarget.style.zIndex = current_z_index;
                    current_z_index += 1;
                }
            },

            modifiers: [
                interact.modifiers.restrictEdges({
                    outer: 'parent'
                }),
                interact.modifiers.restrictSize({
                    min: { width: 200, height: 100 }
                })
            ],

            inertia: false
        })
        .on('tap', (e) => {
            e.currentTarget.style.zIndex = current_z_index;
            current_z_index += 1;
        })
        .styleCursor(false);

    function dragMoveListener(event) {
        const target = event.target;
        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)';
        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);

        event.currentTarget.style.zIndex = current_z_index;
        current_z_index += 1;
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

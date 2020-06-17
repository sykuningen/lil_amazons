$(() => {
    // Set up draggable windows
    let current_z_index = 10;
    let maximized       = null;

    interact('.draggable')
        .draggable({
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'html',
                    endOnly: false
                })
            ],

            listeners: {
                move: dragMoveListener
            },

            allowFrom: '.window-title'
        })
        .resizable({
            edges: { bottom: true, right: true },

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

                    maximized = null;

                    // Update board size
                    const size = Math.min($('#window-game').width(), $('#window-game').height());

                    window.app.renderer.resize(size, size);
                    window.renderBoard();
                }
            },

            modifiers: [
                interact.modifiers.restrictSize({
                    min: { width: 200, height: 200 }
                })
            ],

            inertia: false,
            allowFrom: '.window-dragbox'
        })
        .on('tap', (e) => {
            if (e.currentTarget != maximized) {
                e.currentTarget.style.zIndex = current_z_index;
                current_z_index += 1;
            }
        });

    function dragMoveListener(event) {
        const target = event.target;
        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)';
        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);

        if (event.currentTarget != maximized) {
            event.currentTarget.style.zIndex = current_z_index;
            current_z_index += 1;
        }
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

    $('#window-game').on('click', 'a', (e) => {
        $(e.delegateTarget).css({
            top:    '42px',
            bottom: 0,
            left:   0,
            right:  0 });

        $(e.delegateTarget).css('z-index', '0');
        maximized = e.delegateTarget;

        // Update board size
        const size = Math.min($('#window-game').width(), $('#window-game').height());

        window.app.renderer.resize(size, size);
        window.renderBoard();
    });
});

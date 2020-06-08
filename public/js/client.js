$(() => {
    const socket = io();

    socket.on('server_stats', (stats) => {
        if (stats.online_users) {
            $('#navbar-online-users').html(stats.online_users.toString() + ' user(s) online');
        }
    });

    // Lobby List
    socket.on('lobby_list', (lobbies) => {
        let html = '<table><tr class="header"><td><p>Lobby ID</p></td><td><p>Players</p></td><td></td></tr>';

        for (let i = 0; i < lobbies.length; i++) {
            html
                += '<tr><td><p>'
                + lobbies[i].id
                + '</p></td><td><p>'
                + lobbies[i].players
                + '</p></td><td><p>'
                + '<a href="#" id="' + lobbies[i].id.toString() + '">Join</a>'
                + '</p></td></tr>';
        }

        html += '</table>';
        $('#lobby-list').html(html);
    });

    $('#lobby-list').on('click', 'a', (e) => {
        socket.emit('join_lobby', e.target.id);
    });

    // Lobby Create
    $('#window-lobby-create').on('click', 'a', (e) => {
        if (e.target.id == 'btn-create-lobby') {
            socket.emit('create_lobby');
        } else if (e.target.id == 'btn-start-game') {
            socket.emit('start_game');
        }
    });

    socket.on('update_lobby', (lobby_info) => {
        $('#lobby-id').html('#' + lobby_info.id.toString());
        $('#lobby-players').html(lobby_info.players.join('\n'));

        $('#window-lobby-create').show();
    });

    socket.on('leave_lobby', () => {
        $('#window-lobby-create').hide();

        $('#lobby-id').html('none');
        $('#lobby-players').html('');
    });

    // Game
    socket.on('game_data', game_data => {
        $('#window-game').show();
        $('#game').html(app.view);
        renderBoard(game_data.board);
    });


    // *======================================================== PIXIJS
    const app = new PIXI.Application({
        width:  800,
        height: 600,
        antialias:   true,
        transparent: true });

    const board_offset = 20;
    const tile_size    = 50;

    const grp_board_grid = new PIXI.Graphics();
    grp_board_grid.lineStyle(1, 0xffffff, .25, 0);
    app.stage.addChild(grp_board_grid);


    function renderBoard(board) {
        let offset_x = 0;
        let offset_y = 0;

        for (let x = 0; x < board.width; x++) {
            for (let y = 0; y < board.height; y++) {
                grp_board_grid.drawRect(
                    x * tile_size + board_offset + offset_x,
                    y * tile_size + board_offset + offset_y,
                    tile_size,
                    tile_size );

                offset_y--;
            }

            offset_y = 0
            offset_x--;
        }
    }
});

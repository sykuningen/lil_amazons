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
    let current_board = null;

    socket.on('game_data', game_data => {
        $('#window-game').show();
        $('#game').html(app.view);

        current_board = game_data.board;
        selected      = { x: -1, y: -1 };

        renderBoard(current_board);
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
    app.stage.addChild(grp_board_grid);

    const player_colours    = [ 0x0080FF, 0x00FF80, 0xFF8000, 0x80FF00 ];
    const grp_player_pieces = [];

    for (let i = 0; i < 4; i++) {
        grp_player_pieces[i] = new PIXI.Graphics();
        app.stage.addChild(grp_player_pieces[i]);
    }

    let selected = { x: -1, y: -1 };


    function resetGraphics() {
        grp_board_grid.clear();
        grp_board_grid.lineStyle(1, 0x3B7080, 1, 0);

        for (let i = 0; i < 4; i++) {
            grp_player_pieces[i].clear();
            grp_player_pieces[i].lineStyle(2, player_colours[i], 1, 0);
        }
    }

    function renderBoard(board) {
        resetGraphics();

        // let offset_x = 0;
        // let offset_y = 0;

        for (let x = 0; x < board.width; x++) {
            for (let y = 0; y < board.height; y++) {
                if (x == selected.x && y == selected.y) {
                    grp_board_grid.beginFill(0x3B7080, .5);
                } else if (board.board[x][y] == -2) {
                    grp_board_grid.beginFill(0x3B7080, 1);
                }

                // const pos_x = x * tile_size + board_offset + offset_x;
                // const pos_y = y * tile_size + board_offset + offset_y;
                const pos_x = x * tile_size + board_offset;
                const pos_y = y * tile_size + board_offset;

                grp_board_grid.drawRect(pos_x, pos_y, tile_size, tile_size);
                // offset_y--;

                if ((x == selected.x && y == selected.y) || board.board[x][y] == -2) {
                    grp_board_grid.endFill();
                }

                // Is this tile occupied?
                if (board.board[x][y] >= 0) {
                    grp_player_pieces[board.board[x][y]].drawCircle(
                        pos_x + tile_size/2,
                        pos_y + tile_size/2,
                        tile_size/3 );
                }
            }

            // offset_y = 0
            // offset_x--;
        }
    }


    $('#game').on('click tap', (e) => {
        const x = e.originalEvent.layerX - board_offset;
        const y = e.originalEvent.layerY - board_offset;

        const tile_x = parseInt(x / tile_size);
        const tile_y = parseInt(y / tile_size);

        if (tile_x < 0 || tile_x >= current_board.width || tile_y < 0 || tile_y >= current_board.height) {
            return;
        }

        if (current_board.board[tile_x][tile_y] >= 0) {
            selected = { x: tile_x, y: tile_y };
            renderBoard(current_board);
        } else {
            socket.emit('attempt_move', selected, { x: tile_x, y: tile_y });
        }
    });
});

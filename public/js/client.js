$(() => {
    const socket = io();
    let my_sid = null;

    socket.on('sid', (sid) => {
        my_sid = sid;
    });

    socket.on('server_stats', (stats) => {
        if (stats.online_users) {
            $('#navbar-online-users').html(stats.online_users.toString() + ' user(s) online');
        }
    });

    // Logging
    $('#window-server-log').on('click', 'a', (e) => {
        if (e.target.id == 'btn-log-connect') {
            socket.emit('connect_log');
        }
    });

    socket.on('log_message', (data) => {
        $('#btn-log-connect').hide();
        $('#log-messages tr:nth-child(1)').after('<tr><td><p>' + data.sender + '</p></td><td><p>' + data.message + '</p></td></tr>');
    });

    // Lobby List
    socket.on('lobby_list', (lobbies) => {
        let html = '<table><tr class="header"><td><p>Lobby ID</p></td><td><p>Players</p></td><td></td></tr>';

        for (let i = 0; i < lobbies.length; i++) {
            html
                += '<tr><td><p>'
                + lobbies[i].id
                + '</p></td><td><p>'
                + lobbies[i].players.join('<br />')
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
        } else if (e.target.id == 'btn-ready-up') {
            socket.emit('join_players');
        } else if (e.target.id == 'btn-ready-leave') {
            socket.emit('leave_players');
        } else if (e.target.id == 'btn-start-game') {
            socket.emit('start_game');
        } else if (e.target.id == 'btn-watch-game') {
            socket.emit('watch_game');
        }
    });

    socket.on('update_lobby', (lobby_info) => {
        $('#lobby-id').html('#' + lobby_info.id.toString());
        $('#lobby-users').html(lobby_info.users.join('<br />'));
        $('#lobby-plyrs').html(lobby_info.players.join('<br />'));

        if (lobby_info.owner_sid == my_sid) {
            $('#start-game-p').show();
        }

        if (lobby_info.started) {
            $('#btn-ready-up').hide();
            $('#btn-ready-leave').hide();
        } else if (lobby_info.players.includes(my_sid)) {
            $('#btn-ready-up').hide();
            $('#btn-ready-leave').show();
        } else {
            $('#btn-ready-up').show();
            $('#btn-ready-leave').hide();
        }

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
    const width  = 600;
    const height = 600;

    const app = new PIXI.Application({
        width:  width,
        height: height,
        antialias:   true,
        transparent: true });

    const board_offset = 50;
    const tile_size    = (width - 100) / 10;

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
                } else if ((x + y) % 2 == 0) {
                    grp_board_grid.beginFill(0x000000, .2);
                }

                // const pos_x = x * tile_size + board_offset + offset_x;
                // const pos_y = y * tile_size + board_offset + offset_y;
                const pos_x = x * tile_size + board_offset;
                const pos_y = y * tile_size + board_offset;

                grp_board_grid.drawRect(pos_x-1, pos_y-1, tile_size+1, tile_size+1);
                // offset_y--;

                grp_board_grid.endFill();

                // Is this tile occupied?
                if (board.board[x][y] >= 0) {
                    grp_player_pieces[board.board[x][y]].drawCircle(
                        pos_x + tile_size/2,
                        pos_y + tile_size/2,
                        tile_size/4 );
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

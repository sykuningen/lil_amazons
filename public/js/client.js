$(() => {
    // *======================================================== CLIENT INIT
    const socket = io();
    let   my_sid = null;
    let   in_lob = false;

    socket.on('sid', (sid) => {
        my_sid = sid;
    });

    socket.on('server_stats', (stats) => {
        if (stats.online_users) {
            $('#navbar-online-users').html(stats.online_users.toString() + ' user(s) online');
        }
    });


    // *======================================================== LOGGING
    $('#window-server-log').on('click', 'a', (e) => {
        if (e.target.id == 'btn-log-connect') {
            $('#btn-log-connect').hide();
            socket.emit('connect_log');
        }
    });

    socket.on('log_message', (data) => {
        $('#log-messages tr:nth-child(1)').after('<tr><td><p>' + data.sender + '</p></td><td><p>' + data.message + '</p></td></tr>');
    });


    // *======================================================== LOGIN
    $('#btn-login').on('click', () => {
        socket.emit('login', { username: $('#login-username').val() });
    });

    socket.on('logged_in', () => {
        $('#window-login').hide();
        $('#window-lobby-list').show();
    });


    // *======================================================== LOBBY
    socket.on('lobby_list', (lobbies) => {
        let html = '<table><tr class="header"><td><p>Lobby ID</p></td><td><p>Players</p></td><td></td></tr>';

        for (let i = 0; i < lobbies.length; i++) {
            html
                += '<tr><td><p>'
                + lobbies[i].id
                + '</p></td><td><p>'
                + lobbies[i].player_usernames.join('<br />')
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
            if (in_lob) {
                socket.emit('leave_lobby');
            } else {
                socket.emit('create_lobby');
            }
        } else if (e.target.id == 'btn-ready-up') {
            socket.emit('join_players');
        } else if (e.target.id == 'btn-ready-leave') {
            socket.emit('leave_players');
        } else if (e.target.id == 'btn-add-ai') {
            socket.emit('add_ai_player');
        } else if (e.target.id == 'toggle-game-config') {
            if ($('#lobby-game-config').is(':visible')) {
                $('#lobby-game-config').hide();
            } else {
                $('#lobby-game-config').show();
            }
        } else if (e.target.id == 'btn-start-game') {
            $('#start-game-p').hide();
            socket.emit('start_game', $('#lobby-game-config').val());
        } else if (e.target.id == 'btn-watch-game') {
            socket.emit('watch_game');
        }
    });

    socket.on('update_lobby', (lobby_info) => {
        in_lob = true;

        $('#btn-create-lobby').html('Leave Lobby');

        $('#lobby-id').html('#' + lobby_info.id.toString());
        $('#lobby-users').html(lobby_info.user_usernames.join('<br />'));
        $('#lobby-plyrs').html(lobby_info.player_usernames.join('<br />'));

        if (lobby_info.started) {
            $('.lobby-options').hide();
            $('#btn-ready-up').hide();
            $('#btn-ready-leave').hide();
            $('#btn-add-ai').hide();

            $('#watch-game-p').show();
        } else {
            $('.lobby-options').show();

            if (lobby_info.owner_sid == my_sid) {
                $('#start-game-p').show();
            } else {
                $('#start-game-p').hide();
            }

            $('#watch-game-p').hide();

            if (lobby_info.players.includes(my_sid)) {
                $('#btn-ready-up').hide();
                $('#btn-ready-leave').show();
            } else {
                $('#btn-ready-up').show();
                $('#btn-ready-leave').hide();
            }

            $('#btn-add-ai').show();
        }

        $('#lobby-info').show();
        $('#window-lobby-create').show();
    });

    socket.on('leave_lobby', () => {
        in_lob = false;

        $('#window-lobby-create').hide();
        $('#lobby-info').hide();

        $('#btn-create-lobby').html('Create Lobby');

        $('.lobby-options').hide();
        $('#lobby-id').html('none');
        $('#lobby-users').html('');
        $('#lobby-plyrs').html('');

        $('#btn-ready-up').hide();
        $('#btn-ready-leave').hide();
        $('#start-game-p').hide();

        $('#window-game').hide();
        $('#window-game-info').hide();
    });


    // *======================================================== GAME
    const player_colours     = [ 0x00C0FF,  0x00FF80,  0xC080FF,  0xFF8030 ];
    const player_colours_hex = [ '#00C0FF', '#00FF80', '#C080FF', '#FF8030' ];

    let current_board = null;
    let selected      = { x: -1, y: -1 };

    socket.on('game_data', (game_data) => {
        current_board = game_data.board;
        renderBoard(current_board);

        $('#window-game').show();

        // Game info
        $('#window-game-info').show();
        $('#game-info-id').html('Game#' + game_data.id.toString());

        if (game_data.ended) {
            const colour = player_colours_hex[game_data.winner];
            const text   = "<span style='font-weight:bold;color:" + colour + "'>" + game_data.lobby.player_usernames[game_data.winner] + "</span> wins!";
            $('#game-info-turn').html(text);

            $('#game-info-burning').html('');
        }
        else {
            const turn_colour = player_colours_hex[game_data.current_player];
            const turn_string = "<span style='font-weight:bold;color:" + turn_colour + "'>" + game_data.lobby.player_usernames[game_data.current_player] + "</span>'s turn";
            $('#game-info-turn').html(turn_string);

            if (game_data.burning) {
                $('#game-info-burning').html('Select a tile to burn');
            } else {
                $('#game-info-burning').html('Move a piece');
            }
        }

        // Score info
        let score_text = '';

        for (let i in game_data.scores) {
            const colour = player_colours_hex[parseInt(i)];
            score_text += "<span style='font-weight:bold;color:" + colour + "'>" + game_data.scores[i].toString() + ' - ' + game_data.lobby.player_usernames[parseInt(i)] + '</span><br />';
        }

        $('#game-info-scores').html(score_text);

        // Region info
        let region_text = '';

        for (let i in game_data.regions) {
            region_text += i.toString() + ') ';
            region_text += game_data.regions[i].tiles.length.toString() + ' tiles';

            if (game_data.regions[i].owner != null) {
                region_text += ' - owned by ' + game_data.lobby.player_usernames[game_data.regions[i].owner];
            }

            region_text += '<br />';
        }

        $('#game-info-regions').html(region_text);
    });

    socket.on('select_piece', (piece) => {
        selected = piece;
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

    $('#game').html(app.view);

    // Board graphical setup
    const board_offset = 50;
    const tile_size    = (width - 100) / 10;

    // PIXIJS graphics setup
    const grp_board_grid = new PIXI.Graphics();
    app.stage.addChild(grp_board_grid);

    const grp_valid_move_marker = new PIXI.Graphics();
    app.stage.addChild(grp_valid_move_marker);

    const grp_player_pieces = [];
    for (let i = 0; i < 4; i++) {
        grp_player_pieces[i] = new PIXI.Graphics();
        app.stage.addChild(grp_player_pieces[i]);
    }


    function resetGraphics() {
        grp_board_grid.clear();
        grp_board_grid.lineStyle(1, 0x303030, 1, 0);

        grp_valid_move_marker.clear();
        grp_valid_move_marker.lineStyle(1, 0xFFFFFF, 1, 0);

        for (let i = 0; i < 4; i++) {
            grp_player_pieces[i].clear();
            grp_player_pieces[i].lineStyle(2, player_colours[i], 1, 0);
        }
    }

    function renderBoard(board) {
        resetGraphics();

        for (let x = 0; x < board.width; x++) {
            for (let y = 0; y < board.height; y++) {

                if (board.board[x][y] == -2) {
                    // Fill in tile to show that it has been burned
                    grp_board_grid.beginFill(0xC0C0C0, 1);
                }
                else if (board.board[x][y] >= 0) {
                    let alpha = .1;
                    if (x == selected.x && y == selected.y) {
                        alpha = .5;
                    }
                    grp_board_grid.beginFill(player_colours[board.board[x][y]], alpha);
                }
                else if ((x + y) % 2 == 0) {
                    // Fill in tiles with a minimal checkerboard pattern
                    grp_board_grid.beginFill(0x000000, .2);
                }

                // Determine tile position
                const pos_x = x * tile_size + board_offset;
                const pos_y = y * tile_size + board_offset;

                // Draw tile
                grp_board_grid.drawRect(pos_x-1, pos_y-1, tile_size+1, tile_size+1);
                grp_board_grid.endFill();

                // Draw any pieces on the tile
                if (board.board[x][y] >= 0) {
                    grp_player_pieces[board.board[x][y]].drawCircle(
                        pos_x + tile_size/2,
                        pos_y + tile_size/2,
                        tile_size/4 );
                }

                // Highlight tiles that are a valid move
                if (selected.x != -1 && validMove(board, selected, { x: x, y: y })) {
                    grp_valid_move_marker.drawCircle(
                        pos_x + tile_size/2,
                        pos_y + tile_size/2,
                        tile_size/16 );
                }
            }
        }
    }


    // *======================================================== GAME INTERACTION
    $('#game').on('click', (e) => {
        const x = e.offsetX - board_offset;
        const y = e.offsetY - board_offset;

        const tile_x = parseInt(x / tile_size);
        const tile_y = parseInt(y / tile_size);

        if (tile_x < 0 || tile_x >= current_board.width || tile_y < 0 || tile_y >= current_board.height) {
            return;
        }

        if (current_board.board[tile_x][tile_y] >= 0) {
            if (tile_x == selected.x && tile_y == selected.y) {
                // Deselected a piece
                selected = { x: -1, y: -1 };
            } else {
                // Selected a piece
                selected = { x: tile_x, y: tile_y };
            }

            renderBoard(current_board);
        } else {
            // Selected a tile to move to or to burn
            socket.emit('attempt_move', selected, { x: tile_x, y: tile_y });
        }
    });

    function validMove(board, piece, to) {
        // Trying to move to the same tile?
        if (piece.x == to.x && piece.y == to.y) {
            return false;
        }

        // Trying to move vertically?
        else if (piece.x == to.x) {
            let bgn = Math.min(piece.y, to.y);
            let end = Math.max(piece.y, to.y);

            if (piece.y < to.y) {
                bgn += 1;
                end += 1;
            }

            for (let t = bgn; t < end; t++) {
                if (board.board[piece.x][t] != -1) {
                    return false;
                }
            }

            return true;
        }

        // Trying to move horizontally?
        else if (piece.y == to.y) {
            let bgn = Math.min(piece.x, to.x);
            let end = Math.max(piece.x, to.x);

            if (piece.x < to.x) {
                bgn += 1;
                end += 1;
            }

            for (let t = bgn; t < end; t++) {
                if (board.board[t][piece.y] != -1) {
                    return false;
                }
            }

            return true;
        }

        // Trying to move diagonally?
        else if (Math.abs(piece.x - to.x) == Math.abs(piece.y - to.y)) {
            let change_x = -1;
            let change_y = -1;

            if (piece.x < to.x) {
                change_x = 1;
            }
            if (piece.y < to.y) {
                change_y = 1;
            }

            let x = piece.x;
            let y = piece.y;

            while (true) {
                x += change_x;
                y += change_y;

                if (board.board[x][y] != -1) {
                    return false;
                }

                if (x == to.x) {
                    return true;
                }
            }
        }

        return false;
    }
});

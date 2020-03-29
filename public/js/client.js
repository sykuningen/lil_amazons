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
                + '<a href="#">Join</a>'
                + '</p></td></tr>';
        }

        html += '</table>';
        $('#lobby-list').html(html);
    });

    // Lobby Create
    $('#window-lobby-create').on('click', 'a', (e) => {
        if (e.target.id == 'btn-create-lobby') {
            socket.emit('create_lobby');
        }
    });

    socket.on('join_lobby', (lobby_info) => {
        $('#lobby-id').html('#' + lobby_info.id.toString());
        $('#lobby-players').html(lobby_info.players);
    });
});

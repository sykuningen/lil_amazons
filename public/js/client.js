const socket = io();

$(() => {
    socket.on('server_stats', (stats) => {
        if (stats.online_users) {
            $('#navbar-online-users').html(stats.online_users.toString() + ' user(s) online');
        }
    });
});

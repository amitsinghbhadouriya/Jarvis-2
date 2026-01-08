$(document).ready(function () {
    $('.text').textillate({
        loop: true,
        speed: 1500, 
        sync: true,
        in: {
            effect:"bounceIn",
        },
        out: {
            effect:"bounceOut",
        }
    })
});
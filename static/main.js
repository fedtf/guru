$(function() {
    $('.dropable').sortable({
        connectWith: ".dropable",
        revert: true,
        cursor: 'move',
        activeClass: "ui-state-hover",
        receive: function(event, ui){
            console.log(event);
        }
    });
});
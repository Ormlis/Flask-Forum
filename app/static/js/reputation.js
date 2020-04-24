function like(btn_id, comment_id = 0, by_user_id = 0) {
    change_reputation(comment_id, by_user_id, 1);
    $("#" + (Number(btn_id) + 1)).attr('style', 'background-color: rgba(0, 0, 0, 0)')
    $("#" + btn_id).attr('style', 'background-color: green')
}

function dislike(btn_id, comment_id = 0, by_user_id = 0) {
    change_reputation(comment_id, by_user_id, -1)
    $("#" + (Number(btn_id) - 1)).attr('style', 'background-color: rgba(0, 0, 0, 0)')
    $("#" + btn_id).attr('style', 'background-color: red')
}

function change_reputation(comment_id, by_user_id, change = 0) {
    $.ajax({
        url: '/api/comment/' + comment_id,
        type: 'PUT',
        data: {
            by_user: by_user_id,
            reputation: change
        }
    })
}
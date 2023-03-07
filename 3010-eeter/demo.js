function delBtn(post) {
    const btn = document.createElement('button')
    btn.innerText = 'X'
    if (post['author'] === user()) btn.style.color =  'red'
    btn.onclick = function() {
        runForAuthor(post['author'], toDelPost())
    }
    return btn

    function toDelPost() {
        return () => {
            const req = new XMLHttpRequest()
            req.open('DELETE', `http://localhost:3000/tweets/${post['id']}`)
            req.setRequestHeader('Content-Type', 'application/json')
            req.onload = function () {
                renderPosts()
            }
            req.send()
        }
    }
}
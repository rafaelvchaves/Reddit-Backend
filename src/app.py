import json
from flask import Flask, request

app = Flask(__name__)

post_id_counter = 0
comment_id_counter = 0
posts = {}


def exclude_comments(posts_d):
    posts_no_comments = {}
    for p_id in posts_d:
        post = posts_d[p_id]
        posts_no_comments[p_id] = {k: post[k] for k in post if k != 'comments'}
    return posts_no_comments


def sort_posts(posts_d, sortby):
    decr = sortby == "decreasing"
    sorted_d = sorted(posts_d.values(), key=lambda x: x['upvotes'], reverse=decr)
    return {i: sorted_d[i] for i in range(0, len(sorted_d))}

@app.route('/api/posts/')
def get_all_posts():
    new_posts = exclude_comments(posts)
    sort = request.args.get('sort')
    new_posts = sort_posts(new_posts, sort)
    res = {'success': True, 'data': list(new_posts.values())}
    return json.dumps(res), 200


@app.route('/api/posts/', methods=['POST'])
def create_post():
    global post_id_counter
    post_body = json.loads(request.data)
    title = post_body['title']
    link = post_body['link']
    username = post_body['username']
    post = {
        'id': post_id_counter,
        'upvotes': 1,
        'title': title,
        'link': link,
        'username': username,
        'comments': {}
    }
    posts[post_id_counter] = post
    post_id_counter += 1
    return json.dumps({'success': True, 'data': post}), 201


@app.route('/api/post/<int:post_id>/')
def get_post(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    return json.dumps({'success': True, 'data': post}), 200


@app.route('/api/post/<int:post_id>/', methods=['DELETE'])
def delete_post(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    del posts[post_id]
    return json.dumps({'success': True, 'data': post}), 200


@app.route('/api/post/<int:post_id>/comments/')
def get_comments(post_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    res = {'success': True, 'data': list(post['comments'].values())}
    return json.dumps(res), 200


@app.route('/api/post/<int:post_id>/comment/', methods=['POST'])
def post_comment(post_id):
    global comment_id_counter
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    comment_body = json.loads(request.data)
    text = comment_body['text']
    username = comment_body['username']
    comment = {
        'id': comment_id_counter,
        'upvotes': 1,
        'text': text,
        'username': username
    }
    post['comments'][comment_id_counter] = comment
    comment_id_counter += 1
    return json.dumps({'success': True, 'data': comment}), 201


@app.route('/api/post/<int:post_id>/comment/<int:comment_id>/', methods=['POST'])
def edit_comment(post_id, comment_id):
    post = posts.get(post_id, None)
    if not post:
        return json.dumps({'success': False, 'error': 'Post not found'}), 404
    comment = post['comments'][comment_id]
    if not comment:
        return json.dumps({'success': False, 'error': 'Comment not found'}), 404
    post_body = json.loads(request.data)
    comment['text'] = post_body['text']
    return json.dumps({'success': True, 'data': comment}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

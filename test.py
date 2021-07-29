from flask import json

@app.route('/summary')
def summary():
    data = make_summary()
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/_get_current_user')
def get_current_user():
    return jsonify(
        username=g.user.username,
        email=g.user.email,
        id=g.user.id
    )
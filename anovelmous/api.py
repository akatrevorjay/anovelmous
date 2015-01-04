from anovelmous import app, db, VERSION
from flask import request, jsonify, g
import flask_restless
from models import NovelToken, Novel, Vote, Token, Chapter, FormattedNovelToken
import utils


def get_many_tokens_postprocessor(result=None, search_params=None, **kwargs):
    """Accepts two arguments, `result`, which is the dictionary
    representation of the JSON response which will be returned to the
    client, and `search_params`, which is a dictionary containing the
    search parameters for the request (that produced the specified
    `result`).

    """
    if search_params.get('grammatically_correct'):
        del result['objects']
        result['total_pages'] = 1

        tokens = g.grammar_filter.get_grammatically_correct_vocabulary_subset()
        result['num_results'] = len(tokens)

        if search_params.get('bit_stream'):
            utils.substitute_bit_stream(result, tokens)
        else:
            result['objects'] = [{'id': token.id, 'content': token.content} for token in tokens]


manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(Novel, methods=['GET', 'POST'])
manager.create_api(Chapter, methods=['GET', 'POST'], exclude_columns=['content'])
manager.create_api(Vote, methods=['GET', 'POST'])
manager.create_api(Token, methods=['GET', 'POST'], exclude_columns=['created_at', 'index'],
                   postprocessors={'GET_MANY': [get_many_tokens_postprocessor]})
manager.create_api(NovelToken, methods=['GET', 'POST'], allow_functions=True)
manager.create_api(FormattedNovelToken, methods=['GET', 'POST'])


@app.route('/api/bulk-add-to-vocabulary', methods=['POST'])
def add_to_vocabulary():
    words = request.json['words']
    words = [word.lower() for word in words]

    if len(set(words)) != len(words):
        return jsonify({'message': "All words must be unique."})

    for word in words:
        token = Token(word)
        db.session.add(token)

    db.session.commit()
    return jsonify({'message': "All words added successfully."})


@app.route('/api/metadata')
def get_api_metadata():
    return jsonify({'version': VERSION})
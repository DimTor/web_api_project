import flask

from . import db_session
from .artist import Artist

blueprint = flask.Blueprint(
    'artists_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/artists')
def get_artists():
    db_sess = db_session.create_session()
    artists = db_sess.query(Artist).all()
    return flask.jsonify(
        {
            'artists':
                [item.to_dict(only=('id', 'name'))
                 for item in artists]
        }
    )


@blueprint.route('/api/artists/<int:artist_id>', methods=['GET'])
def get_one_news(artist_id):
    db_sess = db_session.create_session()
    artist = db_sess.query(Artist).get(artist_id)
    if not artist:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'artists': artist.to_dict(only=('id', 'name'))
        }
    )


from app.redisDB import red
from app import creat_app, db
from app.models import User,Post,Comment,Follow,PostLike,Collection,to_dict
import json
import datetime

app = creat_app()
app.app_context().push()


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


def read_hot_postlist():
    hot_postlist = db.session.query(Post).order_by(Post.reading_num.desc()).all()[:10]
    for i in hot_postlist:
        red.zadd('hot_postlist', {json.dumps(to_dict(i), cls=DateEncoder): i.reading_num})

def read_time_postlist():
    time_postlist = db.session.query(Post).order_by(Post.create_time.desc()).all()[:10]
    for i in time_postlist:
        red.zadd('time_postlist', {json.dumps(to_dict(i), cls=DateEncoder): i.post_id})


if __name__ == '__main__':
    read_hot_postlist()
    read_time_postlist()


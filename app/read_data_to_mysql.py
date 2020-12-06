from app.redisDB import red
from app import creat_app, db
from app.models import User,Post,Comment,Follow,PostLike,Collection,to_dict
import json
import datetime
import traceback

app = creat_app()
app.app_context().push()


def redis_post_like_to_mysql():
    key_value = red.hgetall('postlike')
    for k,v in key_value.items():
        author_id = int(k.split('_')[0])
        post_id = int(k.split('_')[1])
        create_time = v
        post_like = PostLike(author_id=author_id,post_id=post_id,create_time=create_time)
        db.session.add(post_like)
    try:
        db.session.commit()
        for i in key_value:
            red.hdel('postlike',i)
    except:
        traceback.print_exc()
        db.session.rollback()



if __name__ == '__main__':
    redis_post_like_to_mysql()
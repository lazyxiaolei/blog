create table user
     (user_id  int  auto_increment,
     email   varchar(50)  not null  unique ,
     username  varchar(20)  not null  unique ,
     password_hash varchar(128) not null ,
     primary key (user_id),
     )engine=InnoDB  default charset=utf8;

create table posts(
    post_id  int   auto_increment,
    author_id  int  not null ,
    title  varchar(100)  not null ,
    content  text  ,
    create_time  datetime not null  default current_timestamp,
    update_time  datetime  not null default current_timestamp on update current_timestamp,
    primary key (post_id),
    foreign key (author_id) references user(user_id)
)engine = InnoDB  default charset =utf8


create table comment(
    comment_id  int   auto_increment,
    author_id  int  not null ,
    post_id  int  not null ,
    content  varchar(500)  not null ,
    create_time  datetime not null  default current_timestamp,
    primary key (comment_id),
    foreign key (author_id) references user(user_id),
    foreign key (post_id) references posts(post_id)
)engine = InnoDB  default charset =utf8

create index user_email_index on user(email);
create index user_username_index on user(username);
create index posts_title_index on posts(title);
create index posts_create_time_index on posts(create_time);
alter table posts add label varchar(20)  default '';
alter table comment add root_comment_id  int not null default -1;
alter table comment add to_comment_id int not null default -1;


create  table follow(
    follower_id  int   not null ,
    followed_id  int   not null ,
    follow_time datetime  not null  default current_timestamp,
    primary key  (follower_id,followed_id),
    foreign key  (follower_id)  references user(user_id),
    foreign key  (followed_id)  references user(user_id)
)engine = InnoDB  default charset =utf8

alter table posts add reading_num int not null  default  0;

create table postlike(
    author_id  int  not null ,
    post_id  int  not null ,
    like_status  int  not null  default 0,
    create_time  datetime  not null  default  current_timestamp,
    primary key (author_id,post_id),
    foreign key (author_id) references user(user_id),
    foreign key (post_id) references  posts(post_id)
)engine = InnoDB  default charset =utf8

alter table postlike drop column like_status;
alter table user add photo varchar(128)  not null default '';
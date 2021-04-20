CREATE DATABASE HotMusic;	-- 创建数据库
use HotMusic;

-- 删除表
-- DROP TABLE IF EXISTS gedan;
-- DROP TABLE IF EXISTS song;
-- DROP TABLE IF EXISTS song_cmt;

CREATE TABLE gedan(		-- 创建歌单信息表
	id VARCHAR(20) PRIMARY KEY COMMENT '歌单id',	-- 主键
	title_gedan varchar(100) COMMENT '歌单名',
	creater varchar(100) COMMENT '创建者',
	tags VARCHAR(100) COMMENT '标签',
	link varchar(100) COMMENT '歌单链接',
	count_songs INT COMMENT '歌曲数量'
);


CREATE table song(		-- 创建歌曲信息表
	id VARCHAR(20) COMMENT '歌曲id',	-- 主键
	name_song VARCHAR(100) COMMENT '歌曲名',
	id_gedan VARCHAR(20) COMMENT '歌单id',	
	singer VARCHAR(20) COMMENT '歌手',
	PRIMARY KEY(id, id_gedan)
);


CREATE TABLE song_cmt(		-- 创建歌曲评论表
	xh INT COMMENT '评论序号',	 
	id_cmt VARCHAR(20) PRIMARY KEY COMMENT '评论id',	-- 主键
	id_song VARCHAR(20) COMMENT '歌曲id',
	song_cmt VARCHAR(1000) CHARACTER set utf8 COMMENT '歌曲评论'
);



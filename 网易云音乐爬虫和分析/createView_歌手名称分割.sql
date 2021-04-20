-- 创建歌手分割视图
CREATE or replace VIEW v_songSinger as 
SELECT b.singer1,
			 b.singer2,
			 trim(replace(replace(REPLACE(b.singer,singer1,''),singer2,''),'/','')) singer3,
			 b.singer,
			 id,
			 id_gedan
FROM (
	SELECT a.singer1,
				 trim(SUBSTRING_INDEX(substr(replace(a.singer,singer1,'') FROM 3),'/',1)) singer2,
				 singer,
				 id,
				 id_gedan
	FROM (
		SELECT trim(SUBSTRING_INDEX(trim(singer),'/',1)) singer1, singer, id, id_gedan
		FROM song)a) b;
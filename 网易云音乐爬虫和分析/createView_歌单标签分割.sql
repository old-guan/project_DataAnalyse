-- 创建歌单标签分割视图
CREATE or replace VIEW v_gedanTags as 
SELECT b.tag1,
			 b.tag2,
			 SUBSTRING_INDEX(trim(replace(replace(b.tags,b.tag1,''),b.tag2,'')),' ',1) tag3,
			 tags,
			 id
FROM (
	SELECT a.tag1,
				 SUBSTRING_INDEX(trim(replace(a.tags,a.tag1,'')),' ',1) tag2,
				 tags,
				 id
	FROM (
		SELECT SUBSTRING_INDEX(trim(tags),' ',1) tag1, tags, id
		FROM gedan)a) b;
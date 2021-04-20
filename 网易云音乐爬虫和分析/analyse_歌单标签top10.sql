-- 按歌单标签汇总，分析top10标签
SELECT tag,
			 count(id) 计数
FROM (
	SELECT id,
				 tag1 tag
	FROM v_gedanTags

	UNION ALL

	SELECT id,
				 tag2
	FROM v_gedanTags
	WHERE tag2 <> ''

	UNION ALL

	SELECT id,
				 tag3
	FROM v_gedanTags
	WHERE tag3 <> '')a 
GROUP BY tag
ORDER BY 2 DESC
LIMIT 10;




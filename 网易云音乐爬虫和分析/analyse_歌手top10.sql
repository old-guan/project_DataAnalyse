-- 按歌手汇总，分析被收录top10歌手
SELECT singer,
			 count(id) 计数
FROM (
	SELECT id,
				 singer1 singer
	FROM v_songSinger

	UNION ALL

	SELECT id,
				 singer2
	FROM v_songSinger
	WHERE singer2 <> ''

	UNION ALL

	SELECT id,
				 singer3
	FROM v_songSinger
	WHERE singer3 <> '')a 
GROUP BY singer
ORDER BY 2 DESC
LIMIT 10;




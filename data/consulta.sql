-- Obtener todas las citas de un autor específico
SELECT quote_text 
FROM quotes 
WHERE author = ?;

-- Contar cuántas citas hay por etiqueta

SELECT 
    tags.tag_name,
    COUNT(quote_tags.quote_id) AS total_citas
FROM tags
LEFT JOIN quote_tags ON tags.id = quote_tags.tag_id
GROUP BY tags.tag_name;


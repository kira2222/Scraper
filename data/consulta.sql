-- Obtener todas las citas de un autor específico
SELECT quote_text 
FROM quotes 
WHERE author = ?;

-- Contar cuántas citas hay por etiqueta
SELECT 
    t.tag_name AS etiqueta,
    COUNT(q.id) AS total_citas
FROM tags t
LEFT JOIN quote_tags qt ON t.id = qt.tag_id
LEFT JOIN quotes q ON qt.quote_id = q.id
GROUP BY t.tag_name;

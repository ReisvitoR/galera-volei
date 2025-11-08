import sqlite3

conn = sqlite3.connect('galera_volei.db')
cursor = conn.cursor()

# Verificar se coluna existe
cursor.execute('PRAGMA table_info(partidas)')
colunas = [col[1] for col in cursor.fetchall()]
print('Colunas atuais:', colunas)

if 'categoria' not in colunas:
    print('Adicionando coluna categoria...')
    cursor.execute('ALTER TABLE partidas ADD COLUMN categoria VARCHAR(20) DEFAULT "livre"')
    conn.commit()
    print('✅ Coluna categoria adicionada!')
else:
    print('✅ Coluna categoria já existe!')

# Verificar novamente
cursor.execute('PRAGMA table_info(partidas)')
colunas_final = [col[1] for col in cursor.fetchall()]
print('Colunas finais:', colunas_final)

conn.close()